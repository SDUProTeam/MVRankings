import numpy as np
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
import pandas as pd
import pickle
import os
from recsys.model.utils import sort_padded, pad
from .recommender import Recommender


class KVMN(nn.Module):
    def __init__(self, layers, n_items, n_r,
                 batch_size=50, dropout_p_hidden=0.5, dropout_p_embed=0.0,
                 learning_rate=0.05, momentum=0.0, lmbd=0.0, embedding=0, KBembedding=0,
                 n_sample=0, sample_alpha=0.75, smoothing=0, decay=0.9, grad_cap=0, sigma=0,
                 init_as_normal=False, reset_after_session=True, train_random_order=False,
                 time_sort=False, out_dim=64, MN_nfactors=10, MN_dims=64):

        super(KVMN, self).__init__()
        self.n_items = n_items
        self.n_r = n_r
        self.layers = layers
        self.batch_size = batch_size
        self.dropout_p_hidden = nn.Dropout(dropout_p_hidden)
        self.dropout_p_embed = nn.Dropout(dropout_p_embed)
        self.learning_rate = learning_rate
        self.decay = decay
        self.momentum = momentum
        self.sigma = sigma
        self.init_as_normal = init_as_normal
        self.reset_after_session = reset_after_session
        self.grad_cap = grad_cap
        self.train_random_order = train_random_order
        self.lmbd = lmbd
        self.embedding = embedding
        self.time_sort = time_sort
        # self.final_act = final_act
        self.loss = nn.NLLLoss
        self.hidden_activation = torch.tanh
        self.n_sample = n_sample
        self.sample_alpha = sample_alpha
        self.smoothing = smoothing
        ## add memory network info
        self.KBembedding = KBembedding
        self.MN_nfactors = MN_nfactors
        self.MN_dims = KBembedding  # MN_dims
        self.out_dim = out_dim
        ## parameters for read operator
        self.MN_u = nn.Linear(self.layers[-1], self.MN_dims)
        self.MN_u2 = nn.Linear((self.MN_dims + self.layers[-1]), self.layers[-1])
        ## parameters for write operator
        self.MN_ea = nn.Linear(self.KBembedding, self.MN_dims)

        self.gru = nn.GRUCell(self.embedding, self.layers[0])
        self.gru2 = nn.GRUCell(self.out_dim, self.out_dim)

        self.mlp1 = nn.Linear(self.layers[-1], self.out_dim)

        use_cuda = torch.cuda.is_available()
        if use_cuda:
            torch.cuda.manual_seed(666)
        else:
            torch.manual_seed(666)
        self.device = torch.device("cuda" if use_cuda else "cpu")

        self.E = nn.Parameter(torch.randn((self.n_items, self.embedding), dtype=torch.float32))  # shape : self.init_weights((self.n_items, self.embedding))
        self.KBE = nn.Parameter(torch.randn((self.n_items, self.KBembedding), dtype=torch.float32))

        # with open('ItemE', 'wb') as f0, open('KBE', 'wb') as f1:
        #     pickle.dump(ItemE, f0)
        #     pickle.dump(ItemKBE, f1)

        # self.MergeE = nn.Parameter(torch.tensor(np.hstack([ItemE, ItemKBE])))
        ### add memory network
        self.r_matrix = nn.Parameter(torch.randn((self.n_r, self.KBembedding), dtype=torch.float32))
        self.mlp2 = nn.Linear(self.KBE.shape[1] + self.E.shape[1], self.out_dim)
        # self.mlp2 = nn.Linear(self.out_dim, self.n_items)

        self.constant_ones = torch.ones((self.MN_dims,), device=self.device)

        self.to(self.device)


    def model_step(self, y, X, hp, MN):
        h = self.gru(y, hp)
        h = self.dropout_p_hidden(h)
        y = h
        ### add memory network part
        ## write operator
        mask = torch.ones_like(self.KBE, device=self.device)
        mask[0] = 0
        KBItem = (self.KBE * mask)[X]  # shape:b*KBembedding
        EA = self.hidden_activation(self.MN_ea(KBItem))  # shape:b*d
        EA = EA.unsqueeze(1).repeat(1, self.MN_nfactors, 1) + self.r_matrix  # shape:b*k*d
        MN_gate = torch.sigmoid(torch.matmul(MN * EA, self.constant_ones.unsqueeze(1)))
        # MN_gate = MN_gate.unsqueeze(2)  # shape:dot(b*k*d, d*1) = b*k*1
        MN = MN * (1 - MN_gate) + EA * MN_gate  # shape:b*k*d
        ## read operator
        U_trans = self.hidden_activation(self.MN_u(y))  # We need to make the same dimension. (shape:b*d)
        MN_AW = F.softmax(torch.matmul(U_trans, self.r_matrix.transpose(1, 0)), dim=1)  # shape:b*k
        MN_AC = torch.matmul(MN.transpose(2, 1), MN_AW.unsqueeze(2))  # shape: b*d*1
        Ut = torch.cat((y, MN_AC[:, :, 0]), -1)  # shape:b*(dim+d)
        Ut = self.hidden_activation(self.MN_u2(Ut))  # shape : b*layers[-1]
        # H_new[-1] = Ut #self.dropout(Ut, drop_p_hidden)
        # add Dense layer
        y = self.hidden_activation(self.mlp1(Ut)) # b*out_dim
        return y, h, MN

    def forward(self, X, predict=False):
        MN = torch.zeros((X.shape[0], self.MN_nfactors, self.MN_dims), device=self.device)
        # self.E[0] = 0
        mask = torch.ones_like(self.E, device=self.device)
        mask[0] = 0
        Sx = (self.E * mask)[X]  # b*l*d
        h = None
        h2 = None
        y_sum = 0
        for t in range(0, X.shape[1]):
            y, h, MN = self.model_step(Sx[:, t, :], X[:, t], h, MN)
            # h2 = self.gru2(y, h2)
            y_sum += y
        y = y_sum / X.shape[1]
        # y = h2
        # self.MergeE[0] = 0
        # SBy = self.By[Y]
        MergeE = torch.cat((self.E, self.KBE), 1)
        mask = torch.ones_like(MergeE, device=self.device)
        mask[0] = 0
        Sy = (MergeE * mask)
        Sy = self.hidden_activation(self.mlp2(Sy))  # b * n * out_dim
        if predict:
            # y = F.softmax(self.mlp2(y), dim=1)

            scores = F.softmax(torch.matmul(y, Sy.transpose(-1, -2)), dim=1)
        else:
            # y = F.log_softmax(self.mlp2(y), dim=1)

            scores = F.log_softmax(torch.matmul(y, Sy.transpose(-1, -2)), dim=1)
        return scores, y


    def predict_next_batch(self, input_item_ids):
        '''
        Gives predicton scores for a selected set of items. Can be used in batch mode to predict for multiple independent events (i.e. events of different sessions) at once and thus speed up evaluation.

        If the session ID at a given coordinate of the session_ids parameter remains the same during subsequent calls of the function, the corresponding hidden state of the network will be kept intact (i.e. that's how one can predict an item to a session).
        If it changes, the hidden state of the network is reset to zeros.

        Parameters
        --------
        session_ids : 1D array
            Contains the session IDs of the events of the batch. Its length must equal to the prediction batch size (batch param).
        input_item_ids : 1D array
            Contains the item IDs of the events of the batch. Every item ID must be must be in the training data of the network. Its length must equal to the prediction batch size (batch param).
        predict_for_item_ids : 1D array (optional)
            IDs of items for which the network should give prediction scores. Every ID must be in the training set. The default value is None, which means that the network gives prediction on its every output (i.e. for all items in the training set).
        batch : int
            Prediction batch size.

        Returns
        --------
        out : pandas.DataFrame
            Prediction scores for selected items for every event of the batch.
            Columns: events of the batch; rows: items. Rows are indexed by the item IDs.

        '''
        self.eval()
        with torch.no_grad():
            # in_idxs = self.itemidmap[input_item_ids]
            in_idxs = torch.tensor(input_item_ids, device=self.device, dtype=torch.int64)
            yhat, hidden = self(in_idxs, predict=True)
            # preds = np.asarray(yhat.cpu()).T
            # return pd.DataFrame(data=preds)
            return yhat, hidden


class KVMNAdapter(Recommender):
    def __init__(self, n_items, n_relations, hidden_size, embedding_dim, kbemb_dim, batch_size, topk=20, layers=[64]):
        super(KVMNAdapter, self).__init__()
        self.model = KVMN(n_items=n_items, n_r=n_relations, out_dim=hidden_size, embedding=embedding_dim,
                          KBembedding=kbemb_dim, batch_size=batch_size, layers=layers)
        self.k = topk
        self.load()

    def load(self):
        self.model.load_state_dict(torch.load('recsys/model/KVMN.pt', map_location=self.model.device))

    def rank(self, seq, lengths, hidden):
        scores, hidden = self.model.predict_next_batch(seq)
        _, top_idx = scores.topk(self.k, -1)
        return top_idx, hidden

    def recall(self, seq, lengths, hidden, init=False):
        seq, lengths = pad(seq, lengths, self.model.device)
        hiddens = self.model.init_hidden(len(hidden))
        if not init:
            hiddens[0, :, :self.model.embedding_dim] = torch.tensor(hidden, device=self.model.device)
        with torch.no_grad():
            top_idx, hidden = self.rank(seq, lengths, hiddens)
        return top_idx.numpy(), hidden.numpy()

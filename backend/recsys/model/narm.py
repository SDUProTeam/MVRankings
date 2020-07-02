import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from recsys.model.utils import sort_padded
from .recommender import Recommender


class NARM(nn.Module):
    """Neural Attentive Session Based Recommendation Model Class

    Args:
        n_items(int): the number of items
        hidden_size(int): the hidden size of gru
        embedding_dim(int): the dimension of item embedding
        batch_size(int): 
        n_layers(int): the number of gru layers

    """

    def __init__(self, n_items, hidden_size, embedding_dim, batch_size, n_layers=1):
        super(NARM, self).__init__()
        self.n_items = n_items
        self.hidden_size = hidden_size
        self.batch_size = batch_size
        self.n_layers = n_layers
        self.embedding_dim = embedding_dim
        self.emb = nn.Embedding(self.n_items, self.embedding_dim, padding_idx=0)
        self.emb_dropout = nn.Dropout(0.25)
        self.gru = nn.GRU(self.embedding_dim, self.hidden_size, self.n_layers)
        self.a_1 = nn.Linear(self.hidden_size, self.hidden_size, bias=False)
        self.a_2 = nn.Linear(self.hidden_size, self.hidden_size, bias=False)
        self.v_t = nn.Linear(self.hidden_size, 1, bias=False)
        self.ct_dropout = nn.Dropout(0.5)
        self.b = nn.Linear(self.hidden_size * 2, self.embedding_dim, bias=False)
        # self.ca = nn.Linear(self.hidden_size * 2, self.hidden_size, bias=False)
        # self.sf = nn.Softmax()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, seq, lengths, hidden=None):
        if hidden is None:
            hidden = self.init_hidden(seq.size(1))
        embs = self.emb_dropout(self.emb(seq))
        embs = pack_padded_sequence(embs, lengths)
        gru_out, hidden = self.gru(embs, hidden)
        gru_out, lengths = pad_packed_sequence(gru_out)

        # fetch the last hidden state of last timestamp
        ht = hidden[-1]
        gru_out = gru_out.permute(1, 0, 2)

        c_global = ht
        q1 = self.a_1(gru_out.contiguous().view(-1, self.hidden_size)).view(gru_out.size())
        q2 = self.a_2(ht)

        mask = torch.where(seq.permute(1, 0) > 0, torch.tensor([1.], device=self.device),
                           torch.tensor([0.], device=self.device))
        q2_expand = q2.unsqueeze(1).expand_as(q1)
        q2_masked = mask.unsqueeze(2).expand_as(q1) * q2_expand

        alpha = self.v_t(torch.sigmoid(q1 + q2_masked).view(-1, self.hidden_size)).view(mask.size())
        c_local = torch.sum(alpha.unsqueeze(2).expand_as(gru_out) * gru_out, 1)

        c_t = torch.cat([c_local, c_global], 1)
        c_t = self.ct_dropout(c_t)
        # c_t = self.ca(c_t)

        item_embs = self.emb(torch.arange(self.n_items, device=self.device))
        scores = torch.matmul(self.b(c_t), item_embs.permute(1, 0))
        # scores = self.sf(scores)

        return scores, c_t

    def init_hidden(self, batch_size):
        return torch.zeros((self.n_layers, batch_size, self.hidden_size), requires_grad=True, device=self.device)


class NARMAdapter(Recommender):
    def __init__(self, n_items, hidden_size, embedding_dim, batch_size, topk=20, n_layers=1):
        super(NARMAdapter, self).__init__()
        self.model = NARM(n_items, hidden_size, embedding_dim, batch_size, n_layers)
        self.k = topk
        self.load()

    def load(self):
        self.model.load_state_dict(torch.load('recsys/model/narm.pt', map_location=self.model.device))

    def rank(self, seq, lengths, hidden):
        scores, hidden = self.model(seq, lengths, hidden)
        _, top_idx = scores.topk(self.k, -1)
        return top_idx, hidden

    def recall(self, seq, lengths, hidden, init=False):
        seq, lengths, reindex = sort_padded(seq, lengths, self.model.device)
        hiddens = self.model.init_hidden(len(hidden))
        if not init:
            hiddens[0, :, :self.model.embedding_dim] = torch.tensor(hidden, device=self.model.device)
        with torch.no_grad():
            top_idx, hidden = self.rank(seq, lengths, hiddens)
        return top_idx[reindex].numpy(), hidden[reindex].numpy()

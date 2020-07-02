
from queue import Queue
from .setting import setting
from .model.recommender import Recommender
from .model.narm import NARMAdapter
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# Create your models here.

class Pack:
    def __init__(self, flag=False, _id=None, seq=None, hidden=None):
        self.flag = flag    # True means activation signal
        self._id = _id
        self.seq = seq
        if hidden:
            self.hidden = hidden
        else:
            self.hidden = [0] * setting['hidden_dim']


class BatchPool:
    def __init__(self, pool_size=200, timeout=0.5):
        self.timeout = timeout
        self.uid2idx = dict()
        self.res = dict()
        self.pool_size = pool_size
        self.waiting_list = Queue(pool_size + 1)
        self.notify_queue = Queue(pool_size)
        self.data = {'seq': list(), 'lengths': list(), 'hidden': list()}
        self.shed = BackgroundScheduler()
        self.job = self.shed.add_job(self.awake, 'interval', seconds=timeout)
        self.shed.start()


    def awake(self):
        if len(self.uid2idx) > 0:
            self.waiting_list.put(Pack(), block=False)

    def clear(self):
        self.uid2idx.clear()
        for key in self.data.keys():
            self.data[key].clear()

    def recall_one(self, preference: list, emb=None):
        top_items, hiddens = recommender.recall(
            seq=[preference], lengths=[len(preference)], hidden=[emb], init=emb is None or len(emb) == 0)
        return top_items[0], hiddens[0]


    def get_recalls(self):
        while True:
            item = self.waiting_list.get()
            if item.flag:
                self.uid2idx[item._id] = len(self.data['seq'])
                self.data['seq'].append(item.seq)
                self.data['hidden'].append(item.hidden)
                self.data['lengths'].append(len(item.seq))
            if len(self.uid2idx) >= self.pool_size or not item.flag and len(self.uid2idx) > 0:
                self.job.pause()
                top_items, hiddens = recommender.recall(**self.data)
                for uid, idx in self.uid2idx.items():
                    self.res[uid] = {'iids': top_items[idx], 'emb': hiddens[idx]}
                self.waiting_list.unfinished_tasks = 1
                self.waiting_list.task_done()
                for i in range(len(self.uid2idx)):
                    try:
                        self.notify_queue.get()
                    except Exception as e:
                        print(e)
                self.clear()
                self.job.resume()

    async def ask_for_recall(self, _id, seq, hidden):
        self.waiting_list.put(Pack(True, _id, seq, hidden))
        self.waiting_list.join()
        res = self.res.pop(_id)
        iids = res['iids']
        emb = res['emb']
        self.notify_queue.put(1)
        return iids, emb


recommender = Recommender
if setting['model'] == 'NARM':
    recommender = NARMAdapter(topk=setting['topk'], **setting[setting['model']])
pool = BatchPool()
thread = threading.Thread(target=pool.get_recalls)
thread.start()

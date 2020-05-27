import json
from collections import defaultdict
from db import Database
import json

with open('setting.json') as f:
    setting = json.load(f)
db = Database('movie', setting['host'], 27017, setting['username'], setting['password'])

def common(list1, list2):
    res = []
    for i in list1:
        for j in list2:
            if i == j:
                res.append(i)
    return res


def wrap(items):
    data = {"source": defaultdict(dict)}
    srcs = ["douban", "mtime", "maoyan"]
    for item in items:
        for key in ["name", "casts", "directors", "type", "time"]:
            if key in item:
                data[key] = item[key]
        for key in ["id", "rate", "url", "cover"]:
            if key in item:
                data["source"][item["source"]][key] = item[key]
        # srcs.remove(item["source"])
    # for src in srcs:
    #     data["source"][src] = {"rate": ""}
    db.insert_one('fusion', data)


cursor = {}
for source in ['douban', 'maoyan', 'mtime']:
    cursor[source] = db.find('profile', {"source": source})

pipeline = [{
        '$group': {
            '_id': "$name",
            'uniqueIds': {
                '$addToSet': '$_id'
            },
            'count': {
                '$sum': 1
            }
        }
    },
    {
        '$match': {
            'count': {
                '$gt': 1
            }
        }
    }
]

for group in db.db.profile.aggregate(pipeline):
    docs = defaultdict(list)
    for id in group["uniqueIds"]:
        doc = db.find_one('profile', id)
        docs[doc["source"]].append(doc)

    if len(docs) == 1:
        continue

    unique = True
    for item in docs.values():
        if len(item) > 1:
            unique = False

    if unique:
        wrap([item[0] for item in docs.values()])
        continue

    if "maoyan" in docs:
        for a in docs['maoyan']:
            potential = []
            if "mtime" in docs:
                if len(docs['mtime']) == 1:
                    b = docs['mtime'][0]
                    if not b.get("time") or a.get("time") and a["time"].startswith(b["time"]):
                        potential.append(b)
                elif a.get("time"):
                    for b in docs['mtime']:
                        if b.get("time") and a["time"][:4] == b["time"]:
                            potential.append(b)
                            break
            if "douban" in docs:
                if len(docs['douban']) == 1:
                    b = docs['douban'][0]
                    if not b.get("casts") or a.get("casts") and common(a["casts"], b["casts"]):
                        potential.append(b)
                elif a.get("casts"):
                    for b in docs['douban']:
                        if b.get("casts") and common(a["casts"], b["casts"]):
                            potential.append(b)
                            break
            if len(potential) > 1:
                potential.append(a)
                wrap(potential)



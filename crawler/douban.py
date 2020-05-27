import requests_html
from db import Database
# from proxy.client.py_cli import ProxyFetcher
import time
import random
import json
from fake_useragent import UserAgent

ua = UserAgent()

session = requests_html.HTMLSession()
# session = requests.session()
session.keep_alive = False
url = 'https://movie.douban.com/j/new_search_subjects?sort=T&range={},{}&tag={}&start={}'

# fetcher = ProxyFetcher('https')

with open('setting.json') as f:
    setting = json.load(f)
db = Database('movie', setting['host'], 27017, setting['username'], setting['password'])

tag = ''
for rate in range(0, 2):
    start = 0
    if rate == 0:
        start = 1240
    while start < 5000:
        print(rate, start)
        while True:
            # proxy = session.get('http://api.ipify.org', proxies={'http': 'http://127.0.0.1:8081'}).text
            # proxies = session.get('http://localhost:8899/api/v1/proxies?anonymous').json()['proxies']
            # proxy = random.choice(proxies)
            # proxy = proxy['ip'] + ':' + str(proxy['port'])
            # proxy = fetcher.get_proxy()
            # while not proxy:
            #     print('no available proxy')
            #     time.sleep(5)
            #     proxy = fetcher.get_proxy()
            resp = session.get(url.format(rate, rate+1, tag, start),
                               headers={'User-Agent': ua.random,
                                        'referer': 'https://movie.douban.com/tag/',
                                        'Host': 'movie.douban.com',
                                        'Accept-Language': 'zh-CN,zh;q=0.9'},
                               # proxies={'http': proxy},
                               timeout=5,
                               # verify=False
                               )
            if 'data' in resp.json():
                break
            else:
                print(resp.text)
                # fetcher.proxy_feedback('failure')
                time.sleep(1000)
        data = resp.json()['data']
        if len(data) == 0:
            break
        for d in data:
            d['source'] = 'douban'
            if 'title' in d:
                d['name'] = d.pop('title')
            del d['cover_x'], d['cover_y'], d['star']
        print(data)
        db.insert_many('profile', data)
        start += 20
        time.sleep(random.uniform(60, 90))

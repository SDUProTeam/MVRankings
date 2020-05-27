import requests_html
import requests
from lxml import etree
from db import Database
# from proxy.client.py_cli import ProxyFetcher
import time
import random
import re
from fake_useragent import UserAgent
import json

ua = UserAgent()

head = """
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: max-age=0
Connection: keep-alive
Host: movie.mtime.com
Referer: http://movie.mtime.com/movie/search/section/?rating=1_10
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"""

def str_to_dict(header):
    """
    构造请求头,可以在不同函数里构造不同的请求头
    """
    header_dict = {}
    header = header.split('\n')
    for h in header:
        h = h.strip()
        if h:
            k, v = h.split(':', 1)
            header_dict[k] = v.strip()
    return header_dict

headers = str_to_dict(head)
url = 'http://movie.mtime.com/movie/search/section/?rating=1_10#pageIndex={}&color=433'
# fetcher = ProxyFetcher('https')
start = 3107
with open('setting.json') as f:
    setting = json.load(f)
db = Database('movie', setting['host'], 27017, setting['username'], setting['password'])


def init(start):
    session = requests_html.HTMLSession()
    # session = requests.session()
    session.keep_alive = True
    r = session.get(url.format(start), headers=headers)
    r.html.render(sleep=1, scrolldown=3, keep_page=True)
    return session, r

pre = None
session, r = init(start)

for pageIndex in range(start, 5342):
    print(pageIndex)
    # headers['User-Agent'] = ua.random

    async def run():
        await r.html.page.click('a#key_nextpage')
        # await r.html.page.screenshot({'path':'shot.png'})
        return await r.html.page.content()
    html = session.loop.run_until_complete(run())
    tree = etree.HTML(html)
    print('rendered.')
    i = 0
    for tr in tree.xpath('//ul[@class="ser_mlist2"]//div[@class="t_r"]'):
        data = {'source': 'mtime'}
        mt6 = tr.find('.//h3[@class="normal mt6"]/a')
        if mt6 is None or mt6.text is None:
            continue
        data['name'] = mt6.text.strip()
        if data['name'] == '':
            continue
        if pre and i==0 and data['name'] == pre['name']:
            time.sleep(60)
            session, r = init(pageIndex)
            break
        data['url'] = mt6.get('href')
        data['id'] = re.search('\d+', data['url']).group()
        data['cover'] = tr.find('.//img').get('src')
        data['rate'] = tr.find('.//p[@class="point ml6"]').text
        data['time'] = tr.find('.//span[@class="c_666"]').text.strip('()')
        data['rate_num'] = int(tr.find('.//p[@class="c_666 mt6"]').text[:-3])
        db.insert_one('profile', data)
        print(data)
        if i == 0:
            pre = data
        i += 1
    time.sleep(random.uniform(60, 90))


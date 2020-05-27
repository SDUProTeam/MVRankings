import requests_html
import requests
from db import Database
# from proxy.client.py_cli import ProxyFetcher
import time
import random
import re
import json
from fake_useragent import UserAgent

ua = UserAgent()

head = """
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: maoyan.com
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
"""

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
session = requests_html.HTMLSession()
# session = requests.session()
session.keep_alive = False
url = 'https://maoyan.com/films?&catId={}&showType=3&offset={}'
# fetcher = ProxyFetcher('zhihu')

with open('setting.json') as f:
    setting = json.load(f)
db = Database('movie', setting['host'], 27017, setting['username'], setting['password'])

for catId in list(range(0, 26)) + [100]:
    # for yearId in range(1, 16):
    for offset in range(0, 2010, 30):
        # time.sleep(random.random() * 30)
        print(catId, offset)
        # proxy = session.get('http://api.ipify.org', proxies={'http': 'http://127.0.0.1:8081'}).text
        # proxies = session.get('http://localhost:8899/api/v1/proxies?anonymous').json()['proxies']
        # proxy = random.choice(proxies)
        # proxy = proxy['ip'] + ':' + str(proxy['port'])
        # proxy = fetcher.get_proxy()
        # print(proxy)
        headers['User-Agent'] = ua.random
        while True:
            r = session.get(url.format(catId, offset), headers=headers,
                            # proxies={'http': proxy},
                            timeout=5)
            r.encoding = 'utf-8'
            if 'verify' in r.url or r.status_code != 200:
                print(r.url)
                catId += 1
                time.sleep(9000)
            elif '很抱歉，您的访问请求由于过于频繁而被禁止。' in r.text:
                print(r.text)
                time.sleep(1500)
            else:
                break
        if '抱歉，没有找到相关结果' in r.text:
            break
        for hover in r.html.find('div.movie-item-hover'):
            data = {'source': 'maoyan'}
            href = hover.find('a', first=True).attrs['href']
            data['id'] = re.search('\d+', href).group()
            data['url'] = 'https://maoyan.com' + href
            data['cover'] = hover.find('img.movie-hover-img', first=True).attrs['src']
            data['name'] = hover.find('span.name', first=True).text
            if hover.find('span.score', first=True):
                data['rate'] = hover.find('span.score', first=True).text
            for div in hover.xpath('//span[@class="hover-tag"]/..'):
                text = div.text
                if text.startswith('类型') and len(text) > 4:
                    data['type'] = text[4:].split('／')
                if text.startswith('主演') and len(text) > 4:
                    data['casts'] = text[4:].split('／')
                if text.startswith('上映时间') and len(text) > 6:
                    data['time'] = text[6:]
            db.insert_one('profile', data)
            print(data)
        time.sleep(random.uniform(150, 180))
        # headers['Referer'] = url.format(catId, offset)


import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

def get_http_https_proxies():
    pagenum = 4
    ua = UserAgent()
    encoding = 'utf-8'
    s = requests.session()
    s.keep_alive = False
    http_list = []
    https_list = []
    root = 'https://www.xicidaili.com/nn/'
    for i in range(pagenum):
        r = s.get(root + str(pagenum+1), headers={'User-Agent': ua.random})
        r.encoding = encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', {'id': 'ip_list'})
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if tds:
                ip = tds[1].string
                port = tds[2].string
                protocol = tds[5].string
                if protocol == 'HTTP':
                    http_list.append('http://' + ip + ':' + port)
                elif protocol == 'HTTPS':
                    https_list.append('https://' + ip + ':' + port)
    return http_list, https_list


def get_proxies():
    http_list, https_list = get_http_https_proxies()
    return http_list + https_list

def wrap_dict(proxy):
    if proxy[4] == 's':
        return {'https': proxy}
    else:
        return {'http': proxy}


class XiciPool:
    def __init__(self):
        self.proxies = get_proxies()

    def get_proxy(self):
        if len(self.proxies) == 0:
            self.proxies = get_proxies()
        return wrap_dict(random.choice(self.proxies))

    def remove(self, proxy):
        self.proxies.remove(proxy)


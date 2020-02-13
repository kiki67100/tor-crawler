__author__ = "Kevin MULLER https://github.com/kiki67100/"
__copyright__ = "Copyright 2020, kiki67100"
__credits__ = ["kiki67100","edmundmartin.com"]
__license__ = "GPL"
__version__ = "1"

#tested on python3.8

import time
import pprint
import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import urllib.parse

#hidden wiki
bootstrap_url = 'http://onionlinksv3zit3.onion/'

explored = []

class MultiThreadScraper:
    def __log(self, txt):
        filename = "log_full.csv"
        myfile = open(filename, 'a+')
        myfile.write(txt)
        myfile.close()

    def __init__(self, base_url):
        self.base_url = base_url
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=2)
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.to_crawl.put(self.base_url)
        self.host = []

    def parse_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            url = urljoin(self.root_url, url)
            if url.startswith('http'):
                o = urlparse(url)
                if o.hostname[-6:] != '.onion':
                    print("Not .onion bypass")
                    continue
                if url not in self.scraped_pages:
                    self.to_crawl.put(url)

    def scrape_info(self, html, url):
        soup = BeautifulSoup(html)
        title = soup.find('title')
        self.__log(str(url) + ";" + str(title) + "\r\n")
        print("{} = {}".format(url, title))
        return

    def post_scrape_callback(self, res):
        # pprint.pprint(res)
        result = res.result()
        if result and result.status_code == 200:
            self.parse_links(result.text)
            self.scrape_info(result.text, result.url)

    def scrape_page(self, url):
        o = urlparse(url)
        if o.hostname in self.host:
            print("skip")
            return []
        self.host.append(o.hostname)
        print("connect %s" % url)
        time.sleep(1)
        if url == self.base_url:
            print("Bootstrap url connect")
        try:
            res = requests.get(url, timeout=(5))
            if url == self.base_url:
                print("bootstrap OK")
            return res
        except requests.RequestException:
            if url == self.base_url:
                print("bootstrap ERROR please change the bootstrap url %s" % url)
            return []

    def run_scraper(self):
        while True:
            try:
                target_url = self.to_crawl.get(timeout=60)
                if target_url not in self.scraped_pages:
                    # print("Scraping URL: {}".format(target_url))
                    self.scraped_pages.add(target_url)
                    job = self.pool.submit(self.scrape_page, target_url)
                    job.add_done_callback(self.post_scrape_callback)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    print ("Recursive tor crawler\nrun this script on tor network with torsocks python crawler.py\n\n")
    s = MultiThreadScraper(bootstrap_url)
    s.run_scraper()

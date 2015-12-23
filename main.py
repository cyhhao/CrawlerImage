# coding=utf-8
import os
import random
import re
import threading
from httplib import IncompleteRead
import requests
import time
from gevent import Timeout, sleep
from Libs import urlTools
from Libs.Queue import Queue
from Libs.Task import Task
from Libs.UrlSet import UrlSet
from Libs.Url import Url
from settings import proxies, headers, output, request_timeout, outsite_page, doc_pool_max, res_pool_max, main_url, \
    wait_time, recursion_deep, source_error_max, document_error_max, logs_path
from pyquery import PyQuery as pq
import gevent.monkey
import sys

reload(sys)
sys.setdefaultencoding('utf8')
gevent.monkey.patch_all(thread=False)


# todo: 请求资源时加refer
# todo: 网络错误继续加入队列尾

class Crawler:
    def __init__(self, url):
        self.main_url = Url(self.requestGet(url).url)
        self.host_option, self.host, self.host_url = self.main_url.getHost()

        self.queue_resource = None
        self.queue_document = None
        self.set = None
        self.document_task = None
        self.source_task = None

    def __del__(self):
        # del self.document_task
        # del self.queue_document
        # del self.source_task
        # del self.queue_resource
        print 'del c'

    def start(self, is_continue=False):
        if is_continue:
            self.queue_resource = Queue.load(logs_path + 'queue_resource.json')
            self.queue_document = Queue.load(logs_path + 'queue_document.json')
            self.set = UrlSet.load(logs_path + 'url_set.json')
        else:
            self.queue_resource = Queue(logs_path + 'queue_resource.json')
            self.queue_document = Queue(logs_path + 'queue_document.json')
            self.set = UrlSet(logs_path + 'url_set.json')

        self.document_task = Task(self.queue_document, doc_pool_max)
        self.document_task.initTaskWork(self.getDocument)

        self.source_task = Task(self.queue_resource, res_pool_max)
        self.source_task.initTaskWork(self.requestSource)

        self.main_url = urlTools.dealUrl2Request(self.main_url, self.main_url)
        print self.main_url, self.host
        file_path, file_name, html_url = urlTools.dealUrl2File(self.main_url, self.main_url, self.host, True)
        self.queue_document.push([self.main_url, file_path, file_name, 0, 0])
        print "file_path:" + file_path, "file_name:" + file_name, "html_url:" + html_url
        self.document_task.start()

    def requestGet(self, url):
        wait = random.random() * (wait_time[1] - wait_time[0])
        sleep(wait)
        timeout = Timeout(request_timeout)
        timeout.start()
        try:
            req = requests.get(url=url, verify=True, headers=headers, proxies=proxies)
        except IncompleteRead:
            pass
            # todo:未知错误，暂还未查清
        timeout.cancel()
        return req

    def saveFile(self, file_path, file_name, bytes):
        path = Url(output + file_path)
        path = path.addUrlEnd()
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            f = open(path + file_name, "wb")
            f.write(bytes)
            f.close()
        except IOError, e:
            print 'save Error: ', e, 'path: ', path, 'name: ', file_name

    def requestSource(self, request_url, file_path, file_name, error_count):
        print request_url
        if error_count > source_error_max:
            return
        try:
            req = self.requestGet(request_url)
            content = req.content
            if 'content-type' in req.headers:
                if 'text/css' in req.headers['content-type']:
                    # req.encoding = 'utf-8'
                    content = self.dealCss(content, req.url)
                    # content = text.decode(req.encoding, errors='ignore')
                    # content = text

            self.saveFile(file_path, file_name, content)
        except requests.exceptions.ConnectionError, e:
            print 'ConnectionError:', e
            self.queue_resource.push([request_url, file_path, file_name, error_count + 1])
        except Timeout:
            print request_url, 'TimeOut !'
            self.queue_resource.push([request_url, file_path, file_name, error_count + 1])

    def dealCss(self, text, origin_url):
        list = re.findall(r'url\(\'(.*?)\'\)|url\(\"(.*?)\"\)|url\((.*?)\)', text)
        for ans_list in list:
            for li in ans_list:
                if li != '' and not li.startswith('data'):
                    request_url = urlTools.dealUrl2Request(li, origin_url)
                    if request_url in self.set:
                        file_path, file_name, html_url = self.set[request_url]
                    else:
                        file_path, file_name, html_url = urlTools.dealUrl2File(request_url, origin_url, self.host, True)
                        error_count = 0
                        self.queue_resource.push([request_url, file_path, file_name, error_count])
                        self.set[request_url] = [file_path, file_name, html_url]
                    # self.requestSource(request_url, file_path, file_name)
                    text = text.replace(li, html_url.encode())

        return text

    def dealSourceLink(self, linkList, origin_url, attr):
        for li in linkList:
            url = pq(li).attr(attr)
            if url is not None:
                url = Url(url)
                request_url = urlTools.dealUrl2Request(url, origin_url)
                if request_url in self.set:
                    file_path, file_name, html_url = self.set[request_url]
                else:
                    file_path, file_name, html_url = urlTools.dealUrl2File(request_url, origin_url, self.host, True)
                    error_count = 0
                    self.queue_resource.push([request_url, file_path, file_name, error_count])
                    self.set[request_url] = [file_path, file_name, html_url]
                pq(li).attr(attr, html_url)

    def getHTMLCharset(self, content):
        d = pq(content)
        charset = 'utf-8'
        meta1 = d('meta[http-equiv]').attr('content')
        meta2 = d('meta[charset]').attr('charset')
        if meta1 is not None:
            res = re.findall(r'charset\s*=\s*(\S*)\s*;?', meta1)
            if len(res) != 0:
                charset = res[0]
        if meta2 is not None:
            charset = meta2
        return charset

    def dealALink(self, linkList, origin_url, attr, deep):
        for li in linkList:
            url = pq(li).attr(attr)
            if url is not None:
                url = Url(url)
                request_url = urlTools.dealUrl2Request(url, origin_url)
                # print 'A:', request_url
                if outsite_page or request_url.getHost()[1] == self.host:
                    if request_url in self.set:
                        file_path, file_name, html_url = self.set[request_url]
                    else:
                        file_path, file_name, html_url = urlTools.dealUrl2File(request_url, origin_url, self.host, True)
                        self.queue_document.push([request_url, file_path, file_name, deep + 1, 0])
                        self.set[request_url] = [file_path, file_name, html_url]
                    pq(li).attr(attr, html_url)

    def getDocument(self, url, file_path, file_name, deep, error_count):
        if 0 <= recursion_deep < deep or error_count > document_error_max:
            return
        url = urlTools.dealUrl2Request(url, url)

        if file_path == '' and file_name == '':
            file_name = 'index.html'
        try:
            req = self.requestGet(url)
            charset = self.getHTMLCharset(req.content)
            req.encoding = charset
            d = pq(req.text)
            # print charset

            linkList1 = d('link')
            self.dealSourceLink(linkList1, Url(req.url), 'href')

            linkList2 = d('script')
            self.dealSourceLink(linkList2, Url(req.url), 'src')

            linkList3 = d('img')
            self.dealSourceLink(linkList3, Url(req.url), 'src')

            linkList4 = d('a')
            self.dealALink(linkList4, Url(req.url), 'href', deep)

            self.source_task.start()

            self.saveFile(file_path, file_name, bytearray(source=d.outer_html(), encoding='utf-8'))
        except requests.exceptions.ConnectionError, e:
            print 'ConnectionError:', e
            self.queue_document.push([url, file_path, file_name, deep, error_count + 1])
        except Timeout:
            print url, 'TimeOut !'
            self.queue_document.push([url, file_path, file_name, deep, error_count + 1])

    def stop(self):
        self.set.save()
        self.document_task.stop()
        self.source_task.stop()


def work():
    print 123

    c.start()
    time.sleep(10)
    print 321


if __name__ == '__main__':
    url0 = raw_input("input the Url:")
    c = Crawler(Url(url0))


    def work(is_continue):
        c.start(is_continue)
        print 'work stoped'


    print "Enter 's' to start, 'c' to continue, 'e' to stop."
    while True:
        char = raw_input()
        if char == 's':
            p = threading.Thread(target=work, args=(False,))
            print 'Process will start.'
            p.start()
        elif char == 'c':
            p = threading.Thread(target=work, args=(True,))
            print 'Process will start.'
            p.start()
        elif char == 'e':
            c.stop()
            break

# coding=utf-8
import hashlib
import os
import re

from Libs.Url import Url


class UrlPathTools:
    replaceChr = {
        '\\': 'xg',
        ':': 'mh',
        '*': 'xh',
        '?': 'wh',
        '<': 'xy',
        '>': 'dy',
        '|': 'sx',
        ' ': 'kg'
    }
    head = ['http://', 'https://', '//']

    def __init__(self):
        pass

    def dealUrl2Request(self, url, origin):
        origin = Url(origin)
        url = Url(url)
        if not url.startswith('http://') and not url.startswith('https://'):
            if url.startswith('//'):
                url = 'http:' + url
            elif url.startswith('/'):
                url = origin.getHost()[2] + url
            else:
                origin = origin.getUrlDir()
                url = origin + url
        url = url.simplifyUrl()
        return url

    def convLongPath(self, file_path, file_name):
        if len(file_name) > 128:
            file_name = Url(hashlib.sha1(file_name).hexdigest())
        if len(file_path) > 128:
            # 懒得管最前面有没有/了
            file_path = file_path[0] + Url(hashlib.sha1(file_path).hexdigest())
        # path_dirs = file_path.split('/')
        # for i, it in enumerate(path_dirs):
        #     if len(it) > 250:
        #         path_dirs[i] = str(hashlib.sha1(it).hexdigest())
        # file_path = '/'.join(path_dirs)
        return file_path, file_name

    def dealUrl2File(self, url, origin, host=None, is_req_url=False):
        """
        :param
            url: 待处理的url
            origin: 请求发生时所在的url
            host: 对于域名为host的url，资源存放目录为output根目录，而不是域名文件夹。默认不设置主host
            is_req_url: url是否做过 dealUrl2Request 处理

        :return
        """

        if not is_req_url:
            url = self.dealUrl2Request(url, origin)
        # url = self.simplifyUrl(url)
        # url除去最后的/
        url = url.delUrlEnd()

        if host is not None:
            # 如果该url就是这个站点域名下的，那么无需新建域名目录存放
            if url.cmpHost(host):
                # 除去host 这里有可能超出output根目录
                url = url.delHttp()
                url = url.delUrlStart()
                url = url.replace(host.getHost()[1], '')
        # 除去头，变身成文件路径
        url = url.delHttp()
        url = url.delUrlStart()
        for k, v in self.replaceChr.iteritems():
            if k in url:
                url = url.replace(k, v)


        file_name = Url(os.path.basename(url))
        file_path = Url(os.path.dirname(url))
        # 如果文件名或文件路径过长
        file_path, file_name = self.convLongPath(file_path, file_name)

        # if file_path.startswith('/') or file_path.startswith('.'):
        #     file_path = file_path[1:]
        # 为了解决同一目录下，文件和文件夹名不能重复的问题
        if file_name != '':
            file_name = 'f_'+file_name
        url = file_path.addUrlEnd() + file_name
        url = url.addUrlStart()

        # 当file_path为""时,表示当前目录
        return file_path, file_name, url

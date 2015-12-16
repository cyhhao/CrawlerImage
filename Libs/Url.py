import re


class UrlMetaclass(type):
    def __new__(cls, name, bases, attrs):
        bb = bases[0]
        not_change = ['__str__', '__new__', '__init__', '__eq__', '__hash__']
        for name, v in bb.__dict__.iteritems():
            if hasattr(v, '__call__') and name not in not_change:
                def call(func, father):
                    def d(*args, **dic):
                        # print func
                        vv = func(*args, **dic)
                        if isinstance(vv, father):
                            return Url(vv)
                        # elif isinstance(vv, dict):
                        #     for k, v in vv.iteritems():
                        #         if isinstance(v, father):
                        #             vv[k] = Url(v)
                        # elif isinstance(vv, list):
                        #     for i, v in enumerate(vv):
                        #         if isinstance(v, father):
                        #             vv[i] = Url(v)

                        return vv

                    return d

                attrs[name] = call(v, bb)
        return type.__new__(cls, name, bases, attrs)


class Url(str):
    __metaclass__ = UrlMetaclass
    head = ['http://', 'https://', '//']

    def __init__(self, string):
        if isinstance(string, unicode):
            string = string.encode(encoding='utf8', errors='ignore')

        super(Url, self).__init__(string)

    def __radd__(self, other):
        return Url(str(other) + str(self))

    def simplifyUrl(self):
        url = self.delUrlSharp()
        url, http = url.delHttp(ret=True)
        return Url(''.join([http, url.simplifyPath()]))

    def delUrlSharp(self):
        return Url(self.split('#')[0])

    def delHttp(self, ret=False):
        for h in self.head:
            if self.startswith(h):
                url = self.replace(h, '/')
                if ret:
                    return url, Url(h)
                else:
                    return url
        if ret:
            return self, Url('')
        else:
            return self

    def simplifyPath(self):
        stack = []
        for item in self.split("/"):
            if item not in [".", "..", ""]:
                stack.append(item)
            if item == ".." and stack:
                stack.pop()
        return "/".join(stack)

    def cmpUrl(self, url1, url2):
        url1 = url1.simplifyUrl().delHttp()
        url2 = url2.simplifyUrl().delHttp()
        if hash(url1) == hash(url2):
            return True
        else:
            return False

    def addUrlEnd(self):
        if not self.endswith('/'):
            return self + '/'
        return self

    def delUrlEnd(self):
        url = self
        if self.endswith('/'):
            url = url[:-1]
        return url

    def delUrlStart(self):
        url = self
        if url.startswith('/'):
            url = url[1:]
        return url

    def getHost(self):
        """
        :param
            url: 'http://xxx.xxx.com/xxx/xxx.xx'
        :return
            host_option: ('http://','xxx.xxx.com')
            host: 'xxx.xxx.com'
            host_url: 'http://xxx.xxx.com'
        """
        url = self
        host_option = re.findall(r'(http://|https://)?([^/]*)', url)[0]
        host = host_option[1]
        host_url = ''.join(host_option)
        return Url(host_option), Url(host), Url(host_url)

    def cmpHost(self, url2):
        url1 = self
        host1 = self.getHost()[1]
        host2 = self.getHost()[1]
        if host1 == host2:
            return True
        else:
            return False

    def addUrlStart(self):
        url = self
        if not url.startswith('/'):
            url = '/' + url
        return url

    def getUrlDir(self):
        start = self.find('//')
        end = self.rfind('/')
        url = self
        if start + 1 == end:
            url += '/'
        else:
            url = Url('/'.join(url.split('/')[:-1]))
        return url.addUrlEnd()

    def getHttp(self):
        for h in self.head:
            if self.startswith(h):
                return h
        return Url('')

    def str(self):
        return self.__str__()

    def __eq__(self, other):
        return self.cmpUrl(self, Url(other))

    def __hash__(self):
        return str(self.simplifyUrl().delHttp()).__hash__()

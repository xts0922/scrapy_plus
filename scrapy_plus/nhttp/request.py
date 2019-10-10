# scrapy/nhttp/request.py
'''封装Request对象'''

class Request(object):
    '''框架内置请求对象，设置请求信息'''

    # 此处修改
    def __init__(self, url, method='GET', headers=None, params=None, data=None, parse='parse', meta={}):
        self.url = url    # 请求地址
        self.method = method    # 请求方法
        self.headers = headers    # 请求头
        self.params = params    # 请求参数
        self.data = data    # 请求体

        # 此处新增
        self.parse = parse    # 指明它的解析函数, 默认是parse方法
        self.meta = meta
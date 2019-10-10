# scrapy/nhttp/response.py
'''封装Response对象'''
import re # 此处新增
import json # 此处新增

from lxml import etree # 此处修改requirments.txt文件 # 此处新增
class Response(object):
    '''完成对响应对象的封装'''

    # 此处修改
    def __init__(self, url,status_code, headers,body, meta={}):
        '''
        初始化resposne对象
        :param url: 响应的url地址
        :param body: 响应体
        :param headers:  响应头
        :param status_code: 状态码
        '''
        self.url = url
        self.headers = headers
        self.status_code = status_code
        self.body = body

        # 此处新增
        self.meta = meta



    # 此处新增
    def xpath(self, rule):
        '''提供xpath方法'''
        html = etree.HTML(self.body)
        return html.xpath(rule)
        # 此处新增

    @property
    def json(self):
        '''提供json解析
        如果content是json字符串，是才有效
        '''
        return json.loads(self.body)
        # 此处新增

    def re_findall(self, rule, data=None):
        '''封装正则的findall方法'''
        if data is None:
            data = self.body
        return re.findall(rule, data)
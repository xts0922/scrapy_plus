# scrapy_plus/core/spider.py
'''爬虫组件封装'''

from item import Item    # 导入Item对象
from nhttp.request import Request    # 导入Request对象


class Spider(object):
    '''
    1. 构建请求信息(初始的)，也就是生成请求对象(Request)
    2. 解析响应对象，返回数据对象(Item)或者新的请求对象(Request)
    '''
    name = ''  # 此处新增
    #
    # start_url = 'http://www.baidu.com'    # 默认初始请求地址
    #                                   #这里以请求百度首页为例
    start_urls = []  # 重写start_requests方法后，这个属性就没有设置的必要了
    def start_requests(self):
        '''构建初始请求对象并返回'''
        for url in self.start_urls:
            yield Request(url)
    def parse(self, response):
        '''解析请求
        并返回新的请求对象、或者数据对象
        '''
        # return Item(response.body)   # 返回item对象
        yield Item(response.body)
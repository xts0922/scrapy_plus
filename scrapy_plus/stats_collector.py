import redis
from conf.settings import REDIS_HOST, REDIS_PORT, REDIS_DB


class StatsCollector(object):
    """对各种数量的统计，包括总的请求数量，总的响应数量，总的重复数量"""
    def __init__(self, spider_names=[], host=REDIS_HOST,
                 port=REDIS_PORT, db=REDIS_DB, password=None):

        self.redis = redis.StrictRedis(host=host, port=port, db=db, password=password)
        #存储请求数量的键
        self.request_nums_key = "_".join(spider_names) + "_request_nums"
        #存储响应数量的键
        self.response_nums_key = "_".join(spider_names) + "_response_nums"
        #存储重复请求的键
        self.repeat_request_nums_key = "_".join(spider_names) + "_repeat_request_nums"
        #存储start_request数量的键
        self.start_request_nums_key = "_".join(spider_names) + "_start_request_nums"

    def incr(self, key):
        '''给键对应的值增加1，不存在会自动创建，并且值为1，'''
        self.redis.incr(key)

    def get(self, key):
        '''获取键对应的值，不存在是为0，存在则获取并转化为int类型'''
        ret = self.redis.get(key)
        if not ret:
            ret = 0
        else:
            ret = int(ret)
        return ret

    def clear(self):
        '''程序结束后清空所有的值'''
        self.redis.delete(self.request_nums_key, self.response_nums_key,
                          self.repeat_request_nums_key, self.start_request_nums_key)

    @property
    def request_nums(self):
        '''获取请求数量'''
        return self.get(self.request_nums_key)

    @property
    def response_nums(self):
        '''获取响应数量'''
        return self.get(self.response_nums_key)

    @property
    def repeat_request_nums(self):
        '''获取重复请求数量'''
        return self.get(self.repeat_request_nums_key)

    @property
    def start_request_nums(self):
        '''获取start_request数量'''
        return self.get(self.start_request_nums_key)
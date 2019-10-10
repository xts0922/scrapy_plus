# scrapy_plus/core/scheduler.py
'''调度器模块封住'''
from six.moves.queue import Queue

import six
import w3lib.url  # 修改requirements.txt文件
from hashlib import sha1
# 此处新增
from stats_collector import StatsCollector # 此处新增
from utils.queue import Queue as ReidsQueue
from conf.settings import SCHEDULER_PERSIST
from utils.set import NoramlFilterContainer, RedisFilterContainer
from  utils.log import logger
class Scheduler(object):
    '''
    1. 缓存请求对象(Request)，并为下载器提供请求对象，实现请求的调度
    2. 对请求对象进行去重判断
    '''
    def __init__(self):
        if SCHEDULER_PERSIST:  # 如果使用分布式或者是持久化，使用redis的队列
            self.queue = ReidsQueue()
            self._filter_container = RedisFilterContainer()  # 使用redis作为python的去重的容器
        else:
            self.queue = Queue()
            self._filter_container = NoramlFilterContainer()  # 使用Python的set()集合

        # self.repeat_request_num = 0  # 统计重复的数量
        # 在engine中阻塞的位置判断程序结束的条件：成功的响应数+重复的数量>=总的请求数量
        self.collector = StatsCollector
        self._filter_container = set()  # 去重容器,是一个集合,存储已经发过的请求的特征 url
        self.total_request_number = 0  # 此处新增
    def add_request(self, request):
        '''添加请求对象'''
        # 添加请求对象,前提是指纹没有重复
        if self._filter_request(request):
            self.queue.put(request)
        self.total_request_number += 1  # 此处新增
    def get_request(self):
        # '''获取一个请求对象并返回'''
        # request = self.queue.get()
        # return request
        '''获取一个请求对象并返回'''
        try:
            # 设置为非阻塞
            request = self.queue.get(False)
        except:
            return None
        else:
            return request
    def _filter_request(self,request):
        # 去重方法
        request.fp = self._gen_fp(request)  # 给request对象增加一个fp指纹属性
        # if request.fp not in self._filter_container:
        if not self._filter_container.exists(request.fp):
            self._filter_container.add(request.fp)  # 向指纹容器集合添加一个指纹
            return True
        else:
            self.repeat_request_num += 1
            logger.info("发现重复的请求：<{} {}>".format(request.method, request.url))
            return False

    def _gen_fp(self, request):
        """生成并返回request对象的指纹
        用来判断请求是否重复的属性：url，method，params(在url中)，data
        为保持唯一性，需要对他们按照同样的排序规则进行排序
        """
        # 1. url排序：借助w3lib.url模块中的canonicalize_url方法
        url = w3lib.url.canonicalize_url(request.url)
        # 2. method不需要排序，只要保持大小写一致就可以 upper()方法全部转换为大写
        method = request.method.upper()
        # 3. data排序：如果有提供则是一个字典，如果没有则是空字典
        data = request.data if request.data is not None else {}
        data = sorted(data.items(), key=lambda x: x[0])  # 用sorted()方法 按data字典的key进行排序
        # items()返回元祖 key参数表示按什么进行排序 x表示data.items() x[0]表示元祖第一个值,也就是data的键

        # 4. 利用sha1计算获取指纹
        s1 = sha1()
        s1.update(self._to_bytes(url))  # sha1计算的对象必须是字节类型
        s1.update(self._to_bytes(method))
        s1.update(self._to_bytes(str(data)))

        fp = s1.hexdigest()
        return fp

    def _to_bytes(self, string):
        """为了兼容py2和py3，利用_to_bytes方法，把所有的字符串转化为字节类型"""
        if six.PY2:
            if isinstance(string, str):
                return string
            else:  # 如果是python2的unicode类型，转化为字节类型
                return string.encode('utf-8')
        elif six.PY3:
            if isinstance(string, str):  # 如果是python3的str类型，转化为字节类型
                return string.encode("utf-8")
            else:
                return string
# scrapy_plus/core/engine.py
'''引擎组件'''
import importlib
from multiprocessing.dummy import Pool # 导入线程池对象 # 此处新增

import time # 此处新增
from datetime import datetime
from utils.log import logger    # 导入logger
from  nhttp.request import Request    # 导入Request对象
from multiprocessing.dummy import Pool # 导入线程池对象 # 此处新增
from .scheduler import Scheduler
from .downloader import Downloader
from .pipeline import Pipeline
from .spider import Spider
from utils.stats_collector import NormalStatsCollector,ReidsStatsCollector
from middlewares.spider_middlewares import SpiderMiddleware
from middlewares.downloader_middlewares import DownloaderMiddleware
from conf.settings import SPIDERS, SCHEDULER_PERSIST,PIPELINES, SPIDER_MIDDLEWARES, DOWNLOADER_MIDDLEWARES, MAX_ASYNC_THREAD_NUMBER,ASYNC_TYPE
# 判断使用什么异步模式，改用对应的异步池
if ASYNC_TYPE == 'thread':
    from multiprocessing.dummy import Pool  # 导入线程池对象
elif ASYNC_TYPE == 'coroutine':
    from async1.coroutine import Pool # 导入协程池对象
else:
    raise Exception("不支持的异步类型：{}, 只能是'thread'或者'coroutine'".format(ASYNC_TYPE))


class Engine(object):
    '''
    a. 对外提供整个的程序的入口
    b. 依次调用其他组件对外提供的接口，实现整个框架的运作(驱动)
    '''

    def __init__(self,spiders,pipelines=[]):
        # self.spider = spiders    # 接收爬虫对象

        self.spiders = self._auto_import_instances(SPIDERS, isspider=True)  # 接收爬虫字典 # 此处修改

        if SCHEDULER_PERSIST:
            self.collector = ReidsStatsCollector()  # 新增
        else:
            self.collector = NormalStatsCollector()  # 新增
        self.scheduler = Scheduler(self.collector)
        self.downloader = Downloader()    # 初始化下载器对象
        # self.pipelines = pipelines  # 此处修改   # 初始化管道对象
        #
        # self.spider_mid = SpiderMiddleware()  # 初始化爬虫中间件对象
        # self.downloader_mid = DownloaderMiddleware()  # 初始化下载器中间件对象 # 此处新增
        self.pipelines = self._auto_import_instances(PIPELINES)  # 管道
        self.spider_mids = self._auto_import_instances(SPIDER_MIDDLEWARES)  # 爬虫中间件
        self.downloader_mids = self._auto_import_instances(DOWNLOADER_MIDDLEWARES)  # 下载中间件
        self.total_request_nums = 0
        self.total_response_nums = 0
        # 此处新增
        self.pool = Pool()
        self.is_running = False  # 判断程序是否需要结束的标志
    # 此处新增函数
    def _auto_import_instances(self, path=[], isspider=False):
        '''通过配置文件，动态导入类并实例化
        path: 表示配置文件中配置的导入类的路径
        isspider: 由于爬虫需要返回的是一个字典，因此对其做对应的判断和处理
        '''
        instances = {} if isspider else []
        for p in path:
            module_name = p.rsplit(".", 1)[0]  # 取出模块名称
            cls_name = p.rsplit(".", 1)[1]  # 取出类名称
            ret = importlib.import_module(module_name)  # 动态导入爬虫模块
            cls = getattr(ret, cls_name)  # 根据类名称获取类对象

            if isspider:
                instances[cls.name] = cls()  # 组装成爬虫字典{spider_name:spider(),}
            else:
                instances.append(cls())  # 实例化类对象
                # 把管道中间件分别组装成 管道列表=[管道类1(),管道类2()] / 中间件列表 = [中间件类1(),中间件类2()]
        return instances  # 返回类对象字典或列表


    def start(self):
        # '''启动整个引擎'''
        # start_time  = datetime.now()  # 起始时间
        # logger.info("开始运行时间：%s" % start_time)  # 使用日志记录起始运行时间
        # self._start_engine()
        # stop = datetime.now()  # 结束时间
        # end_time = datetime.now()
        # logger.info("爬虫结束：{}".format(end_time))
        # logger.info("爬虫一共运行：{}秒".format((end_time - start_time).total_seconds()))
        # logger.info("总的请求数量:{}".format(self.total_request_nums))
        # logger.info("总的响应数量:{}".format(self.total_response_nums))
        # # logger.info("开始运行时间：%s" % stop)  # 使用日志记录结束运行时间
        # # logger.info("耗时：%.2f" % (stop - start).total_seconds())  # 使用日志记录运行耗时
        '''启动整个引擎'''
        t_start = datetime.now()
        logger.info("爬虫开始启动：{}".format(t_start))
        logger.info("爬虫运行模式：{}".format(ASYNC_TYPE))
        logger.info("最大并发数：{}".format(MAX_ASYNC_THREAD_NUMBER))
        logger.info("启动的爬虫有：{}".format(list(self.spiders.keys())))
        logger.info("启动的下载中间件有：\n{}".format(DOWNLOADER_MIDDLEWARES))
        logger.info("启动的爬虫中间件有：\n{}".format(SPIDER_MIDDLEWARES))
        logger.info("启动的管道有：\n{}".format(PIPELINES))
        self._start_engine()
        t_end = datetime.now()
        logger.info("爬虫结束：{}".format(t_end))
        logger.info("耗时：%s" % (t_end - t_start).total_seconds())
        # logger.info("一共获取了请求：{}个".format(self.total_request_nums))
        # logger.info("重复的请求：{}个".format(self.scheduler.repeate_request_num))
        # logger.info("成功的请求：{}个".format(self.total_response_nums))
        logger.info("一共获取了请求：{}个".format(self.collector.request_nums))
        logger.info("重复的请求：{}个".format(self.collector.repeat_request_nums))
        logger.info("成功的请求：{}个".format(self.collector.response_nums))
        self.collector.clear()  # 清除redis中所有的计数的值,但不清除指纹集合 # 修改
    # 此处新增
    def _start_request(self):
        # 1. 爬虫模块发出初始请求
        for spider_name, spider in self.spiders.items():  # 此处新增
            for start_request in self.spider.start_requests():
                #1. 对start_request经过爬虫中间件进行处理
                start_request = self.spider_mid.process_request(start_request)


                # 此处新增
                # 为请求对象绑定它所属的爬虫的名称
                start_request.spider_name = spider_name
                #2. 调用调度器的add_request方法，添加request对象到调度器中
                self.scheduler.add_request(start_request)
                #请求数+1
                self.total_request_nums += 1
            # 此处新增

    def _execute_request_response_item(self):
        # 3. 调用调度器的get_request方法，获取request对象
        request = self.scheduler.get_request()
        if request is None:  # 如果没有获取到请求对象，直接返回
            return

        # request对象经过下载器中间件的process_request进行处理
        request = self.downloader_mid.process_request(request)

        # 4. 调用下载器的get_response方法，获取响应
        response = self.downloader.get_response(request)

        # 此处新增
        response.meta = request.meta

        # response对象经过下载器中间件的process_response进行处理
        response = self.downloader_mid.process_response(response)
        # response对象经过下爬虫中间件的process_response进行处理
        response = self.spider_mid.process_response(response)
        spider = self.spider[request.spider_name]
        # 此处新增
        # parse方法
        parse = getattr(spider, request.parse)  # getattr(类, 类中方法名的字符串) = 类方法对象
        # 5. 调用爬虫的parse方法，处理响应

        results = parse(response)
        # 增加一个判断！
        if results is not None:  # 如果项目中爬虫的解析函数不返回可迭代对象就会报错
            for result in parse(response):
                # 6.判断结果的类型，如果是request，重新调用调度器的add_request方法
                if isinstance(result, Request):
                    # 在解析函数得到request对象之后，使用process_request进行处理
                    result = self.spider_mid.process_request(result)

                    # 此处新增
                    # 给request对象增加一个spider_name属性
                    result.spider_name = request.spider_name
                    self.scheduler.add_request(result)
                    self.total_request_nums += 1
                # 7如果不是，调用pipeline的process_item方法处理结果
                else:
                    # self.pipeline.process_item(result)
                    # 此处修改
                    # 就通过process_item()传递数据给管道
                    for pipeline in self.pipelines:
                        pipeline.process_item(result, spider)

            self.total_response_nums += 1



    # 此处修改
    def _start_engine(self):
        '''
        具体的实现引擎的细节
        :return:
        '''

        self.is_running = True  # 启动引擎，设置状态为True
        self.pool.apply_async(self._start_request, error_callback=self._error_callback)  # 使用异步线程池中的线程执行指定的函数

        # 不断的处理解析过程中产生的request
        self.pool.apply_async(self._execute_request_response_item, callback=self._call_back,error_callback=self._error_callback)
        # 此处新增
        logger.info("重复的请求数量:{}".format(self.scheduler.repeate_request_num))
        # 不断的处理解析过程中产生的request
        for i in range(MAX_ASYNC_THREAD_NUMBER):  # 控制最大并发数
            self.pool.apply_async(self._execute_request_response_item, callback=self._call_back,
                                  error_callback=self._error_callback)  # 此处修改

        self._start_request()

        while True:
            time.sleep(0.001)
            self._execute_request_response_item()

            # # 程序退出条件
            # if self.total_response_nums>= self.total_request_nums:
            #     break
            # 此处修改
            # 成功的响应数+重复的数量>=总的请求数量 程序结束
            if self.total_response_nums != 0:  # 因为异步，需要增加判断，响应数不能为0
                if self.total_response_nums + self.scheduler.repeat_request_num >= self.total_request_nums:
                    self.is_running = False  # 此时引擎状态为False
                    break

        # 此处新增

    def _error_callback(self, exception):
        """异常回调函数"""
        try:
            raise exception  # 抛出异常后，才能被日志进行完整记录下来
        except Exception as e:
            logger.exception(e)

    # 此处新增
    def _call_back(self, temp): # 这是异步线程池的callback参数指向的函数,temp参数为固定写法
        if self.is_running:
            self.pool.apply_async(self._execute_request_response_item, callback=self._call_back)
    # def _start_engine(self):
    #     '''依次调用其他组件对外提供的接口，实现整个框架的运作(驱动)'''
    #     # 1. 爬虫模块发出初始请求
    #     start_request = self.spider.start_requests()
    #
    #     # 2. 把初始请求添加给调度器
    #     # 利用爬虫中间件预处理请求对象
    #     start_request = self.spider_mid.process_request(start_request)
    #     self.scheduler.add_request(start_request)
    #     # 3. 从调度器获取请求对象，交给下载器发起请求，获取一个响应对象
    #     request = self.scheduler.get_request()
    #     # 利用下载器中间件预处理请求对象
    #     request = self.downloader_mid.process_request(request)
    #
    #     # 4. 利用下载器发起请求
    #     response = self.downloader.get_response(request)
    #     # 利用下载器中间件预处理响应对象
    #     response = self.downloader_mid.process_response(response)
    #     # 5. 利用爬虫的解析响应的方法，处理响应，得到结果
    #     result = self.spider.parse(response)
    #     # 6. 判断结果对象
    #     # 6.1 如果是请求对象，那么就再交给调度器
    #     if isinstance(result, Request):
    #         # 此处新增
    #         # 利用爬虫中间件预处理请求对象
    #         result = self.spider_mid.process_request(result)
    #         self.scheduler.add_request(result)
    #     # 6.2 否则，就交给管道处理
    #     else:
    #         self.pipeline.process_item(result)
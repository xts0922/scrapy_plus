# project_dir/main.py
# from core.engine import Engine    # 导入引擎
#
# from .spiders.baidu import BaiduSpider
# from .spiders.douban import DoubanSpider
# from .pipelines import BaiduPipeline, DoubanPipeline
# # 此处新增
# from .spider_middlewares import TestDownloaderMiddleware1, TestDownloaderMiddleware2
# from .downloader_middlewares import TestSpiderMiddleware1, TestSpiderMiddleware2
# if __name__ == '__main__':
#     baidu_spider = BaiduSpider()    # 实例化爬虫对象
#     douban_spider = DoubanSpider()    # 实例化爬虫对象
#     spiders = {BaiduSpider.name: baidu_spider, DoubanSpider.name: douban_spider}
#     pipelines = [BaiduPipeline(), DoubanPipeline()]  # 管道们
#     spider_mids = [TestSpiderMiddleware1(), TestSpiderMiddleware2()]  # 多个爬虫中间件
#     downloader_mids = [TestDownloaderMiddleware1(), TestDownloaderMiddleware2()]  # 多个下载中间件
#     # engine = Engine(spiders)    # 传入爬虫对象
#     engine = Engine(spiders, pipelines=pipelines,
#                     spider_mids=spider_mids, downloader_mids=downloader_mids)    # 传入爬虫对象
#     engine.start()    # 启动引擎

# project_dir/main.py
from  core.engine import Engine    # 导入引擎

if __name__ == '__main__':
    engine = Engine()  # 创建引擎对象
    engine.start()    # 启动引擎
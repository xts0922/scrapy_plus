# scrapy_plus/conf/settings
from .default_settings import *    # 全部导入默认配置文件的属性
# 这里导入的settings，是项目文件夹的settings文件
from .settings import *


# 增加以下信息：
# 启用的爬虫类
SPIDERS = [
    'spiders.baidu.BaiduSpider',
    'spiders.douban.DoubanSpider'
]

# 启用的管道类
PIPELINES = [
    'pipelines.BaiduPipeline',
    'pipelines.DoubanPipeline'
]

# 启用的爬虫中间件类
SPIDER_MIDDLEWARES = []

# 启用的下载器中间件类
DOWNLOADER_MIDDLEWARES = []
# coding: utf-8

"""
基类，添加公共的功能，数据库连接，日志处理等
可以连接异步数据库
"""

from datetime import datetime
from ax_spider import Spider
from aioredis import Redis
from typing import Optional


class CurrencySpider(Spider):

    def __init__(self, crawler):
        super().__init__(crawler)
        self.server: Optional[Redis] = None

    @classmethod
    def from_crawler(cls, crawler):
        crawler.state.set_value('start_time', datetime.now().strftime('%F %T.%f'))
        crawler.register(lambda: crawler.state.set_value('end_time', datetime.now().strftime('%F %T.%f')))
        spider = cls(crawler)
        crawler.loop.run_until_complete(spider.db_connect())
        crawler.register(spider.db_close)
        return spider

    # 连接数据库
    async def db_connect(self):
        self.server = Redis(socket_connect_timeout=2, decode_responses=True)
        await self.server.ping()

    # 关闭数据库
    async def db_close(self):
        await self.server.close()

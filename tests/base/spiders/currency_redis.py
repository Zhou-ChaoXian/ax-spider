# coding: utf-8

"""
通过redis获取任务
"""

import asyncio
from typing import AsyncGenerator
from .currency import CurrencySpider


class CurrencyRedisSpider(CurrencySpider):
    redis_key = None

    def __init__(self, crawler):
        super().__init__(crawler)
        self.monitored_seconds = self.setting.get_int('MONITORED_SECONDS', 60)
        self.use_seconds = 0

    @classmethod
    def from_crawler(cls, crawler):
        spider = super().from_crawler(crawler)
        spider.redis_key = 'ax_spider:' + spider.redis_key
        return spider

    def __init_subclass__(cls, **kwargs):
        if cls.redis_key is None:
            raise KeyError('please set subclass redis_key attribute')
        if cls.make_request_from_data is getattr(cls.__base__, 'make_request_from_data'):
            raise NotImplementedError('please overload subclass make_request_from_data method')

    async def __call__(self, *args, **kwargs):
        self.logger.info(f'redis_key -> {self.redis_key}')
        self.crawler.signal_handler.connect(self.add_generator, self.crawler.signals.spider_idle)

    async def add_generator(self):
        while True:
            generator = await self.next_generator()
            if generator is not None:
                if isinstance(generator, AsyncGenerator):
                    self.crawler.engine.add_generator(generator)
                else:
                    await generator
                self.use_seconds = 0
                break
            else:
                await asyncio.sleep(5)
                self.use_seconds += 5
                if self.use_seconds > self.monitored_seconds:
                    self.crawler.close()

    async def make_request_from_data(self, data):
        raise NotImplementedError

    async def next_generator(self):
        async with self.server.client() as conn:
            data = await conn.lpop(self.redis_key)
            if data is not None:
                return self.make_request_from_data(data)

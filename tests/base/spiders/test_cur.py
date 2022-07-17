# coding: utf-8

from ax_spider import Request
from .currency import CurrencySpider


class TestCurSpider(CurrencySpider, coroutine_num=1, max_depth=0):

    async def __call__(self, *args, **kwargs):
        self.logger.info(self.options)

    async def parse(self, response):
        pass

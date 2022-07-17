# coding: utf-8

from ax_spider import Request
from ax_spider.basics.no_http import MockTransport
from .currency_redis import CurrencyRedisSpider


class TestCurRedisSpider(CurrencyRedisSpider, coroutine_num=1, max_depth=0):
    redis_key = 'test'

    async def make_request_from_data(self, data):
        self.logger.info(data)
        yield Request(url='http://localhost', transport=MockTransport())

    async def parse(self, response):
        self.logger.info(response.text)

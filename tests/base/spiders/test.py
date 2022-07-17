# coding: utf-8

from httpx import Timeout
from ax_spider import Spider, Request
from ax_spider.basics.no_http import MockTransport
from ..item import BaseItem


class TestSpider(Spider, coroutine_num=1, max_depth=0):

    async def __call__(self, *args, **kwargs):
        yield Request(url='http://localhost/', transport=MockTransport())

    async def parse(self, response):
        self.logger.info(response.text)
        yield Request(url='http://localhost/', transport=MockTransport(), callback=self.other_parse)
        yield Request(url='http://localhost/', timeout=Timeout(None, connect=1), callback=self.other_parse)

    async def other_parse(self, response):
        self.logger.info(f'other_parse {response.text}')
        yield BaseItem('hello')

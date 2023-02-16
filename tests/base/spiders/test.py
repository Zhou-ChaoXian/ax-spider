# coding: utf-8

import httpx
from ax_spider import Spider, Request, Response
from ax_spider.basics.no_http import MockTransport
from ..item import BaseItem


class Stream(httpx.AsyncByteStream):

    async def __aiter__(self):
        yield b'hello\r\n'
        yield b'world'


class Transport(httpx.AsyncBaseTransport):

    async def handle_async_request(self, request: Request):
        return Response(200, stream=Stream())


class TestSpider(Spider, coroutine_num=3, max_depth=0):

    async def __call__(self, *args, **kwargs):
        yield Request(url='http://localhost/', transport=Transport(), stream_model=True)

    async def parse(self, response):
        async for i in response.aiter_raw():
            self.logger.info('%s %s', i, '---')
        await response.close_default_client()

        # yield Request(url='http://localhost/', transport=MockTransport(), callback=self.other_parse)
        # yield Request(url='http://localhost/', timeout=Timeout(None, connect=1), callback=self.other_parse)

    async def other_parse(self, response):
        self.logger.info(f'other_parse {response.text}')
        yield BaseItem('hello')

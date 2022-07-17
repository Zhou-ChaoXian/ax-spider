# coding: utf-8

import httpx
from .http import Request, Response

__all__ = ['no_response', 'MockTransport']


class MockTransport(httpx.AsyncBaseTransport):

    async def handle_async_request(self, request: Request) -> Response:
        return Response(200, text='no_content')


async def no_response(callback) -> Response:
    request = Request(url='http://localhost/', transport=MockTransport(), callback=callback)
    return await request.send()

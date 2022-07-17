# coding: utf-8


class BaseMiddleware(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = self.crawler.spider.logger

    async def process_request(self, request):
        self.logger.info('before request')
        return request

    async def process_exception(self, request, exception):
        self.logger.error(repr(exception))
        info = f'\n{request.url}\n{request.headers}'
        self.logger.error(info)

    async def process_response(self, response):
        self.logger.info('after request')
        return response

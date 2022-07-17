# coding: utf-8


class BasePipeline(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = self.crawler.spider.logger

    async def process_item(self, item, response):
        self.logger.info(item)
        return item

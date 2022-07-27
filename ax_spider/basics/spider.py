# coding: utf-8

import logging
from typing import final
from .http import Response
from .protect import protect
from ..core.crawler import Crawler
from ..__version__ import __title__

__all__ = ['Spider']


class Spider(metaclass=protect('no_parse')):
    custom_settings = {}

    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        self.loop = crawler.loop
        self.setting = crawler.setting
        self.options = crawler.options
        self._logger = logging.getLogger(__title__)

    async def __call__(self, *args, **kwargs):
        pass

    async def parse(self, response: Response):
        pass

    @final
    async def no_parse(self, response: Response):
        pass

    @property
    def logger(self):
        return self._logger

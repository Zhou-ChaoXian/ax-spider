# coding: utf-8

import pprint
from typing import Optional
from collections import deque
from importlib import import_module
from asyncio.base_events import BaseEventLoop
from asyncio import iscoroutinefunction
from ..settings import Settings
from ..basics.others import load_object
from .signal_handler import SignalHandler
from . import signals
from .engine import Engine, ExitException
from .state import StateCollector
from .log import DefaultLogger

__all__ = ['Crawler']


class Crawler(object):

    def __init__(self):
        self.setting: Optional[Settings] = None
        self.loop: Optional[BaseEventLoop] = None
        self.signal_handler = SignalHandler()
        self.signals = signals
        self.state = StateCollector()
        self.options: Optional[dict] = None
        self.engine: Optional[Engine] = None
        self._spider = None
        self._exit_func = deque()
        self.register(self._log_state_info)

    @classmethod
    def from_crawler(cls, loop, options):
        crawler = cls()
        crawler.loop = loop
        crawler.options = options
        path = options['path']
        setting_path = path.split('.', 1)[0] + '.setting'
        crawler.setting = Settings(import_module(setting_path))
        class_name = path.rsplit('.', 1)[-1].title().replace('_', '') + 'Spider'
        spider_class = load_object(f'{path}.{class_name}')
        crawler.setting.set_dict(spider_class.custom_settings)
        crawler.instance_from_class(DefaultLogger).set_logger()
        crawler._spider = crawler.instance_from_class(spider_class)
        crawler.engine = crawler.instance_from_class(Engine)
        crawler._basics_signal_func()
        return crawler

    spider = property(lambda self: self._spider)

    async def start_crawler(self):
        try:
            await self.signal_handler.send(self.signals.spider_opened)
            await self.engine.start()
        finally:
            await self.signal_handler.send(self.signals.spider_closed)

    async def end_crawler(self):
        for func in self._exit_func:
            try:
                if iscoroutinefunction(func):
                    await func()
                else:
                    func()
            except Exception as e:
                self.spider.logger.exception(e)

    def register(self, func):
        self._exit_func.appendleft(func)
        return func

    def unregister(self, func):
        self._exit_func.remove(func)

    def instance_from_path(self, path):
        obj = load_object(path)
        return self.instance_from_class(obj)

    def instance_from_class(self, obj):
        if hasattr(obj, 'from_crawler'):
            ins = obj.from_crawler(self)
        else:
            ins = obj(self)
        return ins

    def close(self):
        raise ExitException

    def _log_state_info(self):
        width = self.setting.get('PPRINT_WIDTH')
        depth = self.setting.get('PPRINT_DEPTH')
        sort_dicts = self.setting.get('PPRINT_SORT_DICTS')
        state_data = pprint.pformat(self.state.all_value, width=width, depth=depth, sort_dicts=sort_dicts)
        self.spider.logger.info('\n%s', state_data)

    def _basics_signal_func(self):
        self.signal_handler.connect(
            lambda _: self.state.inc_value('request_received'),
            self.signals.request_received
        )
        self.signal_handler.connect(
            lambda _, __: self.state.inc_value('request_error'),
            self.signals.request_error
        )
        self.signal_handler.connect(
            lambda _, __: self.state.inc_value('item_received'),
            self.signals.item_received
        )

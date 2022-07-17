# coding: utf-8

from typing import Optional
from inspect import isasyncgen
from functools import wraps
from collections import deque, defaultdict
from .pool import Pool
from .item import is_item
from ..basics.http import Request, Response
from ..basics.no_http import no_response

__all__ = ['Engine', 'ExitException']


class ExitException(Exception):
    pass


def exception_manager(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        engine = args[0]
        try:
            return await func(*args, **kwargs)
        except ExitException:
            if not engine.exit_flag:
                engine.pool.clear()
                engine.exit_flag = True
        except Exception as e:
            engine.crawler.state.inc_value('logical_error')
            engine.crawler.spider.logger.exception(e)

    return inner


class Engine(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.setting = crawler.setting
        self.handlers = defaultdict(deque)
        self.current_depth = []
        self.max_depth = self.setting.get_int('MAX_DEPTH')
        self.generator_data = defaultdict(deque)
        self.coroutine_num = self.setting.get_int('COROUTINE_NUM')
        self.pool = Pool(self.coroutine_num)
        self.no_resp = self.crawler.loop.run_until_complete(no_response(self.crawler.spider.no_parse))
        self.exit_flag = False

    @classmethod
    def from_crawler(cls, crawler):
        engine = cls(crawler)
        setting = crawler.setting
        engine.set_middleware(setting.get_dict('MIDDLEWARES'))
        engine.set_pipeline(setting.get_dict('PIPELINES'))
        engine.set_extension(setting.get_dict('EXTENSIONS'))
        return engine

    def set_middleware(self, middlewares):
        for path, _ in sorted(middlewares.items(), key=lambda x: x[1]):
            ins = self.crawler.instance_from_path(path)
            if process_request := getattr(ins, 'process_request', None):
                self.handlers['process_request'].append(process_request)
            if process_exception := getattr(ins, 'process_exception', None):
                self.handlers['process_exception'].appendleft(process_exception)
            if process_response := getattr(ins, 'process_response', None):
                self.handlers['process_response'].appendleft(process_response)

    def set_pipeline(self, pipelines):
        for path, _ in sorted(pipelines.items(), key=lambda x: x[1]):
            ins = self.crawler.instance_from_path(path)
            if process_item := getattr(ins, 'process_item', None):
                self.handlers['process_item'].append(process_item)

    def set_extension(self, extensions):
        for path in extensions.keys():
            self.crawler.instance_from_path(path)

    async def process_extension(self, signal, *args, **kwargs):
        await self.crawler.signal_handler.send(signal, *args, **kwargs)

    async def process_request(self, request):
        await self.process_extension(self.crawler.signals.request_received, request)
        for handler in self.handlers['process_request']:
            request = await handler(request)
            if not isinstance(request, Request):
                return
        return request

    async def process_exception(self, request, exception):
        await self.process_extension(self.crawler.signals.request_error, request, exception)
        for handler in self.handlers['process_exception']:
            result = await handler(request, exception)
            if isinstance(result, Request):
                return result
            elif isinstance(result, Exception):
                continue
            else:
                return
        return exception

    async def process_response(self, response):
        await self.process_extension(self.crawler.signals.response_received, response)
        for handler in self.handlers['process_response']:
            response = await handler(response)
            if isinstance(response, Response):
                continue
            elif isinstance(response, Request):
                return response
            else:
                return
        return response

    @exception_manager
    async def process_item(self, item, response):
        if self.exit_flag:
            return
        await self.process_extension(self.crawler.signals.item_received, item, response)
        for handler in self.handlers['process_item']:
            item = await handler(item, response)
            if item is None:
                return

    @exception_manager
    async def process(self, request, depth):
        if self.exit_flag:
            return
        req = await self.process_request(request)
        if req is not None:
            resp = await req.send()
            if resp is None:
                await self.handler_exception(req, depth)
            else:
                resp = await self.process_response(resp)
                if resp is not None:
                    await self.handler_response(resp, depth)

    async def handler_exception(self, request, depth):
        result = await self.process_exception(request, request.exception)
        if result is not None:
            if isinstance(result, Exception):
                self.crawler.spider.logger.error(repr(result))
            else:
                self.handler_retry_request(result, depth)

    def handler_retry_request(self, request, depth):
        async def wrapper_request(request_instance):
            yield request_instance

        if len(self.current_depth) == 0 or depth > self.current_depth[-1]:
            self.current_depth.append(depth)
        self.generator_data[depth].appendleft((wrapper_request(request), ''))

    async def handler_response(self, response, depth):
        if isinstance(response, Request):
            self.handler_retry_request(response, depth)
        else:
            callback = response.request.callback
            if callback is None:
                callback = self.crawler.spider.parse
            gen = callback(response)
            if isasyncgen(gen):
                self.append_generator(gen, depth, response)
            else:
                await gen

    def append_generator(self, gen, depth, response):
        next_depth = depth + 1
        if 0 < self.max_depth < next_depth:
            return
        if len(self.current_depth) == 0 or next_depth > self.current_depth[-1]:
            self.current_depth.append(next_depth)
        self.generator_data[next_depth].append((gen, response))

    async def add_task(self, depth, dq):
        for _ in range(self.coroutine_num):
            if len(dq) == 0:
                self.current_depth.remove(depth)
                return
            else:
                try:
                    gen, response = dq[0]
                    task = await gen.asend(None)
                except ExitException:
                    self.exit_flag = True
                    return
                except StopAsyncIteration:
                    dq.popleft()
                except Exception as e:
                    self.crawler.state.inc_value('logical_error')
                    self.crawler.spider.logger.exception(e)
                    dq.popleft()
                else:
                    if self.exit_flag:
                        return
                    if isinstance(task, Request):
                        self.pool.add_coroutine(self.process(task, depth))
                    elif is_item(task):
                        self.pool.add_coroutine(self.process_item(task, response))

    def add_request(self, request, depth: Optional[int] = None):
        if depth is None:
            depth = self.current_depth[-1] if len(self.current_depth) > 1 else 1
        self.pool.add_coroutine(self.process(request, depth))

    def add_item(self, item, response: Optional[Response] = None):
        if response is None:
            response = self.no_resp
        self.pool.add_coroutine(self.process_item(item, response))

    def add_coroutine(self, coroutine, *callbacks):
        self.pool.add_coroutine(coroutine, *callbacks)

    def add_generator(self, generator, depth=1, response: Optional[Response] = None):
        if not isasyncgen(generator):
            generator.close()
            return
        if len(self.current_depth) == 0 or depth > self.current_depth[-1]:
            self.current_depth.append(depth)
        if response is None:
            response = self.no_resp
        self.generator_data[depth].append((generator, response))

    async def start(self):
        first_gen = self.crawler.spider()
        if isasyncgen(first_gen):
            self.current_depth.append(1)
            self.generator_data[1].append((first_gen, self.no_resp))
        else:
            await first_gen
        while True:
            while len(self.current_depth) > 0:
                depth = self.current_depth[-1]
                dq = self.generator_data[depth]
                await self.add_task(depth, dq)
                if self.exit_flag:
                    return
                await self.pool.wait_available()
            if self.exit_flag:
                return
            if not await self.pool.wait_one():
                await self.process_extension(self.crawler.signals.spider_idle)
                if len(self.current_depth) == 0 and self.pool.empty():
                    return

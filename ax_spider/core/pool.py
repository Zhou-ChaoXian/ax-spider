# coding: utf-8

import asyncio
from collections import deque
from contextlib import suppress

__all__ = ['Pool']


class Pool(object):

    def __init__(self, size=1):
        self._size = size
        self._future_num = 0
        self._dq = deque()
        self._fs = set()

    def add_coroutine(self, coroutine_func, *callbacks):

        def done_callback(fut):
            self._future_num -= 1
            self._fs.remove(fut)
            with suppress(IndexError):
                self.add_coroutine(*self._dq.popleft())

        if self._future_num < self._size:
            future = asyncio.ensure_future(coroutine_func)
            self._future_num += 1
            self._fs.add(future)
            for cb in callbacks:
                future.add_done_callback(cb)
            future.add_done_callback(done_callback)
        else:
            self._dq.append((coroutine_func, *callbacks))

    def full(self):
        return self._future_num == self._size

    def empty(self):
        return self._future_num == 0

    def clear(self):
        for task in self._fs:
            task.cancel()
        for coroutine, *_ in self._dq:
            coroutine.close()
        self._dq.clear()

    async def join(self):
        while self._future_num > 0:
            await asyncio.wait(self._fs, return_when=asyncio.FIRST_COMPLETED)

    async def wait_available(self):
        while self._future_num == self._size:
            await asyncio.wait(self._fs, return_when=asyncio.FIRST_COMPLETED)

    async def wait_one(self):
        if self._future_num == 0:
            return False
        else:
            await asyncio.wait(self._fs, return_when=asyncio.FIRST_COMPLETED)
            return True

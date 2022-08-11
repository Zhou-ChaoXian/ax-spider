# coding: utf-8

from collections import deque
from asyncio import ensure_future

__all__ = ['Pool']


class Pool(object):

    def __init__(self, size, loop):
        self._size = size
        self._future_num = 0
        self._dq = deque()
        self._fs = set()
        self._loop = loop

    def add_coroutine(self, coroutine, *callbacks):

        def done_callback(fut):
            self._future_num -= 1
            self._fs.remove(fut)
            if len(self._dq) > 0:
                self.add_coroutine(*self._dq.popleft())

        if self._future_num < self._size:
            future = ensure_future(coroutine)
            self._future_num += 1
            self._fs.add(future)
            for cb in callbacks:
                future.add_done_callback(cb)
            future.add_done_callback(done_callback)
        else:
            self._dq.append((coroutine, *callbacks))

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
            await self._wait()

    async def wait_available(self):
        while self._future_num == self._size:
            await self._wait()

    async def wait_one(self):
        if self._future_num == 0:
            return False
        else:
            await self._wait()
            return True

    async def _wait(self):
        fs = self._fs.copy()
        waiter = self._loop.create_future()

        def _on_completion(_):
            if not waiter.done():
                waiter.set_result(None)

        for f in fs:
            f.add_done_callback(_on_completion)
        try:
            await waiter
        finally:
            for f in fs:
                f.remove_done_callback(_on_completion)

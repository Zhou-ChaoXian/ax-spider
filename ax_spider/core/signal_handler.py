# coding: utf-8

from asyncio import iscoroutinefunction
from pydispatch import dispatcher
from pydispatch.dispatcher import liveReceivers, getAllReceivers

__all__ = ['SignalHandler']


class SignalHandler(object):

    def __init__(self):
        self.sender = dispatcher.Anonymous

    def connect(self, receiver, signal, weak=False):
        return dispatcher.connect(receiver, signal, self.sender, weak)

    def disconnect(self, receiver, signal, weak=False):
        return dispatcher.disconnect(receiver, signal, self.sender, weak)

    def disconnect_all(self, signal, weak=False):
        for receiver in liveReceivers(getAllReceivers(self.sender, signal)):
            dispatcher.disconnect(receiver, signal, self.sender, weak=weak)

    async def send(self, signal, *args, **kwargs):
        for receiver in liveReceivers(getAllReceivers(self.sender, signal)):
            if iscoroutinefunction(receiver):
                await receiver(*args, **kwargs)
            else:
                receiver(*args, **kwargs)

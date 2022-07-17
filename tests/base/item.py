# coding: utf-8

from ax_spider import Item, Field


@Item()
class BaseItem(object):
    title = Field()

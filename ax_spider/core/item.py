# coding: utf-8

import attr
from functools import partial

__all__ = [
    'Item',
    'Field',
    'is_item',
    'as_dict',
    'as_tuple',
]

Item = partial(attr.attrs, slots=True)
Field = partial(attr.attrib, default=None)
as_dict = attr.asdict
as_tuple = attr.astuple


def is_item(item_info):
    item_class = item_info if isinstance(item_info, type) else item_info.__class__
    return attr.has(item_class)

# coding: utf-8

import copy
import json
from . import default_settings


class BaseSettings(object):

    def __init__(self):
        self.attributes = dict()

    def __getitem__(self, item):
        return self.attributes.get(item)

    def __contains__(self, item):
        return item in self.attributes

    def get(self, name, default=None):
        return value if (value := self[name]) else default

    def get_bool(self, name, default=False):
        got = self.get(name, default)
        if got in ('True', 'true'):
            return True
        if got in ('False', 'false'):
            return False
        return bool(int(got))

    def get_int(self, name, default=0):
        return int(self.get(name, default))

    def get_float(self, name, default=0.0):
        return float(self.get(name, default))

    def get_list(self, name, default=None, sep=','):
        value = self.get(name, default or [])
        if isinstance(value, str):
            value = value.split(sep)
        return list(value)

    def get_dict(self, name, default=None, **kwargs):
        value = self.get(name, default or {})
        if isinstance(value, str):
            value = json.loads(value, **kwargs)
        return dict(value)

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, name, value):
        self.attributes[name] = value

    def set_dict(self, values):
        for key, value in values.items():
            self.set(key, value)

    def set_module(self, module):
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def delete(self, name):
        del self.attributes[name]

    def copy(self):
        return copy.deepcopy(self.attributes)

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)


class Settings(BaseSettings):

    def __init__(self, new_settings=None):
        super(Settings, self).__init__()
        self.set_module(default_settings)
        if new_settings:
            self.set_module(new_settings)

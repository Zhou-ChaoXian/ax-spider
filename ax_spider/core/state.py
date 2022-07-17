# coding: utf-8


class StateCollector(object):

    def __init__(self):
        self._stats = {}

    def get_value(self, key, default=None):
        return self._stats.get(key, default)

    def get_stats(self):
        return self._stats

    def get_keys(self):
        return list(self._stats.keys())

    def set_value(self, key, value):
        self._stats[key] = value

    def set_values(self, dicts):
        self._stats.update(dicts)

    def set_stats(self, stats):
        self._stats = stats

    def inc_value(self, key, count=1, start=0):
        self._stats.setdefault(key, start)
        self._stats[key] += count

    def dec_value(self, key, count=1, start=0):
        self._stats.setdefault(key, start)
        self._stats[key] -= count

    def clear_stats(self):
        self._stats.clear()

    @property
    def all_value(self):
        return self._stats

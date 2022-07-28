# coding: utf-8

from importlib import import_module


def load_object(path):
    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError(f"Error loading object '{path}': not a full path")
    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)
    try:
        obj_info = getattr(mod, name)
    except AttributeError:
        raise NameError(f"Module '{module}' doesn't define any object named '{name}'")
    return obj_info


def indent(text: str, prefix='+'):
    def prefixed():
        count = 1
        for i in text.splitlines(True):
            yield f'{prefix}{count} {i}'
            count += 1

    return ''.join(prefixed())


class Pipe(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, key=None):
        if key is None:
            return Pipe(lambda x: self.func(x))
        else:
            return Pipe(lambda x: self.func(x, key))

    def __ror__(self, other):
        return self.func(other)

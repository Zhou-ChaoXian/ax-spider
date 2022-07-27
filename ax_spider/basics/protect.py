# coding: utf-8


def protect(*protected):
    class ProtectMeta(type):
        _parse_instance = None

        def __new__(mcs, name, bases, namespace, **kwargs):
            namespace.setdefault('custom_settings', {})
            if bases and bases != (object,):
                for i in protected:
                    if (func := namespace.get(i)) and callable(func):
                        raise ProtectError(f'The {i} method cannot be overridden')
                if (coroutine_num := kwargs.get('coroutine_num', 1)) > 1:
                    namespace['custom_settings']['COROUTINE_NUM'] = coroutine_num
                if (max_depth := kwargs.get('max_depth', 0)) > 0:
                    namespace['custom_settings']['MAX_DEPTH'] = max_depth
            return super().__new__(mcs, name, bases, namespace)

        def __call__(cls, *args, **kwargs):
            if cls._parse_instance is None:
                cls._parse_instance = super().__call__(*args, **kwargs)
            return cls._parse_instance

    return ProtectMeta


class ProtectError(Exception):
    pass

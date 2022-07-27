# coding: utf-8

import argparse
from ..core.run import executor


class Command(object):
    short_desc = 'Start parsing spider'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('path', help='spider path')
        parser.add_argument('kws', action=Action, nargs='*', default=[], help='custom parameters')
        parser.add_argument('--selector', action='store_true', default=False, help='selector EventLoop')
        parser.add_argument('--debug', action='store_true', default=False, help='debug')

    @staticmethod
    def run(options):
        data = dict(options.kws)
        data['path'] = options.path
        executor(data, options.selector, options.debug)


class Action(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        data = []
        for i in values:
            if '=' in i:
                data.append(i.split('=', 1))
        setattr(namespace, self.dest, data)

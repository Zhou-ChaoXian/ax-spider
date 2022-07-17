# coding: utf-8

import sys
import argparse
from pathlib import Path
from importlib import import_module
from ..__version__ import __title__, __version__


def run():
    parser = argparse.ArgumentParser(
        prog=__title__,
        usage='%(prog)s <command> [option ...]',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prefix_chars='-/',
        conflict_handler='resolve',
        allow_abbrev=False
    )
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    sub_parser = parser.add_subparsers(title='二级命令', prog=__title__)
    parser_dict = {}
    files = Path(__file__).parent.glob('[!_]*.py')
    module_path = f'{__title__}.commands'
    add_parser(files, module_path, sub_parser, parser_dict)
    sys.path.append(str(Path.cwd()))
    current_commands_path = Path.cwd().joinpath('commands')
    if current_commands_path.exists():
        files = current_commands_path.glob('[!_]*.py')
        add_parser(files, 'commands', sub_parser, parser_dict)
    if info := parser_dict.get(sys.argv[1]):
        command = info[0]()
        command.add_arguments(info[1])
        options, _ = parser.parse_known_args()
        command.run(options)
    else:
        parser.parse_known_args()


def add_parser(files, module_path, sub_parser, parser_dict):
    for file in files:
        file_name = file.stem
        module = import_module(f'{module_path}.{file_name}')
        if obj := getattr(module, 'Command', None):
            parser = sub_parser.add_parser(
                name=file_name,
                usage='%(prog)s [option ...]',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prefix_chars='-/',
                conflict_handler='resolve',
                allow_abbrev=False,
                help=obj.short_desc
            )
            parser_dict[file_name] = (obj, parser)


if __name__ == '__main__':
    run()

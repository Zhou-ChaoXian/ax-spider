# coding: utf-8

import shutil
from pathlib import Path
from string import Template
from ..__version__ import __title__


class Command(object):
    short_desc = '生成解析文件'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('spider_name', help='spider文件名')
        parser.add_argument('spider_folder', nargs='?', default='spiders', help='spider所在的文件夹')
        parser.add_argument('-t', metavar='template', default=None, help='模板路径')

    @staticmethod
    def run(options):
        spider_name = options.spider_name
        spider_folder = options.spider_folder
        template = options.t
        if template is None:
            template_spider_path = Path(__file__).parents[1].joinpath('template/spiders/base_spider.tmpl')
        else:
            template_spider_path = Path.cwd().joinpath(template)
        folder_path = Path.cwd().joinpath(spider_folder)
        if not folder_path.exists():
            folder_path.mkdir(0o755, True)
            init = folder_path.joinpath('__init__.py')
            init.write_text('# coding: utf-8\n', encoding='utf-8')
        spider_path = folder_path.joinpath(f'{spider_name}.py')
        if spider_path.exists():
            y = input('文件已存在，是否替换 (y/n)? ')
            if y.lower() == 'y':
                print('文件已替换')
            else:
                return
        shutil.copy(template_spider_path, spider_path)
        class_name = spider_name.title().replace('_', '')
        txt = spider_path.read_text(encoding='utf-8')
        raw = Template(txt).safe_substitute({'ClassName': class_name, 'module': __title__})
        spider_path.write_text(raw, encoding='utf-8')

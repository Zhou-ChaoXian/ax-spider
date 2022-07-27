# coding: utf-8

import shutil
from pathlib import Path
from string import Template
from ..__version__ import __title__


class Command(object):
    short_desc = 'Create new project'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('project_name', help='project name')
        parser.add_argument('--safe', action='store_true', help='Do not overwrite existing files')

    def run(self, options):
        path = Path(__file__).parents[1]
        self.copy_run(path, options)
        source_dir = path.joinpath('template/project')
        target_dir = Path.cwd().joinpath(options.project_name)
        self.copy_dir(source_dir, target_dir, options)

    @staticmethod
    def copy_run(path, options):
        run = Path.cwd().joinpath('run.py')
        if options.safe and run.exists():
            return
        shutil.copy(path.joinpath('template/run.tmpl'), run)
        raw = Template(run.read_text(encoding='utf-8')).safe_substitute({'module': __title__})
        run.write_text(raw, encoding='utf-8')

    def copy_dir(self, source_dir, target_dir, options):
        if not target_dir.exists():
            target_dir.mkdir(0o755)
        project_info = options.project_name.title().replace('_', '')
        replace_dict = {'ClassName': project_info, 'module': __title__}
        for i in source_dir.iterdir():
            dst = target_dir.joinpath(i.name)
            if i.is_dir():
                self.copy_dir(i, dst, options)
            else:
                dst = dst.with_suffix('.py')
                if options.safe and dst.exists():
                    continue
                shutil.copy(i, dst)
                raw = Template(dst.read_text(encoding='utf-8')).safe_substitute(replace_dict)
                dst.write_text(raw, encoding='utf-8')

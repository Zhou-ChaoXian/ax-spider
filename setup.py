# coding: utf-8

from setuptools import setup, find_packages

data = 'ax_spider'

setup(
    name=data,
    version='0.0.9a0',
    project_urls={
        'Source': 'https://github.com/Zhou-ChaoXian/ax-spider'
    },
    packages=find_packages(include=[f'{data}*']),
    zip_safe=False,
    description=f'一款简单的python爬虫框架',
    author='Zhou-ChaoXian',
    author_email='2542606900@qq.com',
    keywords=data,
    license='GPLv3',
    python_requires='>=3.9',
    install_requires=[
        'httpx >= 0.23.0',
        'attrs',
        'parsel',
        'itemloaders',
        'pathlib',
        'PyDispatcher'
    ],
    platforms='Independant',
    py_modules=[data],
    package_data={
        data: ['template/*', 'template/project/*', 'template/spiders/*']
    },
    classifiers=[
          'Programming Language :: Python :: 3.9',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts': [
            f'{data} = {data}.commands:run',
        ]
    }
)

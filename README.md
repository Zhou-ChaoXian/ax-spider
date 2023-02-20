### ax-spider

> **简介** 一个简单的`python`爬虫框架
>
> **开发** `asyncio` `httpx`
>
> **依赖** `python>=3.9` `httpx>=0.23.0`

***

* [亮点](#亮点)
* [安装](#安装)
* [简单示例](#一起来实现一个简单的示例)
* [命令行](#命令行)
* [请求](#请求操作推荐第一个)
* [存储](#存储操作推荐第一个)
* [中间件](#middleware)
* [管道](#pipeline)
* [信号](#信号)
* [配置](#setting)
* [spider](#spider)
* [添加任务](#添加任务到pool)
* [添加总任务](#添加异步生成器)
* [关闭](#关闭)
* [添加退出函数](#添加退出函数)
* [流模式](#流模式请求数据)

### 亮点

轻量级、依赖少、安装快、运行速度也快、支持异步（有问题直接找`httpx`文档）

[comment]: <> (![]&#40;./谁反对.gif "谁反对"&#41;)

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 安装

`pip install ax-spider`

或者进入<b><font size=5 color=Tomato face="华文彩云">上面源码<font color=Violet><kbd>↑</kbd></font><font color=green>
dist</font></font></b>目录下，里面有 <b><font size=5 color=green face="黑体">whl安装包</font></b> 点击下载，`pip install *.whl`

`ax_spider -v` | `python -m ax_spider -v` 检查版本

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 一起来实现一个简单的示例

<b><font size=5 color=Tomato face="华文彩云">源码tests</font></b>目录下有一个更详细的示例

1. 找一个空闲的文件夹，使用IDE打开


2. 打开终端，进入文件夹路径


3. `python -m ax_spider project test1`  生成项目，项目名为test1


4. `python -m ax_spider spider t1 test1/spiders`  在test1/spiders目录下生成spider文件


5. 编辑t1.py

```python
from ax_spider import Spider, Request


class T1Spider(Spider, coroutine_num=1, max_depth=0):

    async def __call__(self, *args, **kwargs):
        yield Request(url='http://www.baidu.com')

    async def parse(self, response):
        self.logger.info(response.status_code)
```

6. 项目同级目录下有一个run.py，运行文件

```python
from ax_spider import executor

if __name__ == '__main__':
    executor({
        'path': 'test1.spiders.t1',
    })
```

或者 `python -m ax_spider crawl test1.spiders.t1`

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 命令行

***命令前可以加*** `python -m`

`ax_spider -h` 查看帮助信息

***

`ax_spider project -h`

在当前目录下生成项目 `ax_spider project base --safe`

--safe **确保存在的文件不覆盖**

***

`ax_spider spider -h`

生成spider文件，`ax_spider spider test base/spiders -t base/template/base.tmpl`

-t **在当前路径下找要复制的模板，有默认的模板**

***

`ax_spider crawl -h`

运行 `ax_spider crawl base.spiders.test name=james age=37`

**自定义参数用`=`隔开**

***

项目同级目录 run.py ，可以运行

```python
from ax_spider import executor

if __name__ == '__main__':
    executor({
        'path': 'test1.spiders.t1',
        'name': 'james',
        'age': 37
    })
```

***

项目同级目录，如果发现 ***commands*** 文件夹，py文件格式如下，文件名就是命令名

```python
from argparse import ArgumentParser


class Command(object):
    short_desc = ''

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-t', help='')

    def run(self, options):
        pass
```

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 请求操作(推荐<sup>第一个</sup>)

`yield Request(url='http://localhost/')`

`self.crawler.engine.add_request(Request(url='http://localhost/'))`

默认调用 **parse** 方法

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 存储操作(推荐<sup>第一个</sup>)

`yield BaseItem()`

`self.crawler.engine.add_item(BaseItem(), response)`

response可以忽略

自定义`Item`

```python
from ax_spider import Item, Field


@Item()
class BaseItem(object):
    title = Field()
```

使用的`attr`模块，`Item`是`attr.attrs`的别名，`Field`是`attr.attrib`的别名

```python
import attr


@attr.attrs()
class BaseItem(object):
    title = attr.attrib(
        type=str,
        converter=attr.converters.pipe(lambda x: x * 3, lambda x: x[:5]),
        validator=attr.validators.in_(['hello', 'hi'])
    )
```

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### middleware

`process_request(self, request)`

发起请求前调用，返回值有三种类型 <b>[`Request`, `Response`, 其他]</b>

request会调用下一个`process_request`，response会调用`process_response`，其他类型直接舍弃

`process_exception(self, request, exception)`

请求出错调用，返回`request`(重新请求) `exception`(下一个) 其他(停止)

`process_response(self, response)`

请求后调用，返回`request`(重新请求) `response`(下一个) 其他(停止)

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### pipeline

`process_item(self, item, response)`

item处理，返回`item`(下一个) 其他(停止)

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 信号

**可以注册普通函数或异步函数**

`spider_opened` (解析之前)参数 无

`spider_idle` (空闲)参数 无

`spider_closed` (解析完毕)参数 无

`request_received` (收到请求)参数 `request`

`request_error` (请求出错)参数 `request` `exception`

`response_received` (收到响应)参数 `response`

`item_received` (收到item)参数 `item` `response`

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### setting

`COROUTINE_NUM` 协程数量，默认1

`MAX_DEPTH` 最大调用深度，默认0，无限制

`LOG_ENABLED` 是否打印日志

`LOG_LEVEL` 默认DEBUG

`LOG_FORMAT_FMT` 日志打印格式

`LOG_FORMAT_DATE` 日志日期格式

`LOG_FORMAT_STYLE` 日志style

`MIDDLEWARES` 请求操作

`PIPELINES` 存储操作

`EXTENSIONS` 信号操作

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### spider

`class TestSpider(Spider, coroutine_num=1, max_depth=0):`

`coroutine_num` 快速设置协程数量（大于1生效，否则使用配置）

`max_depth` 快速设置调用深度（大于0生效，否则使用配置）

`self.logger` logging 默认 `StreamHandler` 和 `NullHandler`

`self.options` 命令行传的参数

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 添加任务到pool

`self.crawler.engine.add_coroutine(coroutine, *callbacks)`

coroutine: 异步函数调用

*callbacks: 回调函数

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 添加异步生成器

`self.crawler.engine.add_generator(generator)`

generator: 异步生成器

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 关闭

`self.crawler.close()`

主动结束程序

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 添加退出函数

`self.crawler.register(func)`

func 普通函数或异步函数(函数没有形参)

程序结束前的回调函数

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Enter</kbd>

### 流模式请求数据

`Resquest`对象新增一个参数`stream_model`，表示以流模式请求数据，适用于请求图片，大文件的情况

如果没有使用自定义`client`，`Response`读取完数据需要调用 `response.close_default_client()`，关闭默认的连接，推荐使用`with`语句关闭

```python
class StreamSpider(Spider, coroutine_num=3, max_depth=0):

    async def __call__(self, *args, **kwargs):
        yield Request(url='http://localhost', stream_model=True)

    async def parse(self, response):
        if response.request.stream_model:
            async with response:
                async for i in response.aiter_raw():
                    pass
```

<kbd>↑</kbd><kbd>↓</kbd><kbd>←</kbd><kbd>→</kbd><kbd>Alt</kbd><kbd>F4</kbd>

完结 :100: :satellite: :earth_asia: :snowflake: :+1: :sunglasses:

!["鼓掌"](./鼓掌.gif "i'm fine thank you")

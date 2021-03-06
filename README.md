## ax-spider

> ***依赖***：python >= 3.9
>
> ***简介***：一款简单的python爬虫框架
> 
> ***开发***：`asyncio`和`httpx`
> 
> ***注意***：使用的`httpx`版本 0.23.0

***

#### 卖点

    轻量级、依赖少、安装快、运行速度也快

![谁反对](./谁反对.gif "谁反对")

#### 安装检查

    pip install ax-spider
    或者进入源码dist目录下，里面有 whl安装包 点击下载，pip install *.whl
    
    ax_spider -v 或者 python -m ax_spider -v

#### 一起来实现一个简单的示例

    源码tests目录下有一个更详细的示例

    1. 找一个空闲的文件夹，使用编辑器打开
    2. 打开终端，进入文件夹路径
    3. python -m ax_spider project test1  生成项目，项目名为test1
    4. python -m ax_spider spider t1 test1/spiders  在test1/spiders目录下生成解析文件
    5. 编辑t1.py
        from ax_spider import Spider, Request


        class T1Spider(Spider, coroutine_num=1, max_depth=0):

            async def __call__(self, *args, **kwargs):
                yield Request(url='http://www.baidu.com/')
        
            async def parse(self, response):
                self.logger.info(response.status_code)
    6. 当前目录下有一个run文件，运行文件
        from ax_spider import executor

        if __name__ == '__main__':
            executor({
                'path': 'test1.spiders.t1',
            })

        或者 python -m ax_spider crawl test1.spiders.t1

#### 命令行

    ax_spider -h 

    ax_spider project -h
    > 在当前目录下生成项目 ax_spider project base
    > --safe参数确保存在的文件不覆盖

    ax_spider spider -h
    > 生成解析文件，默认在 spiders 里  cd base && ax_spider spider test
    > 或者 ax_spider spider test base/spiders
    > -t 模板路径

    ax_spider crawl -h
    > 启动任务 cd .. && ax_spider crawl base.spiders.test name=james age=37 

    > 项目目录 run.py ，可以运行
    from ax_spider import executor

    executor({
        'path': 'base.spiders.ttt',
        'name': 'james',
        'age': 37
    })

    > 如果项目目录下有 ***commands*** 文件夹，文件格式如下，文件名就是命令名
    from argparse import ArgumentParser


    class Command(object):
        short_desc = ''
    
        def add_arguments(self, parser: ArgumentParser):
            parser.add_argument('-t', help='')
    
        def run(self, options):
            pass

***

#### 请求操作

    yield Request(url='http://localhost/')
    默认调用 parse 方法
    或者 self.crawler.engine.add_request(Request(url='http://localhost/'))

***

##### 存储

    item = BaseItem()
    item.title = ''
    yield item
    或者 self.crawler.engine.add_item(item, response)  response可以不填

    > 自定义Item
    from ax_spider import Item, Field


    @Item()
    class BaseItem(object):
        title = Field()
    
    > 使用的 attr 模块，Item是attr.attrs的别名，Field是attr.attrib的别名
    > 可以直接使用 attr 模块
    import attr

    
    @attr.attrs()
    class BaseItem(object):
        title = attr.attrib(
            type=str,
            converter=attr.converters.pipe(lambda x: x * 3, lambda x: x[:5]),
            validator=attr.validators.in_(['hello', 'hi'])
        )

***

#### middleware

    process_request
    > 请求前经过
    > return request(下一个) 其他(停止)

    process_exception
    > 请求出错经过
    > return request(重新请求) exception(下一个) 其他(停止) 

    process_response
    > 请求后经过
    > return request(重新请求) response(下一个) 其他(停止)

***

#### pipeline

    process_item
    > 返回item经过
    > return item(下一个) 其他(停止)

***

#### 信号
    
    可以注册普通函数或异步函数

    spider_opened
    > 参数  无

    spider_idle
    > 参数  无
    
    spider_closed
    > 参数  无

    request_received
    > 参数  request

    request_error
    > 参数  request exception

    response_received
    > 参数  response

    item_received
    > 参数  item response

***

#### setting

    COROUTINE_NUM
    协程数量，默认1

    MAX_DEPTH
    最大调用深度，默认0，无限制

    LOG_ENABLED
    是否打印日志

    LOG_LEVEL
    默认 DEBUG

    LOG_FORMAT_FMT
    日志格式

    LOG_FORMAT_DATE
    日志日期格式

    LOG_FORMAT_STYLE
    日志style

    MIDDLEWARES
    请求操作

    PIPELINES
    存储操作

    EXTENSIONS

***

### spider

    class TestSpider(Spider, coroutine_num=1, max_depth=0):

    coroutine_num
    > 快速设置协程数量

    max_depth
    > 快速设置调用深度

    self.logger
    > logging 默认 StreamHandler 和 NullHandler

    self.options
    > 命令行传的参数

***

### 添加任务到 pool

    self.crawler.engine.add_coroutine
    > 参数1: 异步函数
    > *callbacks: 回调函数

***

### 添加异步生成器

    self.crawler.engine.add_generator
    > 参数1: 异步生成器，返回请求对象或者存储对象
    > 其他参数有默认值

***

### 关闭

    self.crawler.close()

***

### 添加退出函数

    self.crawler.register
    > 参数 普通函数或异步函数(函数没有形参)

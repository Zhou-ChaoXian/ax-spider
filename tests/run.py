# coding: utf-8

from ax_spider import executor

if __name__ == '__main__':
    executor({
        'path': 'base.spiders.test',
        # 'path': 'base.spiders.test_cur',
        # 'path': 'base.spiders.test_cur_redis',
    })

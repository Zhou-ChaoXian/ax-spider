# coding: utf-8

import asyncio
import logging
from contextlib import suppress
from ..core.crawler import Crawler
from ..core.engine import ExitException
from ..__version__ import __title__

__all__ = ['executor']


def executor(options, selector=False, debug=False):
    with suppress(KeyboardInterrupt):
        if selector:
            from selectors import SelectSelector
            selector = SelectSelector()
            loop = asyncio.SelectorEventLoop(selector)
        else:
            loop = asyncio.new_event_loop()
        crawler = None
        try:
            asyncio.set_event_loop(loop)
            if debug:
                loop.set_debug(True)
            crawler = Crawler.from_crawler(loop, options)
            loop.run_until_complete(crawler.start_crawler())
        except ExitException:
            pass
        except Exception as e:
            if crawler is not None:
                crawler.state.inc_value('logical_error')
            logger = logging.getLogger(__title__)
            logger.exception(e)
        finally:
            if crawler is not None:
                loop.run_until_complete(crawler.end_crawler())
            try:
                getattr(asyncio.runners, '_cancel_all_tasks')(loop)
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.run_until_complete(loop.shutdown_default_executor())
            finally:
                asyncio.set_event_loop(None)
                loop.close()

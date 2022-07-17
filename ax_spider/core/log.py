# coding: utf-8

from logging.config import dictConfig
from ..__version__ import __title__


class DefaultLogger(object):

    def __init__(self, crawler):
        self.setting = crawler.setting

    def set_logger(self):
        enabled = self.setting.get('LOG_ENABLED')
        level = self.setting.get('LOG_LEVEL')
        fmt = self.setting.get('LOG_FORMAT_FMT')
        date = self.setting.get('LOG_FORMAT_DATE')
        style = self.setting.get('LOG_FORMAT_STYLE')
        log_config_dict = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                f'{__title__}': {
                    'class': 'logging.Formatter',
                    'format': fmt,
                    'datefmt': date,
                    'style': style
                }
            },
            'handlers': {
                'null': {
                    'class': 'logging.NullHandler',
                },
                f'{__title__}': {
                    'class': 'logging.StreamHandler',
                    'level': level,
                    'formatter': f'{__title__}',
                }
            },
            'loggers': {
                f'{__title__}': {
                    'level': level,
                    'handlers': [enabled and f'{__title__}' or 'null'],
                }
            }
        }
        dictConfig(log_config_dict)

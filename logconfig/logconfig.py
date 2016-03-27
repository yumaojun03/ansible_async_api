# An extended version of the log_settings module from zamboni:
# https://github.com/jbalogh/zamboni/blob/master/log_settings.py

from __future__ import absolute_import

from logging.config import dictConfig
import os.path

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(filename)s:%(lineno)d(%(module)s:%(funcName)s) - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'logging.handlers.SysLogHandler.LOG_LOCAL7',
            'formatter': 'standard',
        },
        'syslog2': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'logging.handlers.SysLogHandler.LOG_LOCAL7',
            'formatter': 'standard',
        },
        'access': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename':  os.path.join(LOG_DIR, 'access.log'),
            'maxBytes': 1024*1024*2,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'application': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename':  os.path.join(LOG_DIR, 'app.log'),
            'maxBytes': 1024*1024*2,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'general': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename':  os.path.join(LOG_DIR, 'gen.log'),
            'maxBytes': 1024*1024*2,
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'tornado': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'tornado.access': {
            'handlers': ['access'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tornado.app': {
            'handlers': ['application'],
            'level': 'DEBUG',
            'propagate': True
        },
        'tornado.gen': {
            'handlers': ['general'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}


def init_logging():
    """
    initial logging
    """
    dictConfig(LOGGING)









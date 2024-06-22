import logging
from logging.config import dictConfig

from obscura.process import PROCESS

import uvicorn.config


APP_LOGGER_NAME = 'obscura'
LEVEL = 'DEBUG' if PROCESS.ENV.is_dev else 'INFO'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "default": {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s | %(asctime)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        'obscura': {'level': LEVEL, 'handlers': ['default']},
        'uvicorn.error': {'level': LEVEL, 'handlers': ['default']},
        'uvicorn.access': {'level': 'INFO', 'handlers': ['default']},
    },
}


log = logging.getLogger(APP_LOGGER_NAME)

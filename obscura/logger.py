import logging
from logging.config import dictConfig

from obscura.process import PROCESS


APP_LOGGER_NAME = 'app'
LEVEL = 'DEBUG' if PROCESS.ENV.is_dev else 'INFO'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "default": {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(asctime)s | %(levelprefix)s | %(name)-15s | %(message)s',
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
        APP_LOGGER_NAME: {'level': LEVEL, 'handlers': ['default']},
        'uvicorn': {'level': LEVEL, 'handlers': ['default']},
    },
}


dictConfig(LOGGING_CONFIG)
log = logging.getLogger(APP_LOGGER_NAME)

def component_logger(component) -> logging.Logger:
    # Append the component to our app, so it will inherit the app's logging config
    name = f'{APP_LOGGER_NAME}.{component}'
    return logging.getLogger(name)

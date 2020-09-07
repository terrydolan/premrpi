"""Logger config for premrpi."""

dictLogConfig = {
    'version': 1,
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'myConsoleFormatter'
        }
    },
    'loggers': {
        'premrpi': {
            'handlers': ['consoleHandler'],
            'level': 'DEBUG'
        }
    },
    'formatters': {
        'myConsoleFormatter': {
            'format': '%(name)s - %(levelname)s - %(message)s'
        }
    }
}

"""
With fileHandler

dictLogConfig = {
    'version': 1,
    'handlers': {
        'fileHandler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'myFileFormatter',
            'filename': 'premrpi.log',
            'mode': 'a',
            'maxBytes': 10000,
            'backupCount': 2
        },
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'myConsoleFormatter'
        }
    },
    'loggers': {
        'premrpi': {
            'handlers': ['consoleHandler'], #['consoleHandler', 'fileHandler']
            'level': 'DEBUG'
        }
    },
    'formatters': {
        'myFileFormatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'myConsoleFormatter': {
            'format': '%(name)s - %(levelname)s - %(message)s'
        }
    }
}
"""


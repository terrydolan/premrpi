"""Logger config for premrpi."""

dictLogConfig = {
    'version': 1,
    'handlers': {
        'fileHandler': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'myFileFormatter',
            'filename': 'premrpi.log'
        },
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
        'myFileFormatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'myConsoleFormatter': {
            'format': '%(name)s - %(levelname)s - %(message)s'
        }
    }
}

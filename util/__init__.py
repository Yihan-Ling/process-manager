def default_logging():
    import logging, coloredlogs
    coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s.%(msecs)03d %(filename)15s:%(lineno)03d %(levelname)7s: %(message)s'
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('__main__'))
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('ui'))
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('dummy_processes'))
    coloredlogs.install(level=logging.DEBUG, logger=logging.getLogger('node'))

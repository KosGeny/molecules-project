from loguru import logger
import sys


class LoggerSetup:
    def __init__(self):
        logger.remove()
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        )
        logger.add(
            sys.stdout,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        )

    def get_logger(self):
        return logger


log_setup = LoggerSetup()
app_logger = log_setup.get_logger()

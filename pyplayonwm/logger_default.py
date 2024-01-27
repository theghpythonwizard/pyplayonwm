import logging
import os
import re
from pyplayonwm.helpers import HelperTools

__all__ = ['LoggerDefault']


class StripAsciiFormatter(logging.Formatter):

    def format(self, record):
        message = record.getMessage()
        if record.levelno == logging.INFO:
            message = self.format_message(message)
        formatted_message = f"[{record.levelname} - {self.formatTime(record)}][{record.name}] {message}"
        return formatted_message

    def format_message(self, message):
        if message.isascii():
            pattern = r'\x1b\[[0-9;]*m'  # Regular expression pattern to match ANSI escape sequences
            return re.sub(pattern, '', message)
        else:
            return message


class LoggerDefault(logging.Logger):

    def __init__(self, log_file=""):
        self.h = HelperTools()
        self.logger_base_dir = os.path.join(self.h.git_root(), "logging")
        self.log_file = log_file
        self.default_logger = os.path.join(self.logger_base_dir, self.log_file)

    def info(self, message):
        super().info(message)

    def set_logger(self, logger):

        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(self.default_logger)
        handler.setLevel(logging.INFO)

        logging_formatter = StripAsciiFormatter('[%(levelname)s - %(asctime)s][%(name)s] %(message)s', '%Y/%m/%d %H:%M:%S')
        handler.setFormatter(logging_formatter)

        console_formatter = logging.Formatter('[%(levelname)s - %(asctime)s][%(name)s] %(message)s', '%Y/%m/%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        logger.addHandler(handler)
        logger.addHandler(console_handler)

        return logger

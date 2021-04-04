"""
Logger class.
"""

__version__ = '0.0.1'
__author__ = 'Szabo Cristian'

import logging
import os
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

import config


class LoggerMessageType:
    """
    Logger message types.
    """

    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class Logger:
    """
    Logger class
    """

    LOG_DIR = config.LOG_DIR
    FILE = sys.stdout
    LOGGER_INSTANCES = {}

    @staticmethod
    def get_logger(logger_name, file_name=None, no_stdout=False) -> object:
        """
        Create logger instance with specified logger_name. Logger will write to file specified by file_name in current
        directory and stdout. If logging to stdout is not needed, set no_stdout to True.
        @param logger_name: string
        @param file_name: string
        @param no_stdout: bool
        @return: object (logging.Logger)
        """

        if not file_name and no_stdout:
            raise Exception('No log location. Either specify file_name or set no_stdout to False')

        if logger_name in Logger.LOGGER_INSTANCES:
            return Logger.LOGGER_INSTANCES[logger_name]

        logger = logging.getLogger(logger_name)
        log_formatter = logging.Formatter("%(asctime)s [%(levelname)-8.8s] %(message)s")

        if file_name and file_name[-4:] != '.log':
            file_name = r"{}.log".format(file_name)

        file_handler = RotatingFileHandler(
            os.path.join(Logger.LOG_DIR, file_name)) if file_name else logging.StreamHandler(sys.stdout)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

        if not no_stdout and not isinstance(file_handler, logging.StreamHandler):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            logger.addHandler(console_handler)

        logger.setLevel(logging.INFO)

        Logger.LOGGER_INSTANCES[logger_name] = logger

        return logger

    @staticmethod
    def ensure_log_directory(log_dir=None) -> None:
        """
        Function creates log directory if missing.
        @param log_dir: string
        @return: None
        """
        if not log_dir:
            log_dir = Logger.LOG_DIR

        if os.path.isdir(log_dir):
            return

        os.makedirs(log_dir)

    @staticmethod
    def set_file_logging(file_name, log_dir=None) -> None:
        """
        Logging file setter. File is opened for writing here.
        @param file_name: string
        @param log_dir: string (optional, default config.LOG_DIR)
        @return: None
        """
        if not log_dir:
            log_dir = Logger.LOG_DIR

        Logger.ensure_log_directory(log_dir)

        try:
            file_path = os.path.join(log_dir, file_name)
            file = open(file_path, "w+" if not os.path.isfile(file_path) else 'a+')
            Logger.FILE = file
        except IOError as exception:
            print(exception)

    @staticmethod
    def close_log_file() -> None:
        """
        Close log file.
        @return: None
        """

        if Logger.FILE and Logger.FILE != sys.stdout:
            Logger.FILE.close()

    @staticmethod
    def datetime_string() -> str:
        """
        Datetime string formatter.
        @return: string
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def __log(logger_type, message, flush, line_end) -> None:
        """
        Format message and Write to log file.
        @param logger_type: string (LoggerMessageType)
        @param message: string
        @param flush: boolean
        @param line_end: string
        @return: None
        """
        try:
            from flask import request
            flask_message = f"{request.remote_addr} "
        except:
            flask_message = ""

        if logger_type:
            Logger.FILE.write(
                f"{flask_message}" + f"[{logger_type:7s} {Logger.datetime_string()}] {message}" + line_end)
        else:
            Logger.FILE.write("{0}".format(message) + line_end)

        if flush:
            Logger.FILE.flush()

    @staticmethod
    def info(message, flush=True, line_end='\n') -> None:
        """
        Log INFO.
        @param message: string
        @param flush: boolean
        @param line_end: string
        @return: None
        """
        Logger.__log(LoggerMessageType.INFO, message, flush, line_end)

    @staticmethod
    def warning(message, flush=True, line_end='\n') -> None:
        """
        Log WARNING.
        @param message: string
        @param flush: boolean
        @param line_end: string
        @return: None
        """
        Logger.__log(LoggerMessageType.WARNING, message, flush, line_end)

    @staticmethod
    def error(message, flush=True, line_end='\n') -> None:
        """
        Log ERROR.
        @param message: string
        @param flush: boolean
        @param line_end: string
        @return: None
        """
        Logger.__log(LoggerMessageType.ERROR, message, flush, line_end)

    @staticmethod
    def exception(message, flush=True, line_end='\n') -> None:
        """
        Log ERROR wrapper for exceptions.
        @param message: string
        @param flush: boolean
        @param line_end: string
        @return: None
        @return:
        """
        Logger.__log(LoggerMessageType.ERROR, message, flush, line_end)
        Logger.__log(LoggerMessageType.ERROR, traceback.format_exc(), flush, line_end)

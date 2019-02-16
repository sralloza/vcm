"""General used functions."""
import logging
import os
import re

from requests import Response

PRODUCTION = False


def get_logger(name, level=None, rewrite=False, log_format=None, filename='vcd.log'):
    """Returns a custom Logger."""

    if level is None:
        if PRODUCTION:
            level = logging.INFO
        else:
            level = logging.DEBUG

    default_format = '[%(asctime)s] %(levelname)-8s - %(threadName)s - ' \
                     '%(name)s:%(lineno)s: %(message)s'
    log_format = log_format or default_format
    if not filename:
        filename = name + '.log'

    if rewrite:
        logger = logging.getLogger(name)
        logger.handlers = []
    else:
        logger = logging.getLogger(name)

    if logger.hasHandlers() is False:
        handler = logging.FileHandler(filename, encoding='utf-8')
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger


get_logger('rpi.downloader', rewrite=True)

FILENAME_PATTERN = re.compile('filename="(.*)"')
ROOT_FOLDER = 'D:/sistema/desktop/virtual_ittade3'

if os.path.isdir(ROOT_FOLDER) is False:
    os.mkdir(ROOT_FOLDER)

ERROR_FOLDER = 'D:/.scripts/vcd/errors'

ERROR_LOGGER = get_logger(__name__, filename='error.log')


def save_response(response: Response, name):
    """Saves a response content in case of error.

    Args:
        response (Response): response to save.
        name (str): name of the file to save the response.
    """
    ERROR_LOGGER.critical('Saving response to %r', name)

    with open(name, 'wb') as file_handler:
        file_handler.write(response.content)

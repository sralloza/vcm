import logging
import os
import re

from requests import Response


def get_logger(name, level=logging.DEBUG, rewrite=False, log_format=None, filename='vcd.log'):
    """Returns a custom Logger."""

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

error_logger = get_logger(__name__, filename='error.log')


def save_response(response: Response, name):
    # if os.path.isdir(ERROR_FOLDER):
    #     os.mkdir(ERROR_FOLDER)

    # name = os.path.join(ERROR_FOLDER, name)
    error_logger.critical('Saving response to %r', name)

    with open(name, 'wb') as fh:
        fh.write(response.content)

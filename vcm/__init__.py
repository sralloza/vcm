"""File downloader for the Virtual Campus of the Valladolid Unversity."""
import logging
import os
from logging.handlers import RotatingFileHandler
from threading import current_thread

from .core.options import Options

__all__ = []

if os.environ.get('TESTING') is None:
    should_roll_over = os.path.isfile(Options.LOG_PATH)

    fmt = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
    handler = RotatingFileHandler(filename=Options.LOG_PATH, maxBytes=2_500_000,
                                  encoding='utf-8', backupCount=5)

    current_thread().setName('MT')

    if should_roll_over:
        handler.doRollover()

    logging.basicConfig(handlers=[handler, ], level=Options.LOGGING_LEVEL, format=fmt)

logging.getLogger('urllib3').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

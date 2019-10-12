"""File downloader for the Virtual Campus of the Valladolid Unversity."""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import current_thread

from .core.options import Options

__all__ = []



def get_version():
    version_path = Path(__file__).with_name("VERSION")
    return version_path.read_text()


version = get_version()

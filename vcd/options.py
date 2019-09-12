import logging
import os
import re
from pathlib import Path

from colorama import init

init()


class Options:
    _LOADED = False

    PRODUCTION = False
    FILENAME_PATTERN = re.compile('filename=\"?([\w\s\-!$?%^&()_+~=`{\}\[\].;\',]+)\"?')

    ROOT_FOLDER: Path = Path(__file__).parent.parent
    LOGS_FOLDER: Path = ROOT_FOLDER / 'logs'
    LOG_PATH: Path = LOGS_FOLDER / 'vcd.log'
    TIMEOUT = 30
    LOGGING_LEVEL = logging.DEBUG

    FORUMS_SUBFOLDERS = True

    _CONFIG_PATH = os.path.normpath(os.path.join(os.path.expanduser('~'), 'vcd-config.ini'))

    @staticmethod
    def ensure_files():
        Options.ROOT_FOLDER.mkdir(exist_ok=True)
        Options.LOGS_FOLDER.mkdir(exist_ok=True)


Options.ensure_files()

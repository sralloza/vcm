import logging
import re
from pathlib import Path

from colorama import init

from vcm.core.modules import Modules

init()


class Options:
    PRODUCTION = False
    FILENAME_PATTERN = re.compile('filename=\"?([\w\s\-!$?%^&()_+~=`{\}\[\].;\',]+)\"?')

    ROOT_FOLDER: Path = Path('D:/sistema/desktop/ittade-metadata-4')
    LOGS_FOLDER: Path = ROOT_FOLDER / '.logs'
    LOG_PATH: Path = LOGS_FOLDER / 'vcd.log'
    TIMEOUT = 30
    LOGGING_LEVEL = logging.DEBUG

    FORUMS_SUBFOLDERS = True

    DATABASE_PATH: Path = ROOT_FOLDER / 'links.db'
    USE_BASE64_ICONS = False

    CONFIG_PATH = Path.home() / 'vcd-config.ini'
    CREDENTIALS_PATH = Path.home() / 'vcd-credentials.ini'

    _MODULE = Modules.undefined

    @staticmethod
    def ensure_files():
        Options.ROOT_FOLDER.mkdir(exist_ok=True)
        Options.LOGS_FOLDER.mkdir(exist_ok=True)

    @staticmethod
    def set_module(module):
        Options._MODULE = Modules(module)

    @staticmethod
    def get_module():
        return Options._MODULE


Options.ensure_files()

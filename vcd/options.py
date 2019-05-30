import os
import logging
import re

from colorama import Fore, init
from configparser import ConfigParser, NoSectionError, NoOptionError


init()


class OptionError(Exception):
    """Option error."""


class Options:
    _CONFIG_PATH = os.path.expanduser('~') + '/vcd-config.ini'

    PRODUCTION = False
    FILENAME_PATTERN = re.compile(
        'filename=\"?([\w\s\-\!\$\?\%\^\&\(\)\_\+\~\=\`\{\}\[\]\.\;\'\,]+)\"?')
    ROOT_FOLDER = 'D:/sistema/desktop/ittade-files'

    LOGS_FOLDER = os.path.expanduser('~').replace('\\', '/') + '/logs/'
    LOG_PATH = os.path.join(LOGS_FOLDER, 'vcd.log').replace('\\', '/')
    TIMEOUT = 30
    LOGGING_LEVEL = logging.DEBUG

    # Creators

    @staticmethod
    def create_root_folder():
        if os.path.isdir(Options.ROOT_FOLDER) is False:
            os.makedirs(Options.ROOT_FOLDER)

    @staticmethod
    def create_logs_folder():
        if os.path.isdir(Options.LOGS_FOLDER) is False:
            os.makedirs(Options.LOGS_FOLDER)

    # Setters

    @staticmethod
    def set_logs_folder(logs_folder):
        Options.LOGS_FOLDER = logs_folder
        Options.create_logs_folder()

    @staticmethod
    def set_root_folder(root_folder):
        Options.ROOT_FOLDER = root_folder
        Options.create_root_folder()

    @staticmethod
    def set_timeout(timeout: int):
        if not isinstance(timeout, int):
            raise TypeError(f'Timeout must be int, not {type(timeout).__name__}')

        Options.TIMEOUT = timeout

    @staticmethod
    def set_logging_level(logging_level):
        logging_level = logging.getLevelName(logging_level.upper())
        if not isinstance(logging_level, int):
            raise ValueError(f'Invalid log level: {logging_level!r}')

        Options.LOGGING_LEVEL = logging_level

    @staticmethod
    def load_config():
        config = ConfigParser()
        config.read(Options._CONFIG_PATH)
        try:
            root_folder = config.get('OPTIONS', 'ROOT_FOLDER')
            timeout = config.get('OPTIONS', 'TIMEOUT')
            logs_folder = config.get('OPTIONS', 'LOG_FOLDER')
            logging_level = config.get('OPTIONS', 'LOGGING_LEVEL')

        except (NoSectionError, NoOptionError):
            config['OPTIONS'] = {
                'ROOT_FOLDER': Options.ROOT_FOLDER,
                'TIMEOUT': 30, 'LOG_FOLDER': Options.LOGS_FOLDER,
                'LOGGING_LEVEL': logging.getLevelName(Options.LOGGING_LEVEL)
            }
            with open(Options._CONFIG_PATH, 'wt', encoding='utf-8') as fh:
                config.write(fh)

            return exit(Fore.RED + 'Invalid Options' + Fore.RESET)

        Options.set_root_folder(root_folder)
        Options.set_timeout(int(timeout))
        Options.set_logs_folder(logs_folder)
        Options.set_logging_level(logging_level)


Options.load_config()
Options.create_root_folder()

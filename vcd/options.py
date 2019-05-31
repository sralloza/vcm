import os
import logging
import re

from colorama import Fore, init
from configparser import ConfigParser, NoSectionError, NoOptionError


init()


class OptionError(Exception):
    """Option error."""


class Options:
    _CONFIG_PATH = os.path.normpath(os.path.join(os.path.expanduser('~'), 'vcd-config.ini'))

    PRODUCTION = False
    FILENAME_PATTERN = re.compile(
        'filename=\"?([\w\s\-\!\$\?\%\^\&\(\)\_\+\~\=\`\{\}\[\]\.\;\'\,]+)\"?')
    ROOT_FOLDER = os.path.normpath(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'default_root_folder'))

    LOGS_FOLDER = os.path.normpath(os.path.join(os.path.expanduser('~'), 'logs'))
    LOG_PATH = os.path.normpath(os.path.join(LOGS_FOLDER, 'vcd.log'))
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
        Options.TIMEOUT = int(timeout)

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
            Options.set_root_folder(config.get('options', 'root_folder'))
            Options.set_timeout(config.get('options', 'timeout'))
            Options.set_logs_folder(config.get('options', 'log_folder'))
            Options.set_logging_level(config.get('options', 'logging_level'))

        except (NoSectionError, NoOptionError):
            config['options'] = {
                'root_folder': Options.ROOT_FOLDER,
                'timeout': '30', 'log_folder': Options.LOGS_FOLDER,
                'logging_level': logging.getLevelName(Options.LOGGING_LEVEL),
            }
            with open(Options._CONFIG_PATH, 'wt', encoding='utf-8') as fh:
                config.write(fh)

            return exit(Fore.RED + 'Invalid Options' + Fore.RESET)


Options.load_config()
Options.create_root_folder()

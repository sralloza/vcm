import logging
import types
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path

from colorama import init

from vcm.core.exceptions import ConfigError
from vcm.core.modules import Modules
from vcm.core.utils import exception_exit, safe_exit

init()

_config = ConfigParser()


class Options:
    ROOT_FOLDER: Path = Path('D:/sistema/desktop/ittade-metadata-4')
    LOGS_FOLDER: Path = ROOT_FOLDER / '.logs'
    LOG_PATH: Path = LOGS_FOLDER / 'vcd.log'
    TIMEOUT = 30
    LOGGING_LEVEL: int = logging.DEBUG

    FORUMS_SUBFOLDERS: bool = True

    DATABASE_PATH: Path = ROOT_FOLDER / 'links.db'
    USE_BASE64_ICONS: bool = False

    CONFIG_PATH: Path = Path.home() / 'vcd-config.ini'
    CREDENTIALS_PATH: Path = Path.home() / 'vcd-credentials.ini'

    _MODULE: Modules = Modules.undefined

    def __str__(self):
        data = self.list()
        data.sort()
        print(data)

        template = '%%-%ds: %%s' % (max([len(x) for x in data]) + 1)

        def get_info(x):
            return x.replace('_', ' ').strip().capitalize(), getattr(self, x.upper())

        message = '\n'.join([template % get_info(x) for x in data])
        return message

    def __repr__(self):
        return str(self)

    @classmethod
    def to_string(cls):
        return cls().__str__()

    @classmethod
    def list(cls):
        output = []
        for e in dir(cls):
            if e.startswith('_'):
                continue

            real = getattr(cls, e)

            if (isinstance(real, types.FunctionType)
                    or isinstance(real, types.MethodType) or callable(real)):
                continue

            output.append(e)
        return output

    @classmethod
    @safe_exit
    def load_config(cls):
        try:
            return cls._load_config()
        except NoOptionError as exc:
            raise ConfigError(exc.message)

    @classmethod
    def make_default(cls):
        config = ConfigParser()
        config.add_section("general")
        config['general']['root_folder'] = ' '
        config['general']['logging_level'] = 'INFO'
        config['general']['timeout'] = '30'
        config['general']['forum_subfolders'] = 'True'
        config['general']['use_base64_icons'] = 'False'

        with cls.CONFIG_PATH.open('wt') as fp:
            config.write(fp)

    # noinspection PyProtectedMember
    @classmethod
    def _load_config(cls):
        _config.read(cls.CONFIG_PATH.as_posix())

        # raise NotImplementedError
        try:
            root_folder = _config.get('general', 'root_folder')
        except (FileNotFoundError, NoSectionError):
            cls.make_default()
            return exit('No config file found, created one (%s).\nRun again.' % cls.CONFIG_PATH)

        if not root_folder:
            raise ConfigError('Must set root_folder')

        logging_level = _config.get('general', 'logging_level').upper()

        cls.ROOT_FOLDER: Path = Path(root_folder)
        cls.TIMEOUT = _config.getint('general', 'timeout')

        try:
            cls.LOGGING_LEVEL = logging._nameToLevel[logging_level]
        except KeyError:
            raise ConfigError('%s is not a valid logging level' % logging_level)

        cls.FORUMS_SUBFOLDERS = _config.getboolean('general', 'forum_subfolders')
        cls.USE_BASE64_ICONS = _config.getboolean('general', 'use_base64_icons')

        cls._fix_dependencies()

        # TODO - think, these are absolute, with no dependecies
        # cls.CONFIG_PATH = Path.home() / 'vcd-config.ini'
        # cls.CREDENTIALS_PATH = Path.home() / 'vcd-credentials.ini'

    @classmethod
    def _fix_dependencies(cls):
        if not isinstance(cls.ROOT_FOLDER, Path):
            raise ConfigError(
                'root folder must be pathlib.Path, not %s' % cls.__name__)

        cls.DATABASE_PATH: Path = cls.ROOT_FOLDER / 'links.db'
        cls.LOGS_FOLDER: Path = cls.ROOT_FOLDER / '.logs'
        cls.LOG_PATH: Path = cls.LOGS_FOLDER / 'vcd.log'

    @staticmethod
    def ensure_files():
        try:
            Options.ROOT_FOLDER.mkdir(exist_ok=True)
        except OSError:
            exc = ConfigError('Invalid root folder: %s' % Options.ROOT_FOLDER)
            return exception_exit(exc)

        Options.LOGS_FOLDER.mkdir(exist_ok=True)

    @staticmethod
    def set_module(module):
        Options._MODULE = Modules(module)

    @staticmethod
    def get_module():
        return Options._MODULE


Options.load_config()
Options.ensure_files()

import logging
import os
import re
import sys
from time import time
from logging.handlers import RotatingFileHandler
from threading import current_thread
from traceback import format_exc
from typing import Union

from colorama import Fore
from colorama import init as start_colorama
from decorator import decorator
from packaging import version
from werkzeug.utils import secure_filename as _secure_filename

from .time_operations import seconds_to_str

logger = logging.getLogger(__name__)
start_colorama()


class MetaGetch(type):
    _instances = {}

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs, **kwargs)
        cls.__new__ = cls._getch


class Key:
    def __init__(self, key1, key2=None, is_int=None):
        if not isinstance(key1, (bytes, int)):
            raise TypeError("key1 must be bytes or int, not %r" % type(key1).__name__)

        if not isinstance(key2, (bytes, int)) and key2 is not None:
            raise TypeError("key2 must be bytes or int, not %r" % type(key1).__name__)

        if isinstance(key1, bytes):
            if len(key1) != 1:
                raise ValueError("key1 must have only one byte, not %d" % len(key1))

        if isinstance(key2, bytes):
            if len(key2) != 1:
                raise ValueError("key2 must have only one byte, not %d" % len(key2))

        if key2:
            if type(key1) != type(key2):
                raise TypeError(
                    "key1 and key2 must be of the same type (%r - %r)"
                    % (type(key1).__name__, type(key2).__name__)
                )

        self.is_int = is_int
        if self.is_int is None:
            key1_bytes = isinstance(key1, bytes)
            key2_bytes = key2 is None or isinstance(key2, bytes)

            key1_int = isinstance(key1, int)
            key2_int = key2 is None or isinstance(key2, int)

            if key1_bytes and key2_bytes:
                self.is_int = False
            elif key1_int and key2_int:
                self.is_int = True

        assert self.is_int is not None, "is_int can't be None here"

        self.key1 = int(key1) if is_int and key1 else key1
        self.key2 = int(key2) if is_int and key2 else key2

    def __str__(self):
        return "Key(key1=%r, key2=%r)" % (self.key1, self.key2)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.key1 == other.key1 and self.key2 == other.key2

    def to_int(self):
        if self.is_int:
            raise ValueError("Key is already in int mode")

        key1 = ord(self.key1)
        key2 = ord(self.key2) if self.key2 else self.key2
        return type(self)(key1=key1, key2=key2, is_int=True)

    def to_char(self):
        if not self.is_int:
            raise ValueError("Key is already in char mode")

        key1 = chr(self.key1).encode("utf-8")
        key2 = chr(self.key2).encode("utf-8") if self.key2 else self.key2
        return type(self)(key1=key1, key2=key2, is_int=False)


class getch(metaclass=MetaGetch):
    key1: Union[bytes, int]
    key2: Union[bytes, int, None]

    def _getch(self, to_int=False, *args, **kwargs):
        result = getch._Getch()()

        if result == b"\x00":
            key = Key(result, getch._Getch()())
        else:
            key = Key(result)

        if to_int:
            key = key.to_int()

        return key

    def to_int(self):
        """Only for intellisense."""

    class _Getch:
        """Gets a single character from standard input.  Does not echo to the
    screen."""

        def __init__(self):
            try:
                self.impl = self._GetchWindows()
            except ImportError:
                self.impl = self._GetchUnix()

        def __call__(self):
            return self.impl()

        class _GetchUnix:
            def __init__(self):
                import tty, sys

            def __call__(self):
                import sys, tty, termios

                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch

        class _GetchWindows:
            def __init__(self):
                import msvcrt

            def __call__(self):
                import msvcrt

                return msvcrt.getch()


def secure_filename(filename, spaces=False):
    """Makes the filename secure enough to be used as a filename.

    Args:
        filename (str): the filename to secure.
        spaces (bool, optional): If True, the low bars will be replaced with
            spaces. If True, the spaces will be replaced with low bars.
            Defaults to False.

    Returns:
        str: secured filename.
    """
    filename = _secure_filename(filename)
    if not spaces:
        return filename
    return filename.replace("_", " ")


class Patterns:
    FILENAME_PATTERN = re.compile(
        r'filename="?([\w\s\-!$?%^&()_+~=`{\}\[\].;\',´¨¡¿!@#·\$%€\/]+)"'
    )


def exception_exit(exception, to_stderr=False, red=True):
    """Exists the progam showing an exception.

    Args:
        exception: Exception to show. Must hinherit `Exception`

    Raises:
        TypeError: if exception is not a subclass of Exception.

    """

    raise_exception = False

    try:
        if not issubclass(exception, BaseException):
            raise_exception = True
    except TypeError:
        if not isinstance(exception, BaseException):
            raise_exception = True

    if isinstance(exception, SystemExit):
        return

    if raise_exception:
        raise TypeError("exception should be a subclass of Exception")

    exc_str = ", ".join((str(x) for x in exception.args))
    message = "%s: %s" % (exception.__class__.__name__, exc_str)
    message += "\n" + format_exc()

    if red:
        message = Fore.LIGHTRED_EX + message + Fore.RESET

    if to_stderr:
        print(message, file=sys.stderr)
        return sys.exit(-1)

    print(message)
    return sys.exit(-1)


@decorator
def safe_exit(func, to_stderr=False, red=True, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except BaseException as exc:
        return exception_exit(exc, to_stderr=to_stderr, red=red)


@decorator
def timing(func, name=None, level=None, *args, **kwargs):
    name = name or func.__name__
    level = level or logging.INFO
    t0 = time()
    raise_exc = False
    exception = None

    try:
        result = func(*args, **kwargs)
    except SystemExit as exc:
        raise_exc = True
        exception = exc
    except Exception as exc:
        raise_exc = True
        exception = exc

    delta_t = time() - t0
    logger.log(level, "%s executed in %s", name, seconds_to_str(delta_t))

    if raise_exc:
        raise exception
    return result


def str2bool(value):
    _true_set = {"yes", "true", "t", "y", "1", "s", "si", "sí"}
    _false_set = {"no", "false", "f", "n", "0"}

    if value in (True, False):
        return value

    if isinstance(value, str):
        value = value.lower()
        if value in _true_set:
            return True
        if value in _false_set:
            return False

    raise ValueError("Invalid bool string: %r" % value)


def configure_logging():
    from .settings import GeneralSettings

    if os.environ.get("TESTING") is None:
        should_roll_over = GeneralSettings.log_path.exists()

        fmt = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
        handler = RotatingFileHandler(
            filename=GeneralSettings.log_path,
            maxBytes=2_500_000,
            encoding="utf-8",
            backupCount=GeneralSettings.max_logs,
        )

        current_thread().setName("MT")

        if should_roll_over:
            handler.doRollover()

        logging.basicConfig(
            handlers=[handler], level=GeneralSettings.logging_level, format=fmt
        )

    logging.getLogger("urllib3").setLevel(logging.ERROR)


def more_settings_check():
    from vcm.core._settings import defaults
    from vcm.core.settings import GeneralSettings, NotifySettings

    os.environ["VCM_DISABLE_CONSTRUCTS"] = "True"
    if GeneralSettings.root_folder == defaults["general"]["root-folder"]:
        del os.environ["VCM_DISABLE_CONSTRUCTS"]
        raise Exception("Must set 'general.root-folder'")

    if NotifySettings.email == defaults["notify"]["email"]:
        del os.environ["VCM_DISABLE_CONSTRUCTS"]
        raise Exception("Must set 'notify.email'")

    del os.environ["VCM_DISABLE_CONSTRUCTS"]

    # Setup
    os.makedirs(GeneralSettings.root_folder, exist_ok=True)
    os.makedirs(GeneralSettings.logs_folder, exist_ok=True)


def setup_vcm():
    more_settings_check()
    configure_logging()


class Printer:
    _print = print

    @classmethod
    def reset(cls):
        cls._print = print

    @classmethod
    def silence(cls):
        cls._print = cls.useless

    @classmethod
    def print(cls, *args, **kwargs):
        return cls._print(*args, **kwargs)

    @classmethod
    def useless(cls, *args, **kwargs):
        pass


def check_updates():
    from vcm import version as current_version
    from .networking import connection

    response = connection.get(
        "https://raw.githubusercontent.com/sralloza/vcm/master/vcm/VERSION"
    )
    newer_version = version.parse(response.text.strip())
    current_version = version.parse(current_version)

    if newer_version > current_version:
        Printer.print(
            "Newer version available: %s (current version: %s)"
            % (newer_version, current_version)
        )
        return True

    Printer.print("No updates available (current version: %s)" % current_version)
    return False


class MetaSingleton(type):
    """Metaclass to always make class return the same instance."""

    def __init__(cls, name, bases, attrs):
        super(MetaSingleton, cls).__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MetaSingleton, cls).__call__(*args, **kwargs)

        # Uncomment line to check possible singleton errors
        # logger.info("Requested Connection (id=%d)", id(cls._instance))
        return cls._instance

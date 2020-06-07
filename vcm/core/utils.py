import logging
import os
import pickle
import re
import sys
import time
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from logging.handlers import RotatingFileHandler
from threading import Lock, current_thread
from traceback import format_exc
from typing import TypeVar, Union

from colorama import Fore
from colorama import init as start_colorama
from decorator import decorator
from packaging import version

from .time_operations import seconds_to_str

ExceptionClass = TypeVar("ExceptionClass")
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


def secure_filename(filename, spaces=True):
    if isinstance(filename, str):
        from unicodedata import normalize

        filename = normalize("NFKD", filename).encode("ascii", "ignore")
        filename = filename.decode("ascii")
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    _filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
    _windows_device_files = (
        "CON",
        "AUX",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "LPT1",
        "LPT2",
        "LPT3",
        "PRN",
        "NUL",
    )

    temp_str = "_".join(filename.split())
    filename = str(_filename_ascii_strip_re.sub("", temp_str)).strip("._")

    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = "_" + filename

    if spaces:
        return " ".join(filename.split("_"))

    return filename


class Patterns:
    FILENAME_PATTERN = re.compile(
        r'filename="?([\w\s\-!$%^&()_+=`´\¨{\}\[\].;\',¡¿@#·€]+)"?'
    )


def exception_exit(exception, to_stderr=True, red=True):
    """Exists the progam showing an exception.

    Args:
        exception: Exception to show. Must hinherit `Exception`

    Raises:
        TypeError: if exception is not a subclass of Exception.

    """

    raise_exception = False

    try:
        if not issubclass(exception, Exception):
            raise_exception = True
    except TypeError:
        # Check for SytemExit (inherints from BaseException, not Exception)
        if not isinstance(exception, BaseException):
            raise_exception = True

    if raise_exception:
        raise TypeError("exception should be a subclass of Exception")

    message = "%s: %s" % (
        exception.__class__.__name__,
        ", ".join((str(x) for x in exception.args)),
    )
    message += "\n" + format_exc()

    if red:
        message = Fore.LIGHTRED_EX + message + Fore.RESET

    file = sys.stderr if to_stderr else sys.stdout
    print(message, file=file)

    return exit(-1)


@decorator
def safe_exit(func, to_stderr=False, red=True, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        logger.exception("Exception catched:")
        return exception_exit(exc, to_stderr=to_stderr, red=red)


@decorator
def timing(func, name=None, level=None, *args, **kwargs):
    level = level or logging.INFO
    name = name or func.__name__
    t0 = time.time()
    result = None

    logger.log(level, "Starting execution of %s", name)
    try:
        result = func(*args, **kwargs)
    finally:
        if ErrorCounter.has_errors():
            logger.warning(ErrorCounter.report())

        delta_t = time.time() - t0
        logger.log(level, "%s executed in %s", name, seconds_to_str(delta_t))

        is_exception = sys.exc_info()[0] is not None
        if not is_exception:
            return result


_true_set = {"yes", "true", "t", "y", "1", "sí", "si", "s"}
_false_set = {"no", "false", "f", "n", "0"}


def str2bool(value):
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
    from ._settings import defaults
    from .settings import GeneralSettings, NotifySettings

    os.environ["VCM_DISABLE_CONSTRUCTS"] = "True"
    if GeneralSettings.root_folder == defaults["general"]["root-folder"]:
        raise Exception("Must set 'general.root-folder'")

    if NotifySettings.email == defaults["notify"]["email"]:
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
    _lock = Lock()

    @classmethod
    def reset(cls):
        cls._print = print

    @classmethod
    def silence(cls):
        cls._print = cls.useless

    @classmethod
    def useless(cls, *args, **kwargs):
        pass

    @classmethod
    def print(cls, *args, **kwargs):
        with cls._lock:
            return cls._print(*args, **kwargs)


def check_updates():
    from vcm import __version__ as current_version
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

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ErrorCounter:
    error_map = defaultdict(lambda: 0)

    @classmethod
    def has_errors(cls) -> bool:
        return bool(cls.error_map)

    @classmethod
    def record_error(cls, exc: Exception):
        cls.error_map[exc.__class__] += 1

    @classmethod
    def report(cls) -> str:
        message = f"{sum(cls.error_map.values())} errors found "
        errors = list(cls.error_map.items())
        errors.sort(key=lambda x: x[1], reverse=True)
        errors_str = ", ".join([f"{k.__name__}: {v}" for k, v in errors if v])
        return message + f"({errors_str})"


def save_crash_context(crash_object, object_name, reason=None):
    from .settings import GeneralSettings

    now = datetime.now()
    index = 0
    while True:
        crash_path = GeneralSettings.root_folder.joinpath(
            object_name + ".%s.pkl" % now.strftime("%Y.%m.%d-%H.%M.%S")
        )
        if index:
            crash_path = crash_path.with_name(
                crash_path.stem + f".{index}" + crash_path.suffix
            )

        if not crash_path.exists():
            break

        index += 1

    crash_object_copy = deepcopy(crash_object)

    if reason:
        try:
            setattr(crash_object_copy, "vcm_crash_reason", reason)
        except AttributeError:
            crash_object_copy = {
                "real_object": crash_object_copy,
                "vcm_crash_reason": reason,
            }

    crash_path.write_bytes(pickle.dumps(crash_object_copy))
    logger.info("Crashed saved as %s", crash_path.as_posix())


def handle_fatal_error_exit(exit_message, exit_code=-1):
    print(Fore.RED + exit_message + Fore.RESET, file=sys.stderr)
    sys.exit(exit_code)

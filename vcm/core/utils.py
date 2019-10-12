import logging
import os
import re
import time
from logging.handlers import RotatingFileHandler
from threading import current_thread

from colorama import Fore, init
from decorator import decorator

from .time_operations import seconds_to_str

logger = logging.getLogger(__name__)
init()


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""

    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


# noinspection PyUnresolvedReferences
class _GetchUnix:
    def __init__(self):
        import tty
        import sys

    def __call__(self):
        import sys
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# noinspection PyUnresolvedReferences
class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt

        return msvcrt.getch()


getch = _Getch()


def secure_filename(filename):
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
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )
    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = "_" + filename

    return filename


class Patterns:
    FILENAME_PATTERN = re.compile('filename=\"?([\w\s\-!$?%^&()_+~=`{\}\[\].;\',]+)\"?')


def exception_exit(exception, to_stderr=False, red=True):
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
        if not isinstance(exception, Exception):
            raise_exception = True

    if raise_exception:
        raise TypeError("exception should be a subclass of Exception")

    message = "%s: %s" % (exception.__class__.__name__, ", ".join(exception.args))

    if red:
        message = Fore.RED + message + Fore.RESET

    if to_stderr:
        return exit(message)
    print(message)
    return exit(-1)


@decorator
def safe_exit(func, to_stderr=False, red=True, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        return exception_exit(exc, to_stderr=to_stderr, red=red)


@decorator
def timing(func, name=None, level=logging.INFO, *args, **kwargs):
    name = name or func.__name__
    t0 = time.time()
    result = func(*args, **kwargs)
    delta_t = time.time() - t0
    logger.log(level, "%s executed in %s", name, seconds_to_str(delta_t))
    return result


_true_set = {"yes", "true", "t", "y", "1"}
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
            backupCount=5,
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


@safe_exit
def setup_vcm():
    more_settings_check()
    configure_logging()

import logging
import os
import re
import time

from decorator import decorator

from vcm.core.time_operations import seconds_to_str

logger = logging.getLogger(__name__)


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
    _windows_device_files = ("CON", "AUX", "COM1", "COM2", "COM3",
                             "COM4", "LPT1", "LPT2", "LPT3", "PRN", "NUL")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )
    if os.name == "nt" and filename and filename.split(".")[0].upper() in _windows_device_files:
        filename = "_" + filename

    return filename


class Patterns:
    FILENAME_PATTERN = re.compile('filename=\"?([\w\s\-!$?%^&()_+~=`{\}\[\].;\',]+)\"?')


def exception_exit(exception):
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
        raise TypeError('exception should be a subclass of Exception')

    exit('%s: %s' % (exception.__class__.__name__, ', '.join(exception.args)))


@decorator

@decorator
def timing(func, name=None, level=logging.INFO, *args, **kwargs):
    name = name or func.__name__
    t0 = time.time()
    result = func(*args, **kwargs)
    delta_t = time.time() - t0
    logger.log(level, '%s executed in %s', name, seconds_to_str(delta_t))
    return result

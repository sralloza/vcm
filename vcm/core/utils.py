"""Utils module."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import os
import pickle
import re
import sys
from threading import Lock, current_thread
from time import time
from traceback import format_exc
from typing import TypeVar, Union
from warnings import warn
from webbrowser import get as get_webbrowser

import click
from colorama import init as start_colorama
from packaging import version
from werkzeug.utils import (
    _windows_device_files as WIN_DEVS,
    secure_filename as _secure_filename,
)

from .exceptions import FilenameWarning
from .modules import Modules
from .time_operations import seconds_to_str

ExceptionClass = TypeVar("ExceptionClass")
logger = logging.getLogger(__name__)
start_colorama()


_def = bytes(1)


def secure_filename(input_filename: str, spaces=True) -> str:
    """Ensures that `input_filename` is a valid filename.

    Args:
        filenainput_filenameme (str): filename to parse.
        spaces (bool, optional): if False, all spaces are replaced with
            underscores. Defaults to True.

    Returns:
        str: filename parsed.
    """

    filename = _secure_filename(input_filename)
    if not spaces:
        return filename

    spaced_filename = filename.replace("_", " ").strip()
    if spaced_filename.split(".")[0].upper() in WIN_DEVS:
        warn("Couldn't allow spaces parsing ", FilenameWarning)
        return _secure_filename(filename)

    return spaced_filename


class Patterns:
    """Stores useful regex patterns for this application."""

    FILENAME = re.compile(r'filename="?([\w\s\-!$%^&()_+=`´\¨{\}\[\].;\',¡¿@#·€]+)"?')

    # https://emailregex.com/
    EMAIL = re.compile(
        r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\""
        r"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b"
        r'\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9]('
        r"?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01"
        r"-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f"
        r"])+)\])"
    )


def timing(_func=_def, *, name=None, level=None, report=True):
    if _func is not _def and not callable(_func):
        raise ValueError("Use keyword arguments in the timing decorator")

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            _name = name or func.__name__
            _level = level or logging.INFO
            t0 = time()
            exception = None
            result = None

            logger.log(_level, "Starting execution of %r", _name)
            try:
                result = func(*args, **kwargs)
            except SystemExit as exc:
                exception = exc
            except Exception as exc:
                exception = exc
            finally:
                if report and ErrorCounter.has_errors():
                    logger.warning(ErrorCounter.report())

            eta = seconds_to_str(time() - t0)  # elapsed time
            logger.log(_level, "%r executed in %s [%r]", _name, eta, result)

            if exception:
                raise exception
            return result

        return inner_wrapper

    if _func is _def:
        return outer_wrapper
    else:
        return outer_wrapper(_func)


def str2bool(value):
    """Returns the boolean as a lowercase string, like json.

    Args:
        value (bool): boolen input.

    Raises:
        TypeError: if the value is neither a string nor a bool.
        ValueError: if the string is invalid.

    Returns:
        str: lowercase string.
    """

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

    raise TypeError("Invalid value type: %r (must be string)" % type(value).__name__)


def configure_logging():
    from vcm.settings import settings

    if not os.environ.get("TESTING", False):
        should_roll_over = settings.log_path.exists()

        fmt = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
        handler = RotatingFileHandler(
            filename=settings.log_path,
            maxBytes=2_500_000,
            encoding="utf-8",
            backupCount=settings.max_logs,
        )

        current_thread().setName("MT")

        if should_roll_over:
            handler.doRollover()

        logging.basicConfig(
            handlers=[handler], level=settings.logging_level, format=fmt
        )

    logging.getLogger("urllib3").setLevel(logging.ERROR)


def setup_vcm():
    from vcm.settings import CheckSettings

    configure_logging()
    CheckSettings.check()


class Printer:
    can_print = True
    _lock = Lock()

    @classmethod
    def reset(cls):
        cls.can_print = True

    @classmethod
    def silence(cls):
        cls.can_print = False

    @classmethod
    def print(cls, *args, color=None, **kwargs):
        if not Modules.should_print():
            return

        if not cls.can_print:
            return

        with cls._lock:
            if color:
                return click.secho(*args, fg=color, bold=True, **kwargs)
            return click.secho(*args, **kwargs)


def check_updates():
    from vcm import __version__ as current_version
    from .networking import connection

    url = "https://api.github.com/repos/sralloza/vcm/tags"
    response = connection.get(url)
    newer_version = version.parse(response.json()[0]["name"])
    current_version = version.parse(current_version)

    if newer_version > current_version:
        Printer.print(
            "Newer version available: %s (current version: %s)"
            % (newer_version, current_version)
        )
        return True

    Printer.print(
        "No updates available (current version: %s, last version: %s)"
        % (current_version, newer_version)
    )
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


class ErrorCounter:
    """Counts the exception class raised and the number of times
    each exception class was raised."""

    error_map = defaultdict(int)

    @classmethod
    def has_errors(cls) -> bool:
        """Checks if some errors were registered.

        Returns:
            bool: True if there is any error, False otherwise.
        """

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
    """Saves the `crash_object` using pickle.

    The filename is formed using `object_name` and the current datetime. If
    the initial filename exists, the name will be incremented (file.log,
    file.1.log, etc.). If reason is passed, it will be appended to `crash_object`
    as an attribute named vcm_crash_reason.

    Args:
        crash_object (object): object to save.
        object_name (str): name of the object to use as base of the filename.
        reason (str, optional): reason of the crash. Defaults to None.
    """

    from vcm.settings import settings

    now = datetime.now()
    index = 0
    while True:
        crash_path = settings.root_folder.joinpath(
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
    """Prints `exit_message` to stderr in light red and exits.

    Args:
        exit_message (str): exit message to print in red.
        exit_code (int, optional): exit code. Defaults to -1.
    """

    print(Fore.RED + str(exit_message) + Fore.RESET, file=sys.stderr)
    sys.exit(exit_code)


def open_http_status_server():
    """Opens the web status server (by default is localhost:8080) in a new
    chrome windows.
    """

    from vcm.settings import settings

    Printer.print("Opening state server")
    chrome_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
    args = f'--new-window "http://localhost:{settings.http_status_port}"'
    get_webbrowser(chrome_path).open_new(args)

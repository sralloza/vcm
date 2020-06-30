import logging
from pathlib import Path

from .utils import str2bool
from .exceptions import SettingsError


def exclude_subjects_ids_setter(*args, **kwargs):
    if kwargs.pop("force", False):
        exclude_list = args[0]
        for index, element in enumerate(exclude_list):
            if not isinstance(element, int):
                raise TypeError(
                    "Element %d (%r) of exclude-subjects-ids must be int, not %s"
                    % (index, element, type(element).__name__)
                )
        return exclude_list
    raise SettingsError("general.exclude-subjects-ids can't be set using the CLI.")


def section_indexing_setter(*args, **kwargs):
    if kwargs.pop("force", False):
        exclude_list = args[0]
        for index, element in enumerate(exclude_list):
            if not isinstance(element, int):
                raise TypeError(
                    "Element %d (%r) of section-indexing must be int, not %s"
                    % (index, element, type(element).__name__)
                )
        return exclude_list
    raise SettingsError("download.section-indexing can't be set using the CLI")


class Checkers:
    @staticmethod
    def logging(item):
        if isinstance(item, str):
            item = item.upper()

        return item in (
            "NOTSET",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
            50,
            40,
            30,
            20,
            10,
        )

    @staticmethod
    def bool(item):
        return isinstance(item, bool)

    @staticmethod
    def int(item):
        if isinstance(item, bool):
            return False
        return isinstance(item, int)

    @staticmethod
    def str(item):
        return isinstance(item, str)

    @staticmethod
    def list(item):
        return isinstance(item, list)

    @staticmethod
    def float(item):
        return isinstance(item, float)


class Setters:
    @staticmethod
    def int(item, force=False):
        return int(item)

    @staticmethod
    def list(item, force=False):
        return list(item)

    @staticmethod
    def str(item, force=False):
        return str(item)


defaults = {
    "general": {
        "root-folder": "insert-root-folder",
        "logging-level": "INFO",
        "timeout": 30,
        "retries": 10,
        "login-retries": 5,
        "logout-retries": 5,
        "max-logs": 5,
        "exclude-subjects-ids": [],
        "http-status-port": 8080,
    },
    "download": {
        "forum-subfolders": True,
        "section-indexing": [],
        "secure-section-filename": False,
    },
    "notify": {"email": "insert-email"},
}

checkers = {
    "general": {
        "root-folder": Checkers.str,
        "logging-level": Checkers.logging,
        "timeout": Checkers.int,
        "retries": Checkers.int,
        "login-retries": Checkers.int,
        "logout-retries": Checkers.int,
        "max-logs": Checkers.int,
        "exclude-subjects-ids": Checkers.list,
        "http-status-port": Checkers.int,
    },
    "download": {
        "forum-subfolders": Checkers.bool,
        "section-indexing": Checkers.list,
        "secure-section-filename": Checkers.bool,
    },
    "notify": {"email": Checkers.str},
}

# Transforms TOML → saved
constructors = {
    "general": {
        "root-folder": Path,
        "logging-level": logging._nameToLevel.__getitem__,
        "timeout": int,
        "retries": int,
        "login-retries": int,
        "logout-retries": int,
        "max-logs": int,
        "exclude-subjects-ids": list,
        "http-status-port": int,
    },
    "download": {
        "forum-subfolders": str2bool,
        "section-indexing": list,
        "secure-section-filename": str2bool,
    },
    "notify": {"email": str},
}

# Transforms str → TOML
setters = {
    "general": {
        "root-folder": str,
        "logging-level": str,
        "timeout": int,
        "retries": int,
        "login-retries": int,
        "logout-retries": int,
        "max-logs": int,
        "http-status-port": int,
        "exclude-subjects-ids": exclude_subjects_ids_setter,
    },
    "download": {
        "forum-subfolders": str2bool,
        "section-indexing": section_indexing_setter,
        "secure-section-filename": str2bool,
    },
    "notify": {"email": str},
}

import logging
from pathlib import Path

from .utils import str2bool
from .exceptions import SettingsError


def exclude_subjects_ids_setter(*args, **kwargs):
    if kwargs.pop("force", False):
        exclude_list = args[0]
        for element in exclude_list:
            if not isinstance(element, int):
                raise TypeError(
                    "%r element of exclude-subjects-ids must be int, not %s"
                    % (element, type(element).__name__)
                )
        return exclude_list
    raise SettingsError("general.exclude-subjects-ids can't be set using the CLI.")


def section_indexing_setter(*args, **kwargs):
    if kwargs.pop("force", False):
        exclude_list = args[0]
        for element in exclude_list:
            if not isinstance(element, int):
                raise TypeError(
                    "%r element of section-indexing must be int, not %s"
                    % (element, type(element).__name__)
                )
        return exclude_list
    raise SettingsError("download.section-indexing can't be set using the CLI")


class Checkers:
    @staticmethod
    def logging(item):
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


defaults = {
    "general": {
        "root-folder": "insert-root-folder",
        "logging-level": "INFO",
        "timeout": 30,
        "retries": 10,
        "max-logs": 5,
        "exclude-subjects-ids": [],
    },
    "download": {
        "forum-subfolders": True,
        "section-indexing": [],
        "secure-section-filename": False,
    },
    "notify": {"use-base64-icons": False, "email": "insert-email"},
}

checkers = {
    "general": {
        "root-folder": Checkers.str,
        "logging-level": Checkers.logging,
        "timeout": Checkers.int,
        "retries": Checkers.int,
        "max-logs": Checkers.int,
        "exclude-subjects-ids": Checkers.list,
    },
    "download": {
        "forum-subfolders": Checkers.bool,
        "section-indexing": Checkers.list,
        "secure-section-filename": Checkers.bool,
    },
    "notify": {"use-base64-icons": Checkers.bool, "email": Checkers.str},
}

# Transforms TOML → saved
constructors = {
    "general": {
        "root-folder": Path,
        "logging-level": logging._nameToLevel.__getitem__,
        "timeout": int,
        "retries": int,
        "max-logs": int,
        "exclude-subjects-ids": list,
    },
    "download": {
        "forum-subfolders": str2bool,
        "section-indexing": list,
        "secure-section-filename": str2bool,
    },
    "notify": {"use-base64-icons": str2bool, "email": str},
}

# Transforms str → TOML
setters = {
    "general": {
        "root-folder": str,
        "logging-level": str,
        "timeout": int,
        "retries": int,
        "max-logs": int,
        "exclude-subjects-ids": exclude_subjects_ids_setter,
    },
    "download": {
        "forum-subfolders": str2bool,
        "section-indexing": section_indexing_setter,
        "secure-section-filename": str2bool,
    },
    "notify": {"use-base64-icons": str2bool, "email": str},
}

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
    "notify": {"email": "insert-email"},
}

types = {
    "general": {
        "root-folder": str,
        "logging-level": ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        "timeout": int,
        "retries": int,
        "max-logs": int,
        "exclude-subjects-ids": list,
    },
    "download": {
        "forum-subfolders": bool,
        "section-indexing": list,
        "secure-section-filename": False,
    },
    "notify": {¡"email": str},
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
    "notify": {¡"email": str},
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
    "notify": {"email": str},
}

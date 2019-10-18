import logging
from pathlib import Path

from .utils import str2bool
from .exceptions import SettingsError


def exclude_urls_setter(*args, **kwargs):
    raise SettingsError("general.exclude-urls can't be set using the CLI.")


defaults = {
    "general": {
        "root-folder": "insert-root-folder",
        "logging-level": "INFO",
        "timeout": 30,
        "retries": 10,
        "exclude-urls": [],
    },
    "download": {"forum-subfolders": True},
    "notify": {"use-base64-icons": False, "email": "insert-email"},
}

types = {
    "general": {
        "root-folder": str,
        "logging-level": ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        "timeout": int,
        "retries": int,
        "exclude-urls": list,
    },
    "download": {"forum-subfolders": bool},
    "notify": {"use-base64-icons": bool, "email": str},
}

# Transforms TOML → saved
constructors = {
    "general": {
        "root-folder": Path,
        "logging-level": logging._nameToLevel.__getitem__,
        "timeout": int,
        "retries": int,
        "exclude-urls": list,
    },
    "download": {"forum-subfolders": str2bool},
    "notify": {"use-base64-icons": str2bool, "email": str},
}

# Transforms str → TOML
setters = {
    "general": {
        "root-folder": str,
        "logging-level": str,
        "timeout": int,
        "retries": int,
        "exclude-urls": exclude_urls_setter,
    },
    "download": {"forum-subfolders": str2bool},
    "notify": {"use-base64-icons": str2bool, "email": str},
}


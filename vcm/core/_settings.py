import logging
from pathlib import Path

from .utils import str2bool

defaults = {
    "general": {
        "root-folder": "insert-root-folder",
        "logging-level": "INFO",
        "timeout": 30,
        "retries": 10,
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
    },
    "download": {"forum-subfolders": bool},
    "notify": {"use-base64-icons": bool, "email": str},
}

constructors = {
    "general": {
        "root-folder": Path,
        "logging-level": logging._nameToLevel.__getitem__,
        "timeout": int,
        "retries": int,
    },
    "download": {"forum-subfolders": str2bool},
    "notify": {"use-base64-icons": str2bool, "email": str},
}

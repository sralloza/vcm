from pathlib import Path

import toml

# IMPORTED FROM vcm.core._settings
# TODO: auto import
SETTINGS_DEFAULTS = {
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

CREDENTIALS_DEFAULT = {
    "VirtualCampus": {"username": "e12345678Z", "password": "password-vc"},
    "Email": {
        "username": "email@gmail.com",
        "password": "password-email",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
    },
}


def pytest_configure(config):
    settings_path: Path = Path.home() / "vcm-settings.toml"
    credentials_path: Path = Path.home() / "vcm-credentials.toml"

    if not settings_path.exists():
        with settings_path.open("wt") as file_handler:
            toml.dump(SETTINGS_DEFAULTS, file_handler)

    if not credentials_path.exists():
        with credentials_path.open("wt") as file_handler:
            toml.dump(CREDENTIALS_DEFAULT, file_handler)

import os
from pathlib import Path

import pytest
import toml


def get_settings_defaults():
    path = Path(__file__).parent.with_name("vcm").joinpath("core/_settings.py")

    outfile = []
    with path.open("rt", encoding="utf-8") as infile:
        copy = False
        for line in infile:
            if line.strip() == "defaults = {":
                copy = True
                outfile.append("{\n")
                continue
            elif line.strip() == "}":
                if copy:
                    outfile.append(line)
                copy = False
                continue
            elif copy:
                outfile.append(line)
    return eval("".join(outfile))


# IMPORTED FROM vcm.core._settings
SETTINGS_DEFAULTS = get_settings_defaults()

CREDENTIALS_DEFAULT = {
    "VirtualCampus": {"username": "e12345678Z", "password": "password-vc"},
    "Email": {
        "username": "email@gmail.com",
        "password": "password-email",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
    },
}


def pytest_configure():
    settings_path: Path = Path.home() / "vcm-settings.toml"
    credentials_path: Path = Path.home() / "vcm-credentials.toml"

    if not settings_path.exists():
        with settings_path.open("wt") as file_handler:
            toml.dump(SETTINGS_DEFAULTS, file_handler)

    if not credentials_path.exists():
        with credentials_path.open("wt") as file_handler:
            toml.dump(CREDENTIALS_DEFAULT, file_handler)

    os.environ["TESTING"] = "True"


@pytest.fixture(scope="session", autouse=True)
def check_settings():
    from vcm.core._settings import defaults

    yield
    assert defaults == SETTINGS_DEFAULTS

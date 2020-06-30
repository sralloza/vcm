from ast import literal_eval
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
            if line.strip() == "}":
                if copy:
                    outfile.append(line)
                copy = False
                continue
            if copy:
                outfile.append(line)

    return literal_eval("".join(outfile))


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


test_settings_path: Path = Path.home() / "test-vcm-settings.toml"
test_credentials_path: Path = Path.home() / "test-vcm-credentials.toml"
test_root_folder = Path.home() / "vcm-test-data"


def pytest_configure():
    SETTINGS_DEFAULTS["general"]["root-folder"] = test_root_folder.as_posix()
    SETTINGS_DEFAULTS["notify"]["email"] = "testing@example.com"

    # if not test_settings_path.exists():
    with test_settings_path.open("wt") as file_handler:
        toml.dump(SETTINGS_DEFAULTS, file_handler)

    # if not test_credentials_path.exists():
    with test_credentials_path.open("wt") as file_handler:
        toml.dump(CREDENTIALS_DEFAULT, file_handler)

    os.environ["TESTING"] = "True"


@pytest.fixture(scope="session", autouse=True)
def check_settings():
    from vcm.core._settings import defaults

    assert isinstance(defaults, dict)

    yield
    import shutil

    test_settings_path.unlink()
    test_credentials_path.unlink()
    shutil.rmtree(test_root_folder, ignore_errors=True)

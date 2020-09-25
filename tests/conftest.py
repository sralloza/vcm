from functools import lru_cache
import json
import os
from pathlib import Path
from tempfile import gettempdir

import pytest
from ruamel.yaml import YAML


@lru_cache(maxsize=10)
def get_settings_defaults():
    path = Path(__file__).parent.with_name("vcm").joinpath("data/defaults.json")
    return json.loads(path.read_text())


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

settings_folder = Path(gettempdir())
test_settings_path: Path = settings_folder / "test-vcm-settings.yaml"
test_credentials_path: Path = settings_folder / "test-vcm-credentials.yaml"
test_root_folder = settings_folder / "vcm-test-data"


@pytest.fixture
def get_test_data():
    data_path = Path(__file__).with_name("data")

    def wrapper(name):
        return data_path.joinpath(name).read_text(encoding="utf8")

    return wrapper


def pytest_configure():
    SETTINGS_DEFAULTS["root-folder"] = test_root_folder.as_posix()
    SETTINGS_DEFAULTS["email"] = "testing@example.com"

    yaml = YAML()

    # if not test_settings_path.exists():
    with test_settings_path.open("wt") as file_handler:
        yaml.dump(SETTINGS_DEFAULTS, file_handler)

    # if not test_credentials_path.exists():
    with test_credentials_path.open("wt") as file_handler:
        yaml.dump(CREDENTIALS_DEFAULT, file_handler)

    os.environ["TESTING"] = "True"


@pytest.fixture(scope="session", autouse=True)
def check_settings():
    defaults = get_settings_defaults()

    assert isinstance(defaults, dict)

    yield
    import shutil

    test_settings_path.unlink()
    test_credentials_path.unlink()
    shutil.rmtree(test_root_folder, ignore_errors=True)

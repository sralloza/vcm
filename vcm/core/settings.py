import os
from copy import deepcopy
from pathlib import Path

import toml
from colorama.ansi import Fore

from ._settings import constructors, defaults, types
from .exceptions import InvalidSettingsFileError
from .utils import safe_exit


def extend_settings_class_name(base_settings_class_name):
    return "_" + base_settings_class_name.capitalize() + "Settings"


def save_settings():
    settings_classes = list(settings_name_to_class.values())
    toml_data = {}

    for cls in settings_classes:
        name = cls.__class__.__name__.lower().replace("_", "").replace("settings", "")
        toml_data[name] = cls

    os.environ["VCM_DISABLE_CONSTRUCTS"] = "True"
    with CoreSettings.config_path.open("wt") as file_handler:
        toml.dump(toml_data, file_handler)

    del os.environ["VCM_DISABLE_CONSTRUCTS"]


def settings_to_string():
    output = "- core:\n"
    for key, value in CoreSettings.items():
        # CoreSettings attributes are all pathlib.Path, so using
        # repr will return PosixPath(...) or WindowsPath(...)
        output += "    %s: %s\n" % (key, value)

    output += "\n- general:\n"
    for key, value in GeneralSettings.items():
        output += "    %s: %r\n" % (key, value)

    output += "\n- download:\n"

    for key, value in DownloadSettings.items():
        output += "    %s: %r\n" % (key, value)

    output += "\n- notify:\n"

    for key, value in NotifySettings.items():
        output += "    %s: %r\n" % (key, value)

    return output


class _CoreSettings(dict):
    config_path: Path = Path.home() / "vcm-config.toml"
    credentials_path: Path = Path.home() / "vcm-credentials.toml"

    def __init__(self):
        super().__init__(
            {
                "config_path": _CoreSettings.config_path,
                "credentials_path": _CoreSettings.credentials_path,
            }
        )


CoreSettings = _CoreSettings()


def create_default():
    with CoreSettings.config_path.open("wt") as file_handler:
        toml.dump(defaults, file_handler)


class MetaSettings(type):
    require = []

    try:
        with Path(CoreSettings.config_path) as file_handler:
            real_dict = toml.load(file_handler)
    except FileNotFoundError:
        create_default()
        exit(
            Fore.RED
            + "Missing settings file, created sample (%s)" % CoreSettings.config_path
            + Fore.RESET
        )

    def __new__(mcs, name, bases, attrs, **kwargs):
        lookup_name = name.lower().replace("_", "").replace("settings", "")
        if "base" not in name.lower():
            for arg in mcs.require:
                if arg not in attrs:
                    raise Exception("Expected %r to have %s attribute" % (name, arg))

            try:
                attrs["def_dict"] = deepcopy(defaults)[lookup_name]
                attrs["def_dict"].update(mcs.real_dict[lookup_name])
                attrs["types_dict"] = types[lookup_name]
                attrs["constructors"] = constructors[lookup_name]
            except KeyError as exc:
                raise InvalidSettingsFileError(",".join(exc))

        return super().__new__(mcs, name, bases, attrs)

    def __str__(cls, *args):
        return cls().__str__()


class BaseSettings(dict, metaclass=MetaSettings):
    def __new__(cls):
        self = super().__new__(cls)
        self.__init__(cls.def_dict)

        return self

    def __getitem__(self, key):
        key = self._parse_key(key)
        if os.environ.get("VCM_DISABLE_CONSTRUCTS"):
            return super().__getitem__(key)
        return self.constructors[key](super().__getitem__(key))

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        key = self._parse_key(key)
        expected_type = self.types_dict[key]
        if isinstance(expected_type, tuple):
            assert value in expected_type
        else:
            assert isinstance(value, expected_type)

        super().__setitem__(key, value)
        save_settings()

    @staticmethod
    def _parse_key(key: str):
        return key.lower().replace("_", "-")


class _GeneralSettings(BaseSettings):
    @property
    def root_folder(self):
        return self["root-folder"]

    @property
    def logging_level(self) -> str:
        return self["logging-level"]

    @property
    def timeout(self) -> int:
        return self["timeout"]

    @property
    def retries(self) -> int:
        return self["retries"]

    # DEPENDANT SETTINGS

    @property
    def logs_folder(self) -> Path:
        return self.root_folder / ".logs"

    @property
    def log_path(self) -> Path:
        return self.logs_folder / "vcm.log"

    @property
    def database_path(self) -> Path:
        return self.root_folder / "links.db"


class _DownloadSettings(BaseSettings):
    @property
    def forum_subfolders(self) -> bool:
        return self["forum_subfolders"]


class _NotifySettings(BaseSettings):
    @property
    def use_base64_icons(self) -> bool:
        return self["use-base64-icons"]

    @property
    def email(self) -> str:
        return self["email"]


GeneralSettings = _GeneralSettings()
DownloadSettings = _DownloadSettings()
NotifySettings = _NotifySettings()

SETTINGS_CLASSES = ["general", "download", "notify"]


settings_name_to_class = {
    "general": GeneralSettings,
    "download": DownloadSettings,
    "notify": NotifySettings,
}
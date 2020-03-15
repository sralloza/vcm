import os
from copy import deepcopy
from pathlib import Path
from typing import List

import toml
from colorama.ansi import Fore

from vcm.core.exceptions import (
    AlreadyExcludedError,
    AlreadyIndexedError,
    NotExcludedError,
    NotIndexedError,
)

from ._settings import checkers, constructors, defaults, setters
from .exceptions import InvalidSettingsFileError


def extend_settings_class_name(base_settings_class_name):
    return "_" + base_settings_class_name.capitalize() + "Settings"


def save_settings():
    settings_classes = list(settings_name_to_class.values())
    toml_data = {}

    for cls in settings_classes:
        name = cls.__class__.__name__.lower().replace("_", "").replace("settings", "")
        toml_data[name] = cls

    os.environ["VCM_DISABLE_CONSTRUCTS"] = "True"
    with CoreSettings.settings_path.open("wt") as file_handler:
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


def section_index(subject_id: int):
    if subject_id in DownloadSettings.section_indexing_ids:
        raise AlreadyIndexedError(
            "Subject ID '%d' is already section-indexed" % subject_id
        )

    index = list(DownloadSettings.section_indexing_ids)
    index.append(subject_id)
    index = list(set(index))
    index.sort()
    DownloadSettings.__setitem__("section-indexing", index, force=True)


def un_section_index(subject_id: int):
    if subject_id not in DownloadSettings.section_indexing_ids:
        raise NotIndexedError("Subject ID '%d' is not section-indexed" % subject_id)

    index = list(DownloadSettings.section_indexing_ids)
    index.remove(subject_id)
    index = list(set(index))
    index.sort()
    DownloadSettings.__setitem__("section_indexing", index, force=True)


def exclude(subject_id: int):
    if subject_id in GeneralSettings.exclude_subjects_ids:
        raise AlreadyExcludedError("Subject ID '%d' is already excluded" % subject_id)

    all_excluded = list(GeneralSettings.exclude_subjects_ids)
    all_excluded.append(subject_id)
    all_excluded = list(set(all_excluded))
    all_excluded.sort()
    GeneralSettings.__setitem__("exclude-subjects-ids", all_excluded, force=True)


def include(subject_id: int):
    if subject_id not in GeneralSettings.exclude_subjects_ids:
        raise NotExcludedError("Subject ID '%d' is not excluded" % subject_id)

    all_excluded = list(GeneralSettings.exclude_subjects_ids)
    all_excluded.remove(subject_id)
    all_excluded = list(set(all_excluded))
    all_excluded.sort()
    GeneralSettings.__setitem__("exclude-subjects-ids", all_excluded, force=True)


class _CoreSettings(dict):
    settings_path: Path = Path.home() / "vcm-settings.toml"
    credentials_path: Path = Path.home() / "vcm-credentials.toml"

    def __init__(self):
        super().__init__(
            {
                "settings_path": _CoreSettings.settings_path,
                "credentials_path": _CoreSettings.credentials_path,
            }
        )


CoreSettings = _CoreSettings()


def create_default():
    with CoreSettings.settings_path.open("wt") as file_handler:
        toml.dump(defaults, file_handler)


class MetaSettings(type):
    require = []

    try:
        with Path(CoreSettings.settings_path) as file_handler:
            real_dict = toml.load(file_handler)
    except FileNotFoundError:
        create_default()
        exit(
            Fore.RED
            + "Missing settings file, created sample (%s)" % CoreSettings.settings_path
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
                attrs["checkers_dict"] = checkers[lookup_name]
                attrs["constructors"] = constructors[lookup_name]
                attrs["setters"] = setters[lookup_name]
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

    def __setitem__(self, key, value, force=False):
        # TODO: add support to check types like List[int]
        key = self._parse_key(key)

        # FIXME: think what to do with the check type call
        # self.check_value_type(key, value)
        try:
            # FIXME: figure out what did force do
            value = self.setters[key](value) #, force=force)
        except Exception as exc:
            if "'force'" not in exc.args[0]:
                checker = self.checkers_dict[key]
                raise TypeError(
                    "Invalid value for %s.%s: %r [Checkers.%s]"
                    % (self.__class__.__name__.strip("_"), key, value, checker.__name__)
                )
            value = self.setters[key](value)
        super().__setitem__(key, value)
        save_settings()

    def check_value_type(self, key, value):
        # TODO: add support to check types like List[int]

        checker = self.checkers_dict[key]
        result = checker(value)
        if not result:
            raise TypeError(
                "Invalid value for %s.%s: %r [Checkers.%s]"
                % (self.__class__.__name__.strip("_"), key, value, checker.__name__)
            )
        return True

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

    @property
    def max_logs(self) -> int:
        return self["max-logs"]

    @property
    def exclude_subjects_ids(self) -> List[int]:
        return self["exclude-subjects-ids"]

    @property
    def exclude_urls(self) -> List[str]:
        template = "https://campusvirtual.uva.es/course/view.php?id=%d"
        return [template % x for x in self.exclude_subjects_ids]

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
        return self["forum-subfolders"]

    @property
    def section_indexing_ids(self) -> List[int]:
        return self["section-indexing"]

    @property
    def section_indexing_urls(self) -> List[str]:
        template = "https://campusvirtual.uva.es/course/view.php?id=%d"
        return [template % x for x in self.section_indexing_ids]

    @property
    def secure_section_filename(self) -> bool:
        return self["secure-section-filename"]


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


def check_settings_type():
    os.environ["VCM_DISABLE_CONSTRUCTS"] = "True"
    for settings_class in settings_name_to_class.values():
        for setting in settings_class:
            checker = settings_class.checkers_dict[setting]
            result = checker(settings_class[setting])

            if not result:
                del os.environ["VCM_DISABLE_CONSTRUCTS"]
                raise TypeError(
                    "Invalid value for %s.%s: %r [Checkers.%s]"
                    % (
                        settings_class.__class__.__name__.strip("_"),
                        setting,
                        settings_class[setting],
                        checker.__name__,
                    )
                )

    del os.environ["VCM_DISABLE_CONSTRUCTS"]


check_settings_type()

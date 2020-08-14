import json
import os
from pathlib import Path
from tempfile import gettempdir
from typing import List

from ruamel.yaml import YAML

from vcm.core.exceptions import SettingsError
from vcm.core.utils import handle_fatal_error_exit, str2bool

from .core.exceptions import (
    AlreadyExcludedError,
    AlreadyIndexedError,
    NotExcludedError,
    NotIndexedError,
)
from .core.utils import MetaSingleton, Patterns, str2bool


def save_settings():
    CheckSettings.check()
    settings.update_config()

    yaml = YAML()
    with settings.settings_path.open("wt") as file:
        yaml.dump(settings.config, file)


def settings_to_string():
    output = "- settings:\n"
    for key in ["credentials_path", "settings_path"]:
        value = getattr(settings, key)
        key = key.replace("_", "-")
        output += "    %s: %s\n" % (key, value)

    for key, value in settings.items():
        key = key.replace("_", "-")
        output += "    %s: %r\n" % (key, value)

    return output


def section_index(subject_id: int):
    if subject_id in settings.section_indexing_ids:
        raise AlreadyIndexedError(
            "Subject ID '%d' is already section-indexed" % subject_id
        )

    index = list(settings.section_indexing_ids)
    index.append(subject_id)
    index = list(set(index))
    index.sort()
    settings["section-indexing-ids"] = index


def un_section_index(subject_id: int):
    if subject_id not in settings.section_indexing_ids:
        raise NotIndexedError("Subject ID '%d' is not section-indexed" % subject_id)

    index = list(settings.section_indexing_ids)
    index.remove(subject_id)
    index = list(set(index))
    index.sort()
    settings["section-indexing-ids"] = index


def exclude(subject_id: int):
    if subject_id in settings.exclude_subjects_ids:
        raise AlreadyExcludedError("Subject ID '%d' is already excluded" % subject_id)

    all_excluded = list(settings.exclude_subjects_ids)
    all_excluded.append(subject_id)
    all_excluded = list(set(all_excluded))
    all_excluded.sort()
    settings["exclude-subjects-ids"] = all_excluded


def include(subject_id: int):
    if subject_id not in settings.exclude_subjects_ids:
        raise NotExcludedError("Subject ID '%d' is not excluded" % subject_id)

    all_excluded = list(settings.exclude_subjects_ids)
    all_excluded.remove(subject_id)
    all_excluded = list(set(all_excluded))
    all_excluded.sort()
    settings["exclude-subjects-ids"] = all_excluded


class Settings(dict, metaclass=MetaSingleton):
    if os.getenv("TESTING", False):
        settings_folder = Path(gettempdir())
        _preffix = "test-"
    else:
        settings_folder = Path.home()
        _preffix = ""

    credentials_path = settings_folder.joinpath(_preffix + "vcm-credentials.yaml")
    settings_path = settings_folder.joinpath(_preffix + "vcm-settings.yaml")
    config = {}

    _template = "https://campusvirtual.uva.es/course/view.php?id=%d"

    @classmethod
    def gen_subject_url(cls, subject_id: int) -> str:
        return cls._template % subject_id

    def exclude_subjects_ids_setter(self):
        raise SettingsError("exclude-subjects-ids can't be set using the CLI.")

    def section_indexing_setter(self):
        raise SettingsError("section-indexing can't be set using the CLI")

    transforms = {
        "email": str,
        "exclude-subjects-ids": exclude_subjects_ids_setter,
        "forum-subfolders": str2bool,
        "http-status-port": int,
        "http-status-tickrate": int,
        "login-retries": int,
        "logout-retries": int,
        "max-logs": int,
        "retries": int,
        "root-folder": str,
        "section-indexing-ids": section_indexing_setter,
        "secure-section-filename": str2bool,
        "timeout": int,
    }

    def __init__(self):
        self.update_config()

    def __setitem__(self, k, v) -> None:
        k = k.replace("_", "-").lower()
        self.config[k] = v
        save_settings()

    def __getitem__(self, k):
        k = k.replace("_", "-").lower()
        return self.config[k]

    @classmethod
    def get_current_config(cls):
        if not cls.settings_path.is_file():
            cls.create_example()
            return handle_fatal_error_exit("Settings file does not exist")

        yaml = YAML(typ="safe")
        return yaml.load(cls.settings_path.read_text())

    @classmethod
    def create_example(cls):
        yaml = YAML()
        data = cls.get_defaults()
        with cls.settings_path.open("wt", encoding="utf-8") as file_handler:
            yaml.dump(data, file_handler)

    @staticmethod
    def get_defaults():
        defaults_path = Path(__file__).with_name("data") / "defaults.json"
        return json.loads(defaults_path.read_text())

    def update_config(self):
        if not self.config:
            self.__class__.config = self.get_defaults()
            self.__class__.config.update(self.get_current_config())
        super().__init__(self.config)

    @property
    def root_folder(self):
        return Path(self["root-folder"])

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
    def login_retries(self) -> int:
        return self["login-retries"]

    @property
    def logout_retries(self) -> int:
        return self["logout-retries"]

    @property
    def max_logs(self) -> int:
        return self["max-logs"]

    @property
    def exclude_subjects_ids(self) -> List[int]:
        return self["exclude-subjects-ids"]

    @property
    def http_status_port(self) -> int:
        return self["http-status-port"]

    @property
    def http_status_tickrate(self) -> float:
        return self["http-status-tickrate"]

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

    @property
    def exclude_urls(self) -> List[str]:
        return [self.gen_subject_url(x) for x in self.exclude_subjects_ids]

    @property
    def forum_subfolders(self) -> bool:
        return self["forum-subfolders"]

    @property
    def section_indexing_ids(self) -> List[int]:
        return self["section-indexing-ids"]

    @property
    def section_indexing_urls(self) -> List[str]:
        return [self.gen_subject_url(x) for x in self.section_indexing_ids]

    @property
    def secure_section_filename(self) -> bool:
        return self["secure-section-filename"]

    @property
    def email(self) -> str:
        return self["email"]


settings = Settings()


class CheckSettings:
    @classmethod
    def check(cls):
        for attribute in dir(cls):
            if not attribute.startswith("check_"):
                continue
            check = getattr(cls, attribute)
            check()

    @classmethod
    def check_root_folder(cls):
        if not isinstance(settings["root-folder"], str):
            raise TypeError("Setting root-folder must be str")
        if not isinstance(settings.root_folder, Path):
            raise TypeError("Wrapper of setting root-folder must return Path")
        if settings["root-folder"] == "insert-root-folder":
            raise ValueError("Must set root-folder setting")
        settings.root_folder.mkdir(parents=True, exist_ok=True)

    @classmethod
    def check_logs_folder(cls):
        if not isinstance(settings.logs_folder, Path):
            raise TypeError("Wrapper of logs folder must return Path")
        settings.logs_folder.mkdir(parents=True, exist_ok=True)

    @classmethod
    def check_logging_level(cls):
        if not isinstance(settings.logging_level, str):
            raise TypeError("Setting logging-level must be str")

        from logging import _levelToName

        if settings.logging_level not in _levelToName.values():
            logging_level = settings.logging_level.upper()
            if logging_level not in _levelToName.values():
                raise ValueError(
                    "Setting logging-level must be one of %s" % _levelToName.values()
                )
            settings["logging-level"] = logging_level

    @classmethod
    def check_timeout(cls):
        if not isinstance(settings.timeout, int):
            try:
                timeout = int(settings.timeout)
                settings["timeout"] = timeout
            except ValueError:
                raise TypeError("Setting timeout must be int")
        if settings.timeout < 0:
            raise ValueError("Setting timeout must be positive")

    @classmethod
    def check_retries(cls):
        if not isinstance(settings.retries, int):
            try:
                retries = int(settings.retries)
                settings["retries"] = retries
            except ValueError:
                raise TypeError("Setting retries must be int")
        if settings.retries < 0:
            raise ValueError("Setting retries must be positive")

    @classmethod
    def check_login_retries(cls):
        if not isinstance(settings.login_retries, int):
            try:
                login_retries = int(settings.login_retries)
                settings["login-retries"] = login_retries
            except ValueError:
                raise TypeError("Setting login-retries must be int")
        if settings.login_retries < 0:
            raise ValueError("Setting login-retries must be positive")

    @classmethod
    def check_logout_retries(cls):
        if not isinstance(settings.logout_retries, int):
            try:
                logout_retries = int(settings.logout_retries)
                settings["logout-retries"] = logout_retries
            except ValueError:
                raise TypeError("Setting logout-retries must be int")
        if settings.logout_retries < 0:
            raise ValueError("Setting logout-retries must be positive")

    @classmethod
    def check_max_logs(cls):
        if not isinstance(settings.max_logs, int):
            try:
                max_logs = int(settings.max_logs)
                settings["max-logs"] = max_logs
            except ValueError:
                raise TypeError("Setting max-logs must be int")
        if settings.max_logs < 0:
            raise ValueError("Setting max-logs must be positive")

    @classmethod
    def check_exclude_subjects_ids(cls):
        if not isinstance(settings.exclude_subjects_ids, list):
            raise TypeError("Setting exclude-subjects-ids must be list of integers")
        for subject_id in settings.exclude_subjects_ids:
            if not isinstance(subject_id, int):
                raise TypeError(
                    "All elements of setting exclude-subjects-ids must be integers"
                )
            if subject_id < 0:
                raise ValueError(
                    "All elements of setting exclude-subjects-ids must be positive"
                )

    @classmethod
    def check_http_status_port(cls):
        if not isinstance(settings.http_status_port, int):
            try:
                http_status_port = int(settings.http_status_port)
                settings["http_status_port"] = http_status_port
            except ValueError:
                raise TypeError("Setting http-status-port must be int")
        if settings.http_status_port < 0:
            raise ValueError("Setting http-status-port must be positive")

    @classmethod
    def check_http_status_tickrate(cls):
        if not isinstance(settings.http_status_tickrate, int):
            try:
                http_status_tickrate = int(settings.http_status_tickrate)
                settings["http_status_tickrate"] = http_status_tickrate
            except ValueError:
                raise TypeError("Setting http-status-tickrate must be int")
        if settings.http_status_tickrate < 0:
            raise ValueError("Setting http-status-tickrate must be positive")

    @classmethod
    def check_forum_subfolders(cls):
        if not isinstance(settings.forum_subfolders, bool):
            try:
                forum_subfolders = str2bool(settings.forum_subfolders)
                settings["forum_subfolders"] = forum_subfolders
            except ValueError:
                raise TypeError("Setting forum-subfolders must be a boolean")

    @classmethod
    def check_section_indexing_ids(cls):
        if not isinstance(settings.section_indexing_ids, list):
            raise TypeError("Setting section-indexing must be list of integers")
        for subject_id in settings.section_indexing_ids:
            if not isinstance(subject_id, int):
                raise TypeError(
                    "All elements of setting section-indexing must be integers"
                )
            if subject_id < 0:
                raise ValueError(
                    "All elements of setting section-indexing must be positive"
                )

    @classmethod
    def check_secure_section_filename(cls):
        if not isinstance(settings.secure_section_filename, bool):
            try:
                secure_section_filename = str2bool(settings.secure_section_filename)
                settings["secure_section_filename"] = secure_section_filename
            except ValueError:
                raise TypeError("Setting secure-section-filename must be bool")

    @classmethod
    def check_email(cls):
        if settings.email == "insert-email":
            raise ValueError("Must set email setting")
        if not isinstance(settings.email, str):
            raise TypeError("Setting email must be str")
        if not Patterns.EMAIL.search(settings.email):
            raise ValueError("Setting email is not a valid email")


CheckSettings.check()

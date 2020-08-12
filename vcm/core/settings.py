import json
from pathlib import Path
from typing import List

from ruamel.yaml import YAML

from vcm.core.exceptions import SettingsError
from vcm.core.utils import handle_fatal_error_exit, str2bool

from .exceptions import (
    AlreadyExcludedError,
    AlreadyIndexedError,
    NotExcludedError,
    NotIndexedError,
)
from .utils import MetaSingleton, Patterns


def save_settings():
    CheckSettings.check()
    settings.update_instance_config()

    yaml = YAML()
    with settings.settings_path.open("wt") as file:
        yaml.dump(settings.config, file)


def settings_to_string():
    output = "- settings:\n"
    for key in ["credentials_path", "settings_path"]:
        value = getattr(settings, key)
        output += "    %s: %s\n" % (key, value)

    for key, value in settings.items():
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
    settings["section-indexing"] = index


def un_section_index(subject_id: int):
    if subject_id not in settings.section_indexing_ids:
        raise NotIndexedError("Subject ID '%d' is not section-indexed" % subject_id)

    index = list(settings.section_indexing_ids)
    index.remove(subject_id)
    index = list(set(index))
    index.sort()
    settings["section-indexing"] = index


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


def create_default():
    raise NotImplementedError


class Settings(dict, metaclass=MetaSingleton):
    credentials_path = Path("~").expanduser() / "vcm-credentials.yaml"
    settings_path = Path("~").expanduser() / "vcm-settings.yaml"
    config = None

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
        "section-indexing": section_indexing_setter,
        "secure-section-filename": str2bool,
        "timeout": int,
    }

    def __init__(self):
        self.update_instance_config()

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
        print(data)
        with cls.settings_path.open("wt", encoding="utf-8") as file_handler:
            yaml.dump(data, file_handler)

    @classmethod
    def update_config(cls):
        cls.config = cls.get_current_config()

    @staticmethod
    def get_defaults():
        defaults_path = Path(__file__).with_name("defaults.json")
        return json.loads(defaults_path.read_text())

    def update_instance_config(self):
        settings = self.get_defaults()
        settings.update(self.config)
        super().__init__(settings)

    def __setattr__(self, name: str, value) -> None:
        value = self.transforms[name](value)

        self.config[name] = value
        self.update_instance_config()
        save_settings()

    def __setitem__(self, k, v) -> None:
        self.__setattr__(k, v)

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
        template = "https://campusvirtual.uva.es/course/view.php?id=%d"
        return [template % x for x in self.exclude_subjects_ids]

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

    @property
    def email(self) -> str:
        return self["email"]


Settings.update_config()
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
        from logging import _levelToName

        if settings.logging_level not in _levelToName.values():
            raise TypeError(
                "Setting logging-level must be one of %s" % _levelToName.values()
            )

    @classmethod
    def check_timeout(cls):
        return
        if not isinstance(settings.timeout, int):
            try:
                timeout = int(settings.timeout)
                settings.config["timeout"] = timeout
            except ValueError:
                raise TypeError("Setting timeout must be int")
        if settings.timeout < 0:
            raise ValueError("Setting timeout must be positive")

    @classmethod
    def check_general_retries(cls):
        if not isinstance(settings.retries, int):
            raise TypeError("Setting retries must be int")
        if settings.retries < 0:
            raise ValueError("Setting retries must be positive")

    @classmethod
    def check_login_retries(cls):
        if not isinstance(settings.login_retries, int):
            raise TypeError("Setting login-retries must be int")
        if settings.login_retries < 0:
            raise ValueError("Setting login-retries must be positive")

    @classmethod
    def check_logout_retries(cls):
        if not isinstance(settings.logout_retries, int):
            raise TypeError("Setting logout-retries must be int")
        if settings.logout_retries < 0:
            raise ValueError("Setting logout-retries must be positive")

    @classmethod
    def check_max_logs(cls):
        if not isinstance(settings.max_logs, int):
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
            raise TypeError("Setting http-status-port must be int")
        if settings.http_status_port < 0:
            raise ValueError("Setting http-status-port must be positive")

    @classmethod
    def check_http_status_tickrate(cls):
        if not isinstance(settings.http_status_tickrate, int):
            raise TypeError("Setting http-status-tickrate must be int")
        if settings.http_status_tickrate < 0:
            raise ValueError("Setting http-status-tickrate must be positive")

    @classmethod
    def check_forum_subfolders(cls):
        if not isinstance(settings.forum_subfolders, bool):
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

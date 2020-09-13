"""Settings manager."""

import json
from logging import _levelToName
import os
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Dict, List

from ruamel.yaml import YAML

from .core.exceptions import (
    AlreadyExcludedError,
    AlreadyIndexedError,
    NotExcludedError,
    NotIndexedError,
    SettingsError,
)
from .core.utils import MetaSingleton, Patterns, handle_fatal_error_exit, str2bool


def save_settings():
    """Check settings and saves them."""

    CheckSettings.check()
    settings.update_config()

    yaml = YAML()
    with settings.settings_path.open("wt") as file:
        yaml.dump(settings.config, file)


def settings_to_string() -> str:
    """Returns the settings keys and values as a string.

    Returns:
        str: settings as a string.
    """

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
    """Marks a subject's id to be indexed.

    Args:
        subject_id (int): subject id mark to index.

    Raises:
        AlreadyIndexedError: if the subject id is already marked to be indexed.
    """

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
    """Marks a subject's id to not be indexed.

    Args:
        subject_id (int): subject id mark to unindex.

    Raises:
        NotIndexedError: if the subject id is not marked to be indexed.
    """

    if subject_id not in settings.section_indexing_ids:
        raise NotIndexedError("Subject ID '%d' is not section-indexed" % subject_id)

    index = list(settings.section_indexing_ids)
    index.remove(subject_id)
    index = list(set(index))
    index.sort()
    settings["section-indexing-ids"] = index


def exclude(subject_id: int):
    """Marks a subject's id to be excluded from parsing.

    Args:
        subject_id (int): subject's id to be excluded.

    Raises:
        AlreadyExcludedError: if the subject's id is already marked to be excluded.
    """

    if subject_id in settings.exclude_subjects_ids:
        raise AlreadyExcludedError("Subject ID '%d' is already excluded" % subject_id)

    all_excluded = list(settings.exclude_subjects_ids)
    all_excluded.append(subject_id)
    all_excluded = list(set(all_excluded))
    all_excluded.sort()
    settings["exclude-subjects-ids"] = all_excluded


def include(subject_id: int):
    """Marks a subject's id to be included in parsing.

    Args:
        subject_id (int): subject's id to be included in parsing.

    Raises:
        NotExcludedError: if the subject's id is not marked to be excluded.
    """

    if subject_id not in settings.exclude_subjects_ids:
        raise NotExcludedError("Subject ID '%d' is not excluded" % subject_id)

    all_excluded = list(settings.exclude_subjects_ids)
    all_excluded.remove(subject_id)
    all_excluded = list(set(all_excluded))
    all_excluded.sort()
    settings["exclude-subjects-ids"] = all_excluded


class Settings(dict, metaclass=MetaSingleton):
    # pylint: disable=too-many-public-methods
    """Settings manager."""

    if os.getenv("TESTING"):  # pragma: no cover
        settings_folder = Path(gettempdir())  # pragma: no cover
        _preffix = "test-"  # pragma: no cover
    else:  # pragma: no cover
        settings_folder = Path.home()  # pragma: no cover
        _preffix = ""  # pragma: no cover

    credentials_path = settings_folder.joinpath(_preffix + "vcm-credentials.yaml")
    settings_path = settings_folder.joinpath(_preffix + "vcm-settings.yaml")
    config = {}

    _template = "https://campusvirtual.uva.es/course/view.php?id=%d"

    @classmethod
    def gen_subject_url(cls, subject_id: int) -> str:
        """Generates the subject's real url given its id.

        Args:
            subject_id (int): subject's id.

        Returns:
            str: subject's real url.
        """

        return cls._template % subject_id

    def exclude_subjects_ids_setter(self):  # pylint: disable=no-self-use
        """Setter for setting exclude-subjects-ids."""

        raise SettingsError("exclude-subjects-ids can't be set using the CLI.")

    def section_indexing_setter(self):  # pylint: disable=no-self-use
        """Setter for setting section-indexing."""

        raise SettingsError("section-indexing can't be set using the CLI")

    def logging_level_setter(*args) -> str:
        """Setter for logging-level.

        Args:
            value (str): logging level.

        Raises:
            ValueError: if `value` is not a valid logging-level.

        Returns:
            str: parsed logging level.
        """

        # FIXME: not pythonic

        value = str(args[0]).upper()
        if value in _levelToName.values():
            return value

        raise ValueError(f"Invalid logging-level: {value!r}")

    transforms = {
        "email": str,
        "exclude-subjects-ids": exclude_subjects_ids_setter,
        "forum-subfolders": str2bool,
        "http-status-port": int,
        "http-status-tickrate": int,
        "logging-level": logging_level_setter,
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
        super().__init__()
        self.update_config()

    def __setitem__(self, k, v) -> None:
        k = k.replace("_", "-").lower()
        v = self.transforms[k](v)
        self.config[k] = v
        save_settings()

    def __getitem__(self, k):
        k = k.replace("_", "-").lower()
        return self.config[k]

    def __contains__(self, k: str) -> bool:
        k = k.replace("_", "-").lower()
        return k in self.config

    @classmethod
    def get_current_config(cls) -> Dict[str, Any]:
        """Returns the user settings values.

        Returns:
            Dict[str, Any]: user settings values.
        """

        if not cls.settings_path.is_file():
            cls.create_example()
            return handle_fatal_error_exit("Settings file does not exist")

        yaml = YAML(typ="safe")
        return yaml.load(cls.settings_path.read_text())

    @classmethod
    def create_example(cls):
        """Writes the defaults settings values to the user settings file."""

        yaml = YAML()
        data = cls.get_defaults()
        with cls.settings_path.open("wt", encoding="utf-8") as file_handler:
            yaml.dump(data, file_handler)

    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """Returns the settings defaults.

        Returns:
            Dict[str, Any]: settings defaults.
        """

        defaults_path = Path(__file__).with_name("data") / "defaults.json"
        return json.loads(defaults_path.read_text())

    def update_config(self):
        """Updates config."""

        if not self.config:
            self.__class__.config = self.get_defaults()
            self.__class__.config.update(self.get_current_config())
        super().__init__(self.config)

    @property
    def root_folder(self) -> Path:
        """Root folder where files are downloaded.

        Returns:
            Path: root folder.
        """

        return Path(self["root-folder"])

    @property
    def logging_level(self) -> str:
        """Logging level.

        Returns:
            str: logging level.
        """

        return self["logging-level"]

    @property
    def timeout(self) -> int:
        """Timeout for all HTTP connections.

        Returns:
            int: timeout
        """

        return self["timeout"]

    @property
    def retries(self) -> int:
        """Number of HTTP requests made before giving up.

        Returns:
            int: number of retries.
        """
        return self["retries"]

    @property
    def login_retries(self) -> int:
        """Number of times to try to login before giving up.

        Returns:
            int: login retries.
        """

        return self["login-retries"]

    @property
    def logout_retries(self) -> int:
        """Number of times to try to logout before giving up.

        Returns:
            int: logout retries.
        """

        return self["logout-retries"]

    @property
    def max_logs(self) -> int:
        """Number of logs stored.

        Returns:
            int: number of logs stored.
        """

        return self["max-logs"]

    @property
    def exclude_subjects_ids(self) -> List[int]:
        """List of ids of subjects excluded.

        Returns:
            List[int]: list of subjects excluded.
        """

        return self["exclude-subjects-ids"]

    @property
    def http_status_port(self) -> int:
        """TCP port to start the HTTP status server.

        Returns:
            int: TCP port.
        """

        return self["http-status-port"]

    @property
    def http_status_tickrate(self) -> float:
        """Number of times per second to update the thread status interface.

        Returns:
            float: number of fps.
        """

        return self["http-status-tickrate"]

    # DEPENDANT SETTINGS

    @property
    def logs_folder(self) -> Path:
        """Folder where logs are stored.

        Returns:
            Path: logs folder.
        """

        return self.root_folder / ".logs"

    @property
    def log_path(self) -> Path:
        """Current log file path.

        Returns:
            Path: current log file path.
        """

        return self.logs_folder / "vcm.log"

    @property
    def database_path(self) -> Path:
        """Path of the links database.

        Returns:
            Path: path of the links database.
        """

        return self.root_folder / "links.db"

    @property
    def exclude_urls(self) -> List[str]:
        """List of subjects urls excluded.

        Returns:
            List[str]: list of subjects urls excluded.
        """

        return [self.gen_subject_url(x) for x in self.exclude_subjects_ids]

    @property
    def forum_subfolders(self) -> bool:
        """Returns wether the forum entries should be downloaded in a subfolder or not.

        Returns:
            bool: forum-subfolders.
        """

        return self["forum-subfolders"]

    @property
    def section_indexing_ids(self) -> List[int]:
        """List of subjects ids with section-indexing enabled.

        Returns:
            List[int]: list of subjects ids.
        """

        return self["section-indexing-ids"]

    @property
    def section_indexing_urls(self) -> List[str]:
        """List of subjects urls with section-indexing enabled.

        Returns:
            List[str]: list of subjects urls.
        """

        return [self.gen_subject_url(x) for x in self.section_indexing_ids]

    @property
    def secure_section_filename(self) -> bool:
        """Returns wether the section filename should be secured or not.

        Returns:
            bool: secure-section-filename.
        """

        return self["secure-section-filename"]

    @property
    def email(self) -> str:
        """Email to send the report to.

        Returns:
            str: email.
        """

        return self["email"]


settings = Settings()


class CheckSettings:
    """Checkers for settings."""

    @classmethod
    def check(cls):
        """Executes all checks declared in this class."""
        for attribute in dir(cls):
            if not attribute.startswith("check_"):
                continue
            check = getattr(cls, attribute)
            check()

    @classmethod
    def check_root_folder(cls):
        """Root folder checks.

        Raises:
            TypeError: if settings.root_folder does not return Path.
            TypeError: if settings["root-folder"] does not return str.
            ValueError: if 'root-folder' setting is not set.
        """

        if not isinstance(settings["root-folder"], str):
            raise TypeError("Setting root-folder must be str")
        if not isinstance(settings.root_folder, Path):
            raise TypeError("Wrapper of setting root-folder must return Path")
        if settings["root-folder"] == "insert-root-folder":
            raise ValueError("Must set root-folder setting")
        settings.root_folder.mkdir(parents=True, exist_ok=True)

    @classmethod
    def check_logs_folder(cls):
        """Logs folder checks.

        Raises:
            TypeError: if settings.logs_folder does not return Path.
        """

        if not isinstance(settings.logs_folder, Path):
            raise TypeError("Wrapper of logs folder must return Path")
        settings.logs_folder.mkdir(parents=True, exist_ok=True)

    @classmethod
    def check_logging_level(cls):
        """Logging level checks.

        Raises:
            TypeError: if settings.logging_level does not return str.
            ValueError: if settings.logging_level is not a valid logging level.
        """

        if not isinstance(settings.logging_level, str):
            raise TypeError("Setting logging-level must be str")

        if settings.logging_level not in _levelToName.values():
            logging_level = settings.logging_level.upper()
            if logging_level not in _levelToName.values():
                raise ValueError(
                    "Setting logging-level must be one of %s" % _levelToName.values()
                )
            settings["logging-level"] = logging_level

    @classmethod
    def check_timeout(cls):
        """Timeout checks.

        Raises:
            TypeError: if settings.timeout is not a valid number.
            ValueError: if settings.timeout is negative.
        """

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
        """Retries checks.

        Raises:
            TypeError: if settings.retries is not a valid number.
            ValueError: if settings.retries is negative.
        """

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
        """Login retries checks.

        Raises:
            TypeError: if settings.login_retries is not a valid number.
            ValueError: if settings.login_retries is negative.
        """

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
        """Logout retries checks.

        Raises:
            TypeError: if settings.logout_retries is not a valid number.
            ValueError: if settings.logout_retries is negative.
        """

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
        """Max logs checks.

        Raises:
            TypeError: if settings.max_logs is not a valid number.
            ValueError: if settings.max_logs is negative.
        """

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
        """Exclude subjects ids checks.

        Raises:
            TypeError: if settings.exclude_subjects_ids does not return a list.
            TypeError: if any member of settings.exclude_subjects_ids is not a number.
            ValueError: if any member of settings.exclude_subjects_ids is negative.
        """

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
        """Http status port checks.

        Raises:
            TypeError: if settings.http_status_port is not a valid number.
            ValueError: if settings.http_status_port is negative.
        """

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
        """Http status tickrate checks.

        Raises:
            TypeError: if settings.http_status_tickrate is not a valid number.
            ValueError: if settings.http_status_tickrate is negative.
        """

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
        """Forum subfolders check.

        Raises:
            TypeError: if settings.forum_subfolders is not a boolean.
        """

        if not isinstance(settings.forum_subfolders, bool):
            try:
                forum_subfolders = str2bool(settings.forum_subfolders)
                settings["forum_subfolders"] = forum_subfolders
            except ValueError:
                raise TypeError("Setting forum-subfolders must be a boolean")

    @classmethod
    def check_section_indexing_ids(cls):
        """section indexing ids checks.

        Raises:
            TypeError: if settings.section_indexing does not return a list.
            TypeError: if any member of settings.section_indexing is not a number.
            ValueError: if any member of settings.section_indexing is negative.
        """

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
        """Secure section filename check.

        Raises:
            TypeError: if settings.secure_section_filename is not a boolean.
        """

        if not isinstance(settings.secure_section_filename, bool):
            try:
                secure_section_filename = str2bool(settings.secure_section_filename)
                settings["secure_section_filename"] = secure_section_filename
            except ValueError:
                raise TypeError("Setting secure-section-filename must be bool")

    @classmethod
    def check_email(cls):
        """Email checks.

        Raises:
            ValueError: if settings.email is not set.
            TypeError: if settings.email does not return str.
            ValueError: if settings.email is not a valid email.
        """

        if settings.email == "insert-email":
            raise ValueError("Must set email setting")
        if not isinstance(settings.email, str):
            raise TypeError("Setting email must be str")
        if not Patterns.EMAIL.search(settings.email):
            raise ValueError("Setting email is not a valid email")


CheckSettings.check()

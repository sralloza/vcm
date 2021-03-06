from pathlib import Path
from shutil import rmtree
from typing import Optional
from unittest import mock

import pytest

from vcm.core.exceptions import (
    AlreadyExcludedError,
    AlreadyIndexedError,
    NotExcludedError,
    NotIndexedError,
    SettingsError,
)
from vcm.settings import (
    CheckSettings,
    Settings,
    exclude,
    include,
    save_settings,
    section_index,
    settings_to_string,
    un_section_index,
)

# pylint: disable=protected-access
Settings._instance: Optional[Settings]  # for pylint


class TestSaveSettings:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.check_m = mock.patch("vcm.settings.CheckSettings.check").start()
        self.settings_m = mock.patch("vcm.settings.settings").start()
        self.yaml_m = mock.patch("vcm.settings.YAML").start()

        yield

        mock.patch.stopall()

    def test_save_settings(self):
        save_settings()

        self.check_m.assert_called_once_with()
        self.yaml_m.assert_called_once_with()
        self.settings_m.settings_path.open.assert_called_once_with("wt")
        enter_m = self.settings_m.settings_path.open.return_value.__enter__
        enter_m.assert_called_once()
        self.yaml_m.return_value.dump.assert_called_once_with(
            self.settings_m.config, enter_m.return_value
        )


class TestSettingsToString:
    @pytest.fixture(autouse=True)
    def mocks(self):
        class TestingSettings(dict):
            credentials_path = "<creds-path>"
            settings_path = "<settings-path>"

        self.settings = TestingSettings()
        self.settings["key_a"] = "a"
        self.settings["key-b"] = "b"

        mock.patch("vcm.settings.settings", self.settings).start()
        yield
        mock.patch.stopall()

    def test_settings_to_string(self):
        output = settings_to_string()
        expected = "- settings:\n    credentials-path: <creds-path>\n"
        expected += "    settings-path: <settings-path>\n"
        expected += "    key-a: 'a'\n    key-b: 'b'\n"
        assert output == expected


class TestSectionIndex:
    @pytest.fixture(autouse=True)
    def mocks(self):
        Settings._instance = None
        Settings.config = {}

        self.save_m = mock.patch("vcm.settings.save_settings").start()
        self.transforms_m = mock.patch("vcm.settings.Settings.transforms").start()
        self.transforms_m.__getitem__.return_value.side_effect = lambda x: x

        self.settings = Settings()
        assert self.settings["section-indexing-ids"] == []

        mock.patch("vcm.settings.settings", self.settings).start()

        yield

        Settings._instance = None
        Settings.config = None
        mock.patch.stopall()

    def test_ok_1(self):
        section_index(654)
        section_index(655)
        section_index(653)

        assert self.settings["section-indexing-ids"] == [653, 654, 655]
        assert self.save_m.call_count == 3

    def test_ok_2(self):
        section_index(654)
        section_index(655)
        self.settings["section-indexing-ids"] = [655, 655, 655, 654, 654, 654, 654]
        section_index(653)

        assert self.settings["section-indexing-ids"] == [653, 654, 655]
        assert self.save_m.call_count == 4

    def test_fail(self):
        section_index(654)

        with pytest.raises(AlreadyIndexedError, match="654"):
            section_index(654)

        assert self.settings["section-indexing-ids"] == [654]
        assert self.save_m.call_count == 1


class TestUnSectionIndex:
    @pytest.fixture(autouse=True)
    def mocks(self):
        Settings._instance = None
        Settings.config = {}

        self.save_m = mock.patch("vcm.settings.save_settings").start()
        transforms_m = mock.patch("vcm.settings.Settings.transforms").start()
        transforms_m.__getitem__.return_value.side_effect = lambda x: x

        self.settings = Settings()
        assert self.settings["section-indexing-ids"] == []
        self.settings["section-indexing-ids"] = [753, 754, 755]
        mock.patch("vcm.settings.settings", self.settings).start()

        yield

        Settings.config = None
        Settings._instance = None

        mock.patch.stopall()

    def test_ok_1(self):
        assert self.settings["section-indexing-ids"] == [753, 754, 755]
        un_section_index(753)
        assert self.settings["section-indexing-ids"] == [754, 755]

        un_section_index(754)
        assert self.settings["section-indexing-ids"] == [755]

        un_section_index(755)
        assert self.settings["section-indexing-ids"] == []

        assert self.save_m.call_count == 4

    def test_ok_2(self):
        assert self.settings["section-indexing-ids"] == [753, 754, 755]

        un_section_index(754)
        un_section_index(755)

        assert self.settings["section-indexing-ids"] == [753]
        self.settings["section-indexing-ids"] = [755, 755, 755, 754, 754, 754, 754, 753]
        un_section_index(753)

        assert self.settings["section-indexing-ids"] == [754, 755]
        assert self.save_m.call_count == 5

    def test_fail(self):
        self.settings["section-indexing-ids"] = [754, 755]
        un_section_index(754)

        with pytest.raises(NotIndexedError, match="754"):
            un_section_index(754)

        assert self.settings["section-indexing-ids"] == [755]
        assert self.save_m.call_count == 3


class TestExclude:
    @pytest.fixture(autouse=True)
    def mocks(self):
        Settings._instance = None
        Settings.config = {}

        self.save_m = mock.patch("vcm.settings.save_settings").start()
        transforms_m = mock.patch("vcm.settings.Settings.transforms").start()
        transforms_m.__getitem__.return_value.side_effect = lambda x: x

        self.settings = Settings()
        assert self.settings["exclude-subjects-ids"] == []

        mock.patch("vcm.settings.settings", self.settings).start()

        yield

        Settings._instance = None
        Settings.config = None

        mock.patch.stopall()

    def test_ok_1(self):
        exclude(654)
        exclude(655)
        exclude(653)

        assert self.settings["exclude-subjects-ids"] == [653, 654, 655]
        assert self.save_m.call_count == 3

    def test_ok_2(self):
        exclude(654)
        exclude(655)
        self.settings["exclude-subjects-ids"] = [655, 655, 655, 654, 654, 654, 654]
        exclude(653)

        assert self.settings["exclude-subjects-ids"] == [653, 654, 655]
        assert self.save_m.call_count == 4

    def test_fail(self):
        exclude(654)

        with pytest.raises(AlreadyExcludedError, match="654"):
            exclude(654)

        assert self.settings["exclude-subjects-ids"] == [654]
        assert self.save_m.call_count == 1


class TestInclude:
    @pytest.fixture(autouse=True)
    def mocks(self):
        Settings._instance = None
        Settings.config = {}

        self.save_m = mock.patch("vcm.settings.save_settings").start()
        transforms_m = mock.patch("vcm.settings.Settings.transforms").start()
        transforms_m.__getitem__.return_value.side_effect = lambda x: x

        self.settings = Settings()
        assert self.settings["exclude-subjects-ids"] == []
        self.settings["exclude-subjects-ids"] = [753, 754, 755]
        mock.patch("vcm.settings.settings", self.settings).start()

        yield

        Settings._instance = None
        Settings.config = None

        mock.patch.stopall()

    def test_ok_1(self):
        assert self.settings["exclude-subjects-ids"] == [753, 754, 755]
        include(753)
        assert self.settings["exclude-subjects-ids"] == [754, 755]

        include(754)
        assert self.settings["exclude-subjects-ids"] == [755]

        include(755)
        assert self.settings["exclude-subjects-ids"] == []

        assert self.save_m.call_count == 4

    def test_ok_2(self):
        assert self.settings["exclude-subjects-ids"] == [753, 754, 755]

        include(754)
        include(755)

        assert self.settings["exclude-subjects-ids"] == [753]
        self.settings["exclude-subjects-ids"] = [755, 755, 755, 754, 754, 754, 754, 753]
        include(753)

        assert self.settings["exclude-subjects-ids"] == [754, 755]
        assert self.save_m.call_count == 5

    def test_fail(self):
        self.settings["exclude-subjects-ids"] = [754, 755]
        include(754)

        with pytest.raises(NotExcludedError, match="754"):
            include(754)

        assert self.settings["exclude-subjects-ids"] == [755]
        assert self.save_m.call_count == 3


class TestSettings:
    @pytest.fixture(autouse=True)
    def mocks(self):
        Settings._instance = None
        Settings.config = {}
        self.save_m = mock.patch("vcm.settings.save_settings").start()
        self.transf_patcher = mock.patch("vcm.settings.Settings.transforms")
        self.transforms_m = self.transf_patcher.start()
        self.transforms_m.__getitem__.return_value.side_effect = lambda x: x  # noqa
        yield
        self.save_m.assert_not_called()
        mock.patch.stopall()

    def test_use_metaclass(self):
        settings1 = Settings()
        settings2 = Settings()
        settings3 = Settings()
        assert settings1 is settings2
        assert settings2 is settings3
        assert settings3 is settings1
        assert settings1 is Settings._instance
        assert settings2 is Settings._instance
        assert settings3 is Settings._instance

    def test_class_attributes(self):
        assert hasattr(Settings, "settings_folder")
        assert hasattr(Settings, "_preffix")
        assert hasattr(Settings, "credentials_path")
        assert hasattr(Settings, "settings_path")
        assert hasattr(Settings, "config")

    def test_exclude_subjects_ids_setter(self):
        settings = Settings()
        with pytest.raises(SettingsError, match="can't be set using the CLI"):
            settings.exclude_subjects_ids_setter()

    def test_section_indexing_setter(self):
        settings = Settings()
        with pytest.raises(SettingsError, match="can't be set using the CLI"):
            settings.section_indexing_setter()

    def test_logging_level_setter(self):
        test = Settings.logging_level_setter
        assert test("debug") == "DEBUG"
        assert test("iNfO") == "INFO"
        assert test("WARNINg") == "WARNING"
        assert test("critical") == "CRITICAL"

        with pytest.raises(ValueError):
            test("invalid")

    def test_transforms(self):
        self.transf_patcher.stop()
        assert len(Settings.transforms) == 14
        for transform in Settings.transforms.values():
            assert callable(transform)

    @mock.patch("vcm.settings.Settings.update_config")
    def test_init(self, upd_conf_m):
        Settings()
        upd_conf_m.assert_called_once_with()

    def test_getitem(self):
        settings = Settings()
        settings.config = {"hello-world": "yes"}
        assert settings["hello-world"] == "yes"
        assert settings["hello_world"] == "yes"
        assert settings["HELLO_WORLD"] == "yes"
        assert settings["hElLo_WoRlD"] == "yes"

        with pytest.raises(KeyError):
            assert settings["hello world"]

    def test_contains(self):
        settings = Settings()
        settings.config = {"hello-world": "yes"}
        assert "hello-world" in settings
        assert "hello_world" in settings
        assert "HELLO_WORLD" in settings
        assert "hElLo_WoRlD" in settings

    @mock.patch("vcm.settings.Settings.transform")
    def test_setitem(self, transform_m):
        transform_m.side_effect = lambda key, value: value

        settings = Settings()
        settings["hello-world"] = "yes"
        assert settings["hello-world"] == "yes"

        settings["hello_world"] = "yes"
        assert settings["hello-world"] == "yes"

        settings["HELLO_WORLD"] = "yes"
        assert settings["hello-world"] == "yes"

        settings["hElLo_WoRlD"] = "yes"
        assert settings["hello-world"] == "yes"

        self.save_m.assert_called()
        assert self.save_m.call_count == 4
        self.save_m.reset_mock()

        transform_m.assert_any_call("hello-world", "yes")
        assert transform_m.call_count == 4

    def test_transform(self):
        self.transf_patcher.stop()
        new_transforms = {"key-a": int, "key-b": float}
        mock.patch("vcm.settings.Settings.transforms", new_transforms).start()

        settings = Settings()
        settings["key-a"] = 1
        settings["key-b"] = 0.5
        self.save_m.reset_mock()

        assert settings.transform("key-a", "25") == 25
        assert settings.transform("key-b", "24.5") == 24.5

        with pytest.raises(SettingsError, match="Invalid value for 'key-a'"):
            settings.transform("key-a", "not-an-int")

        with pytest.raises(SettingsError, match="Invalid value for 'key-b'"):
            settings.transform("key-b", "not-a-float")

    @mock.patch("vcm.settings.Settings.create_example")
    @mock.patch("pathlib.Path.is_file")
    def test_get_current_config_ok(self, is_file_m, example_m, capsys):
        is_file_m.return_value = True

        config = Settings.get_current_config()

        assert isinstance(config, dict)
        for key, value in config.items():
            assert isinstance(key, str)
            assert "_" not in key
            assert key.islower()
            assert value.__class__

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

        example_m.assert_not_called()

    @mock.patch("vcm.settings.Settings.create_example")
    @mock.patch("pathlib.Path.is_file")
    def test_get_current_config_fail(self, is_file_m, example_m, capsys):
        is_file_m.return_value = False

        with pytest.raises(SystemExit, match="-1"):
            config = Settings.get_current_config()

        with pytest.raises(NameError):
            assert config

        captured = capsys.readouterr()
        assert captured.err == "Settings file does not exist\n"
        assert captured.out == ""

        example_m.assert_called_once_with()

    @mock.patch("vcm.settings.YAML")
    @mock.patch("vcm.settings.Settings.get_defaults")
    @mock.patch("pathlib.Path.open")
    def test_create_example(self, open_m, gd_m, yaml_m):
        gd_m.return_value = {"defaults": True}

        Settings.create_example()

        yaml_m.assert_called_once_with()
        gd_m.assert_called_once_with()
        open_m.assert_called_once_with("wt", encoding="utf-8")
        open_m.return_value.__enter__.assert_called_once_with()
        file_handler = open_m.return_value.__enter__.return_value
        yaml_m.return_value.dump({"defaults": True}, file_handler)
        open_m.return_value.__exit__.assert_called_once_with(None, None, None)

    @mock.patch("vcm.settings.Settings.get_defaults")
    @mock.patch("vcm.settings.Settings.get_current_config")
    @pytest.mark.parametrize("empty_config", [True, False])
    def test_update_config(self, gcc_m, gd_m, empty_config):
        if empty_config:
            Settings.config = {}
        else:
            Settings.config = {"set-up": True}

        gd_m.return_value = {"key-a": "a0", "key-c": "c0"}
        gcc_m.return_value = {"key-a": "a1", "key-b": "b1"}

        settings = Settings()
        settings.update_config()

        if empty_config:
            assert settings["key-a"] == "a1"
            assert settings["key-b"] == "b1"
            assert settings["key-c"] == "c0"
        else:
            assert settings["set-up"] is True

    def test_get_defaults(self):
        defaults = Settings.get_defaults()
        assert isinstance(defaults, dict)

        for key, value in defaults.items():
            assert isinstance(key, str)
            assert value.__class__


class TestSettingsAttributes:
    @pytest.fixture(autouse=True)
    def mocks(self):
        Settings._instance = None
        self.save_m = mock.patch("vcm.settings.save_settings").start()
        self.transf_patcher = mock.patch("vcm.settings.Settings.transforms")
        self.transforms_m = self.transf_patcher.start()
        self.transforms_m.__getitem__.return_value.side_effect = lambda x: x
        self.settings = Settings()
        yield
        mock.patch.stopall()

    def test_root_folder(self):
        assert isinstance(self.settings.root_folder, Path)
        assert self.settings.root_folder.as_posix() == self.settings["root-folder"]

    def test_base_url(self):
        assert isinstance(self.settings.base_url, str)
        assert self.settings.base_url == self.settings["base-url"]

    def test_logging_level(self):
        assert isinstance(self.settings.logging_level, str)
        assert self.settings.logging_level == self.settings["logging-level"]

    def test_timeout(self):
        assert isinstance(self.settings.timeout, int)
        assert self.settings.timeout == self.settings["timeout"]

    def test_retries(self):
        assert isinstance(self.settings.retries, int)
        assert self.settings.retries == self.settings["retries"]

    def test_login_retries(self):
        assert isinstance(self.settings.login_retries, int)
        assert self.settings.login_retries == self.settings["login-retries"]

    def test_logout_retries(self):
        assert isinstance(self.settings.logout_retries, int)
        assert self.settings.logout_retries == self.settings["logout-retries"]

    def test_max_logs(self):
        assert isinstance(self.settings.max_logs, int)
        assert self.settings.max_logs == self.settings["max-logs"]

    def test_exclude_subjects_ids(self):
        # Ensure exclude-subjects-ids
        ids = [654, 655, 656]
        self.settings["exclude-subjects-ids"] = ids
        assert self.settings.exclude_subjects_ids == ids

    def test_http_status_port(self):
        assert isinstance(self.settings.http_status_port, int)
        assert self.settings.http_status_port == self.settings["http-status-port"]

    def test_http_status_tickrate(self):
        assert isinstance(self.settings.http_status_tickrate, int)
        assert (
            self.settings.http_status_tickrate == self.settings["http-status-tickrate"]
        )

    def test_logs_folder(self):
        assert isinstance(self.settings.logs_folder, Path)
        assert self.settings.logs_folder.as_posix().endswith("logs")
        rel = self.settings.logs_folder.relative_to(self.settings.root_folder)
        assert rel == Path(".logs")

    def test_log_path(self):
        assert isinstance(self.settings.log_path, Path)
        assert self.settings.log_path.as_posix().endswith("log")
        rel = self.settings.log_path.relative_to(self.settings.logs_folder)
        assert rel == Path("vcm.log")

    def test_database_path(self):
        assert isinstance(self.settings.database_path, Path)
        assert self.settings.database_path.relative_to(self.settings.root_folder)
        assert self.settings.database_path.as_posix().endswith("db")

    def test_exclude_urls(self):
        # Ensure exclude-subjects-ids
        ids = [654, 655, 656]
        self.settings["exclude-subjects-ids"] = ids
        assert isinstance(self.settings.exclude_urls, list)
        for url, subject_id in zip(self.settings.exclude_urls, ids):
            assert isinstance(url, str)
            assert str(subject_id) in url
            assert "campusvirtual.uva.es" in url
            assert "https://" in url
            assert "course" in url
            assert "view.php" in url

    def test_forum_subfolders(self):
        assert isinstance(self.settings.forum_subfolders, bool)
        assert self.settings.forum_subfolders == self.settings["forum-subfolders"]

    def test_section_indexing_ids(self):
        # Ensure section-indexing-ids
        ids = [654, 655, 656]
        self.settings["section-indexing-ids"] = ids
        assert self.settings.section_indexing_ids == ids

    def test_section_indexing_urls(self):
        # Ensure section-indexing-ids
        ids = [654, 655, 656]
        self.settings["section-indexing-ids"] = ids
        assert isinstance(self.settings.section_indexing_urls, list)
        for url, subject_id in zip(self.settings.section_indexing_urls, ids):
            assert isinstance(url, str)
            assert str(subject_id) in url
            assert "campusvirtual.uva.es" in url
            assert "https://" in url
            assert "course" in url
            assert "view.php" in url

    def test_secure_section_filename(self):
        assert isinstance(self.settings.secure_section_filename, bool)
        assert (
            self.settings.secure_section_filename
            == self.settings["secure-section-filename"]
        )

    def test_email(self):
        assert isinstance(self.settings.email, str)
        assert self.settings.email == self.settings["email"]


class TestCheckSettings:
    @pytest.fixture(autouse=True)
    def mocks(self):
        Settings._instance = None
        Settings.config = {}
        self.save_m = mock.patch("vcm.settings.save_settings").start()
        self.transf_patcher = mock.patch("vcm.settings.Settings.transforms")
        self.transforms_m = self.transf_patcher.start()
        self.transforms_m.__getitem__.return_value.side_effect = lambda x: x
        self.settings = Settings()
        yield
        mock.patch.stopall()

    def test_check(self):
        checks = [
            "base_url",
            "root_folder",
            "logs_folder",
            "logging_level",
            "timeout",
            "retries",
            "login_retries",
            "logout_retries",
            "max_logs",
            "exclude_subjects_ids",
            "http_status_port",
            "http_status_tickrate",
            "forum_subfolders",
            "section_indexing_ids",
            "secure_section_filename",
            "email",
        ]

        mocked_checks = []
        for check in checks:
            route = "vcm.settings.CheckSettings.check_" + check
            mocked_check = mock.patch(route).start()
            mocked_checks.append(mocked_check)

        CheckSettings.check()

        for mocked_check in mocked_checks:
            mocked_check.assert_called_once_with()
            mocked_check.reset_mock()

    @mock.patch("pathlib.Path.mkdir")
    def test_check_root_folder(self, mkdir_m):
        rmtree(self.settings.root_folder, ignore_errors=True)

        self.settings["root-folder"] = "/path/to/folder"
        CheckSettings.check_root_folder()
        mkdir_m.assert_called_once_with(parents=True, exist_ok=True)

        self.settings["root-folder"] = 65
        with pytest.raises(TypeError):
            CheckSettings.check_root_folder()

        self.settings["root-folder"] = "insert-root-folder"
        with pytest.raises(ValueError):
            CheckSettings.check_root_folder()

        mocked_root_folder = "vcm.settings.Settings.root_folder"
        with mock.patch(mocked_root_folder, new_callable=mock.PropertyMock) as rf_m:
            rf_m.return_value = "invalid"
            with pytest.raises(TypeError, match="Wrapper"):
                CheckSettings.check_root_folder()
            rf_m.assert_called_once_with()
        mkdir_m.assert_called_once_with(parents=True, exist_ok=True)

    def test_check_base_url(self):
        self.settings["base-url"] = "https://example.com"
        CheckSettings.check_base_url()

        self.settings["base-url"] = 65
        with pytest.raises(TypeError):
            CheckSettings.check_base_url()

    @mock.patch("pathlib.Path.mkdir")
    def test_check_logs_folder(self, mkdir_m):
        rmtree(self.settings.logs_folder, ignore_errors=True)
        CheckSettings.check_logs_folder()
        mkdir_m.assert_called_once_with(parents=True, exist_ok=True)

        mocked_logs_folder = "vcm.settings.Settings.logs_folder"
        with mock.patch(mocked_logs_folder, new_callable=mock.PropertyMock) as lf_m:
            lf_m.return_value = "invalid"
            with pytest.raises(TypeError, match="Wrapper"):
                CheckSettings.check_logs_folder()
            lf_m.assert_called_once_with()

        assert mkdir_m.call_count == 1

    def test_check_logging_level(self):
        self.settings["logging-level"] = "DEBUG"
        CheckSettings.check_logging_level()

        self.settings["logging-level"] = "critical"
        CheckSettings.check_logging_level()
        assert self.settings.logging_level == "CRITICAL"

        self.settings["logging-level"] = 54
        with pytest.raises(TypeError):
            CheckSettings.check_logging_level()

        self.settings["logging-level"] = "invalid"
        with pytest.raises(ValueError):
            CheckSettings.check_logging_level()

    def test_check_timeout(self):
        self.settings["timeout"] = 20
        CheckSettings.check_timeout()

        self.settings["timeout"] = "30"
        CheckSettings.check_timeout()
        assert self.settings["timeout"] == 30

        self.settings["timeout"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_timeout()

        self.settings["timeout"] = -5
        with pytest.raises(ValueError):
            CheckSettings.check_timeout()

    def test_check_retries(self):
        self.settings["retries"] = 5
        CheckSettings.check_retries()

        self.settings["retries"] = "30"
        CheckSettings.check_retries()
        assert self.settings["retries"] == 30

        self.settings["retries"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_retries()

        self.settings["retries"] = -5
        with pytest.raises(ValueError):
            CheckSettings.check_retries()

    def test_check_login_retries(self):
        self.settings["login_retries"] = 20
        CheckSettings.check_login_retries()

        self.settings["login_retries"] = "30"
        CheckSettings.check_login_retries()
        assert self.settings["login_retries"] == 30

        self.settings["login_retries"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_login_retries()

        self.settings["login_retries"] = -5
        with pytest.raises(ValueError):
            CheckSettings.check_login_retries()

    def test_check_logout_retries(self):
        self.settings["logout_retries"] = 20
        CheckSettings.check_logout_retries()

        self.settings["logout_retries"] = "30"
        CheckSettings.check_logout_retries()
        assert self.settings["logout_retries"] == 30

        self.settings["logout_retries"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_logout_retries()

        self.settings["logout_retries"] = -5
        with pytest.raises(ValueError):
            CheckSettings.check_logout_retries()

    def test_check_max_logs(self):
        self.settings["max_logs"] = 20
        CheckSettings.check_max_logs()

        self.settings["max_logs"] = "30"
        CheckSettings.check_max_logs()
        assert self.settings["max_logs"] == 30

        self.settings["max_logs"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_max_logs()

        self.settings["max_logs"] = -5
        with pytest.raises(ValueError):
            CheckSettings.check_max_logs()

    def test_check_exclude_subjects_ids(self):
        self.settings["exclude-subjects-ids"] = []
        CheckSettings.check_exclude_subjects_ids()

        self.settings["exclude-subjects-ids"] = [500]
        CheckSettings.check_exclude_subjects_ids()

        self.settings["exclude-subjects-ids"] = 5 + 2j
        with pytest.raises(TypeError):
            CheckSettings.check_exclude_subjects_ids()

        self.settings["exclude-subjects-ids"] = [500, "sdaf"]
        with pytest.raises(TypeError):
            CheckSettings.check_exclude_subjects_ids()

        self.settings["exclude-subjects-ids"] = ["500", "sdaf"]
        with pytest.raises(TypeError):
            CheckSettings.check_exclude_subjects_ids()

        self.settings["exclude-subjects-ids"] = [5, -7]
        with pytest.raises(ValueError):
            CheckSettings.check_exclude_subjects_ids()

        self.settings["exclude-subjects-ids"] = [-5, -7]
        with pytest.raises(ValueError):
            CheckSettings.check_exclude_subjects_ids()

    def test_check_http_status_port(self):
        self.settings["http_status_port"] = 20
        CheckSettings.check_http_status_port()

        self.settings["http_status_port"] = "30"
        CheckSettings.check_http_status_port()
        assert self.settings["http_status_port"] == 30

        self.settings["http_status_port"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_http_status_port()

        self.settings["http_status_port"] = -5
        with pytest.raises(ValueError):
            CheckSettings.check_http_status_port()

    def test_check_http_status_tickrate(self):
        self.settings["http_status_tickrate"] = 20
        CheckSettings.check_http_status_tickrate()

        self.settings["http_status_tickrate"] = "30"
        CheckSettings.check_http_status_tickrate()
        assert self.settings["http_status_tickrate"] == 30

        self.settings["http_status_tickrate"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_http_status_tickrate()

        self.settings["http_status_tickrate"] = -5
        with pytest.raises(ValueError):
            CheckSettings.check_http_status_tickrate()

    def test_check_forum_subfolders(self):
        self.settings["forum_subfolders"] = False
        CheckSettings.check_forum_subfolders()

        self.settings["forum_subfolders"] = "true"
        CheckSettings.check_forum_subfolders()
        assert self.settings["forum_subfolders"] is True

        self.settings["forum_subfolders"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_forum_subfolders()

    def test_check_section_indexing_ids(self):
        self.settings["section-indexing-ids"] = []
        CheckSettings.check_section_indexing_ids()

        self.settings["section-indexing-ids"] = [500]
        CheckSettings.check_section_indexing_ids()

        self.settings["section-indexing-ids"] = 5 + 2j
        with pytest.raises(TypeError):
            CheckSettings.check_section_indexing_ids()

        self.settings["section-indexing-ids"] = [500, "sdaf"]
        with pytest.raises(TypeError):
            CheckSettings.check_section_indexing_ids()

        self.settings["section-indexing-ids"] = ["500", "sdaf"]
        with pytest.raises(TypeError):
            CheckSettings.check_section_indexing_ids()

        self.settings["section-indexing-ids"] = [5, -7]
        with pytest.raises(ValueError):
            CheckSettings.check_section_indexing_ids()

        self.settings["section-indexing-ids"] = [-5, -7]
        with pytest.raises(ValueError):
            CheckSettings.check_section_indexing_ids()

    def test_check_secure_section_filename(self):
        self.settings["secure_section_filename"] = False
        CheckSettings.check_secure_section_filename()

        self.settings["secure_section_filename"] = "true"
        CheckSettings.check_secure_section_filename()
        assert self.settings["secure_section_filename"] is True

        self.settings["secure_section_filename"] = "hello"
        with pytest.raises(TypeError):
            CheckSettings.check_secure_section_filename()

    def test_check_email(self):
        self.settings["email"] = "hey@gmail.com"
        CheckSettings.check_email()

        self.settings["email"] = "insert-email"
        with pytest.raises(ValueError):
            CheckSettings.check_email()

        self.settings["email"] = 5
        with pytest.raises(TypeError):
            CheckSettings.check_email()

        self.settings["email"] = "invalid-email"
        with pytest.raises(ValueError):
            CheckSettings.check_email()

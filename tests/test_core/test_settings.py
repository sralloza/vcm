from pathlib import Path

import pytest

from vcm.core.settings import (
    _CoreSettings,
    _DownloadSettings,
    _GeneralSettings,
    _NotifySettings,
)


@pytest.mark.xfail
def test_extend_settings_class_name():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_save_settings():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_settings_to_string():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_section_index():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_un_section_index():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_exclude():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_include():
    assert 0, "Not implemented"


def test_hidden_core_settings():
    cs = _CoreSettings()

    assert hasattr(cs, "settings_path")
    assert hasattr(cs, "credentials_path")

    assert isinstance(cs.settings_path, Path)
    assert isinstance(cs.credentials_path, Path)


def test_core_settings():
    from vcm.core.settings import CoreSettings

    assert isinstance(CoreSettings, _CoreSettings)


@pytest.mark.xfail
def test_create_default():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_meta_settings():
    assert 0, "Not implemented"


@pytest.mark.xfail
class TestBaseSettings:
    def test_new(self):
        assert 0, "Not implemented"

    def test_getitem(self):
        assert 0, "Not implemented"

    def test_get_attr(self):
        assert 0, "Not implemented"

    def test_set_attr(self):
        assert 0, "Not implemented"

    def test_set_item(self):
        assert 0, "Not implemented"

    def test_check_value_type(self):
        assert 0, "Not implemented"

    def test_parse_key(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
class TestHiddenGeneralSettings:
    def test_root_folder(self):
        assert 0, "Not implemented"

    def test_logging_level(self):
        assert 0, "Not implemented"

    def test_timeout(self):
        assert 0, "Not implemented"

    def test_retries(self):
        assert 0, "Not implemented"

    def test_max_logs(self):
        assert 0, "Not implemented"

    def test_exclude_subjects_ids(self):
        assert 0, "Not implemented"

    def test_exclude_urls(self):
        assert 0, "Not implemented"

    # DEPENDANT SETTINGS

    def test_logs_folder(self):
        assert 0, "Not implemented"

    def test_log_path(self):
        assert 0, "Not implemented"

    def test_database_path(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
class TestHiddenDownloadSettings:
    def test_forum_subfolders(self):
        assert 0, "Not implemented"

    def test_section_indexing_ids(self):
        assert 0, "Not implemented"

    def test_section_indexing_urls(self):
        assert 0, "Not implemented"

    def test_secure_section_filename(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
class TestHiddenNotifySettings:
    def test_use_base64_icons(self):
        assert 0, "Not implemented"

    def test_email(self):
        assert 0, "Not implemented"


def test_general_settings():
    from vcm.core.settings import GeneralSettings

    assert isinstance(GeneralSettings, _GeneralSettings)


def test_download_settings():
    from vcm.core.settings import DownloadSettings

    assert isinstance(DownloadSettings, _DownloadSettings)


def test_notify_settings():
    from vcm.core.settings import NotifySettings

    assert isinstance(NotifySettings, _NotifySettings)


def test_settings_classes():
    from vcm.core.settings import SETTINGS_CLASSES

    assert isinstance(SETTINGS_CLASSES, list)


def test_settings_name_to_class():
    from vcm.core.settings import settings_name_to_class

    assert isinstance(settings_name_to_class, dict)

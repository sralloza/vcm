from vcm.core.credentials import _Credentials
import pytest


class TestEmailCredentials:
    """Represents the data of a mailbox."""

    @pytest.mark.xfail
    def test_init_attributes(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_str(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_to_json(self):
        assert 0, "Not implemented"


class TestVirtualCampusCredentials:
    """Represents a student with credentials."""

    @pytest.mark.xfail
    def test_init_attributes(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_str(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_to_json(self):
        assert 0, "Not implemented"


class TestHiddenCredentials:
    @pytest.mark.xfail
    def test_init_attributes(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_make_default(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_read_credentials(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_load(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_save(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_make_example(self):
        assert 0, "Not implemented"


class TestGlobalImports:
    def test_import_1(self):
        from vcm.core.credentials import credentials

        assert isinstance(credentials, _Credentials)

    def test_import_2(self):
        from vcm.core.credentials import Credentials

        assert isinstance(Credentials, _Credentials)

    def test_import_identity(self):
        from vcm.core.credentials import credentials, Credentials

        assert credentials is Credentials

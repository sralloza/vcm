import pytest

from vcm.core.credentials import (
    EmailCredentials,
    VirtualCampusCredentials,
    _Credentials,
)


class TestEmailCredentials:
    """Represents the data of a mailbox."""

    def test_init_attributes(self):
        credentials = EmailCredentials("a", "b", "c", 5)
        assert hasattr(credentials, "username")
        assert hasattr(credentials, "password")
        assert hasattr(credentials, "smtp_server")
        assert hasattr(credentials, "smtp_port")

        assert isinstance(credentials.username, str)
        assert isinstance(credentials.password, str)
        assert isinstance(credentials.smtp_server, str)
        assert isinstance(credentials.smtp_port, int)

    def test_default_init_args(self):
        credentials = EmailCredentials("a", "b")
        assert "gmail" in credentials.smtp_server

    def test_str(self):
        credentials = EmailCredentials("<username>", "<password>")
        assert str(credentials) == "EmailCredentials(username='<username>')"

    def test_to_json(self):
        credentials = EmailCredentials("<username>", "<password>")
        creds_json = credentials.to_json()
        assert creds_json["username"] == "<username>"
        assert creds_json["password"] == "<password>"

        creds_json["username"] = "<invalid-username>"
        assert credentials.username == "<username>"


class TestVirtualCampusCredentials:
    """Represents a student with credentials."""

    def test_init_attributes(self):
        credentials = VirtualCampusCredentials("<username>", "<password>")
        assert hasattr(credentials, "username")
        assert hasattr(credentials, "password")

        assert isinstance(credentials.username, str)
        assert isinstance(credentials.password, str)

        assert credentials.username == "<username>"
        assert credentials.password == "<password>"

    def test_str(self):
        credentials = VirtualCampusCredentials("<username>", "<password>")
        assert str(credentials) == "VirtualCampusCredentials(username='<username>')"

    def test_to_json(self):
        credentials = VirtualCampusCredentials("<username>", "<password>")
        creds_json = credentials.to_json()
        assert creds_json["username"] == "<username>"
        assert creds_json["password"] == "<password>"

        creds_json["username"] = "<invalid-username>"
        assert credentials.username == "<username>"


class TestHiddenCredentials:
    @pytest.mark.xfail
    def test_init_attributes(self):
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

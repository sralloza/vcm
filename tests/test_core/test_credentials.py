from pathlib import Path
from unittest import mock

import pytest
from colorama.ansi import Fore
from toml import TomlDecodeError

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
    def test_init_attributes(self):
        assert hasattr(_Credentials, "_path")
        assert hasattr(_Credentials, "VirtualCampus")
        assert hasattr(_Credentials, "Email")

        NoneType = type(None)
        assert isinstance(_Credentials._path, Path)
        assert isinstance(
            _Credentials.VirtualCampus, (VirtualCampusCredentials, NoneType)
        )
        assert isinstance(_Credentials.Email, (EmailCredentials, NoneType))

    @mock.patch("vcm.core.credentials._Credentials.load")
    def test_call_arguments(self, load_m):
        c = _Credentials()
        load_m.assert_called_once()

        load_m.reset_mock()

        c = _Credentials(autoload=False)
        load_m.assert_not_called()

        load_m.reset_mock()

        c = _Credentials(autoload=True)
        load_m.assert_called_once()

    class TestReadCredentials:
        @pytest.fixture(autouse=True)
        def mocks(self):
            self.load_m = mock.patch("toml.load").start()
            self.path_m = mock.MagicMock()
            self.path_m.__repr__ = lambda x: repr("<credentials-path>")
            mock.patch("vcm.core.credentials._Credentials._path", self.path_m).start()

            yield

            mock.patch.stopall()

        def test_ok(self):
            result = _Credentials.read_credentials()

            self.path_m.open.assert_called_once_with(encoding="utf-8")
            pointer = self.path_m.open.return_value.__enter__.return_value
            self.load_m.assert_called_once_with(pointer)

            assert result == self.load_m.return_value

        def test_error(self, capsys):
            self.load_m.side_effect = TomlDecodeError("a", "b", 1)

            with pytest.raises(SystemExit, match="-1"):
                _Credentials.read_credentials()

            captured = capsys.readouterr()
            message = "Invalid TOML file: %r" % "<credentials-path>"
            message = Fore.LIGHTRED_EX + message + Fore.RESET + "\n"
            assert captured.err == message
            assert captured.out == ""

    class TestLoad:
        @pytest.fixture(autouse=True)
        def mocks(self):
            self.path_m = mock.MagicMock()
            self.path_m.__str__ = lambda x: "<creds-path>"
            mock.patch("vcm.core.credentials._Credentials._path", self.path_m).start()
            self.vcc_m = mock.patch(
                "vcm.core.credentials.VirtualCampusCredentials"
            ).start()
            self.em_m = mock.patch("vcm.core.credentials.EmailCredentials").start()
            self.rc_m = mock.patch(
                "vcm.core.credentials._Credentials.read_credentials"
            ).start()
            self.me_m = mock.patch(
                "vcm.core.credentials._Credentials.make_example"
            ).start()
            self.save_m = mock.patch("vcm.core.credentials._Credentials.save").start()

            yield
            mock.patch.stopall()

        def test_ok(self):
            self.rc_m.reset_mock()
            self.path_m.exists.return_value = True
            toml_data = {
                "VirtualCampus": {"data": "<vc-data>"},
                "Email": {"data": "<email-data>"},
            }
            self.rc_m.return_value = toml_data

            creds = _Credentials(autoload=False).load()

            self.rc_m.assert_called_once()
            self.vcc_m.assert_called_once_with(**toml_data["VirtualCampus"])
            self.em_m.assert_called_once_with(**toml_data["Email"])

        def test_error(self, capsys):
            self.path_m.exists.return_value = False

            with pytest.raises(SystemExit, match="-1"):
                _Credentials(autoload=False).load()

            error = "Credentials file not found, created sample (%s)" % self.path_m
            captured = capsys.readouterr()

            assert captured.err == Fore.LIGHTRED_EX + error + Fore.RESET + "\n"
            assert captured.out == ""

            self.rc_m.assert_not_called()
            self.me_m.assert_called_once()
            self.save_m.assert_called_once()

    class TestSave:
        @pytest.fixture(autouse=True)
        def mocks(self):
            self.dump_m = mock.patch("toml.dump").start()
            self.path_m = mock.MagicMock()
            self.path_m.__repr__ = lambda x: repr("<credentials-path>")
            mock.patch("vcm.core.credentials._Credentials._path", self.path_m).start()
            self.vcc_m = mock.MagicMock()
            mock.patch(
                "vcm.core.credentials._Credentials.VirtualCampus", self.vcc_m
            ).start()
            self.em_m = mock.MagicMock()
            mock.patch("vcm.core.credentials._Credentials.Email", self.em_m).start()

            yield

            mock.patch.stopall()

        def test_save(self):
            self.vcc_m.to_json.return_value = {"data": "<VirtualCampusCreds>"}
            self.em_m.to_json.return_value = {"data": "<EmailCreds>"}

            data = {
                "VirtualCampus": {"data": "<VirtualCampusCreds>"},
                "Email": {"data": "<EmailCreds>"},
            }

            _Credentials(autoload=False).save()

            self.vcc_m.to_json.assert_called_once()
            self.em_m.to_json.assert_called_once()

            self.path_m.open.assert_called_once_with("wt", encoding="utf-8")
            pointer = self.path_m.open.return_value.__enter__.return_value
            self.dump_m.assert_called_once_with(data, pointer)

    @mock.patch("vcm.core.credentials._Credentials.save")
    def test_make_example(self, save_m):
        mock.patch("vcm.core.credentials._Credentials.Email", None)
        mock.patch("vcm.core.credentials._Credentials.VirtualCampus", None)

        _Credentials.make_example()

        assert _Credentials.VirtualCampus
        assert isinstance(_Credentials.VirtualCampus, VirtualCampusCredentials)
        assert "username" in _Credentials.VirtualCampus.username
        assert "password" in _Credentials.VirtualCampus.password

        assert _Credentials.Email
        assert isinstance(_Credentials.Email, EmailCredentials)
        assert "username" in _Credentials.Email.username
        assert "password" in _Credentials.Email.password
        assert "gmail" in _Credentials.Email.smtp_server

        save_m.assert_called_once()


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

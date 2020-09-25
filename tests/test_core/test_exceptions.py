import warnings

from click.exceptions import ClickException
import pytest

from vcm.core.exceptions import (
    AliasFatalError,
    AliasNotFoundError,
    AlreadyExcludedError,
    AlreadyIndexedError,
    CredentialError,
    DownloaderError,
    FileCacheError,
    FilenameWarning,
    IdError,
    InvalidLanguageError,
    InvalidSettingsFileError,
    InvalidStateError,
    LoginError,
    LogoutError,
    MoodleError,
    NoCredentialsFoundError,
    NotExcludedError,
    NotIndexedError,
    OptionError,
    ResponseError,
    SettingsError,
    UnkownIconWarning,
    VcmError,
    VcmWarning,
)


class TestVcmError:
    def test_inheritance(self):
        exc = VcmError("message")
        assert isinstance(exc, VcmError)
        assert isinstance(exc, ClickException)

    def test_raises(self):
        with pytest.raises(VcmError):
            raise VcmError("message")


class TestLoginError:
    def test_inheritance(self):
        exc = LoginError("message")
        assert isinstance(exc, LoginError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(LoginError):
            raise LoginError("message")


class TestLogoutError:
    def test_inheritance(self):
        exc = LogoutError("message")
        assert isinstance(exc, LogoutError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(LogoutError):
            raise LogoutError("message")


class TestDownloaderError:
    def test_inheritance(self):
        exc = DownloaderError("message")
        assert isinstance(exc, DownloaderError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(DownloaderError):
            raise DownloaderError("message")


class TestCredentialError:
    def test_inheritance(self):
        exc = CredentialError("message")
        assert isinstance(exc, CredentialError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(CredentialError):
            raise CredentialError("message")


class TestNoCredentialsFoundError:
    def test_inheritance(self):
        exc = NoCredentialsFoundError("message")
        assert isinstance(exc, NoCredentialsFoundError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(NoCredentialsFoundError):
            raise NoCredentialsFoundError("message")


class TestIdError:
    def test_inheritance(self):
        exc = IdError("message")
        assert isinstance(exc, IdError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(IdError):
            raise IdError("message")


class TestAliasNotFoundError:
    def test_inheritance(self):
        exc = AliasNotFoundError("message")
        assert isinstance(exc, AliasNotFoundError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AliasNotFoundError):
            raise AliasNotFoundError("message")


class TestAliasFatalError:
    def test_inheritance(self):
        exc = AliasFatalError("message")
        assert isinstance(exc, AliasFatalError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AliasFatalError):
            raise AliasFatalError("message")


class TestFileCacheError:
    def test_inheritance(self):
        exc = FileCacheError("message")
        assert isinstance(exc, FileCacheError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(FileCacheError):
            raise FileCacheError("message")


class TestInvalidLanguageError:
    def test_inheritance(self):
        exc = InvalidLanguageError("message")
        assert isinstance(exc, InvalidLanguageError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(InvalidLanguageError):
            raise InvalidLanguageError("message")


class TestOptionError:
    def test_inheritance(self):
        exc = OptionError("message")
        assert isinstance(exc, OptionError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(OptionError):
            raise OptionError("message")


class TestInvalidStateError:
    def test_inheritance(self):
        exc = InvalidStateError("message")
        assert isinstance(exc, InvalidStateError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(InvalidStateError):
            raise InvalidStateError("message")


class TestInvalidSettingsFileError:
    def test_inheritance(self):
        exc = InvalidSettingsFileError("message")
        assert isinstance(exc, InvalidSettingsFileError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(InvalidSettingsFileError):
            raise InvalidSettingsFileError("message")


class TestSettingsError:
    def test_inheritance(self):
        exc = SettingsError("message")
        assert isinstance(exc, SettingsError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(SettingsError):
            raise SettingsError("message")


class TestAlreadyExcludedError:
    def test_inheritance(self):
        exc = AlreadyExcludedError("message")
        assert isinstance(exc, AlreadyExcludedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AlreadyExcludedError):
            raise AlreadyExcludedError("message")


class TestNotExcludedError:
    def test_inheritance(self):
        exc = NotExcludedError("message")
        assert isinstance(exc, NotExcludedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(NotExcludedError):
            raise NotExcludedError("message")


class TestAlreadyIndexedError:
    def test_inheritance(self):
        exc = AlreadyIndexedError("message")
        assert isinstance(exc, AlreadyIndexedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AlreadyIndexedError):
            raise AlreadyIndexedError("message")


class TestNotIndexedError:
    def test_inheritance(self):
        exc = NotIndexedError("message")
        assert isinstance(exc, NotIndexedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(NotIndexedError):
            raise NotIndexedError("message")


class TestMoodleError:
    def test_inheritance(self):
        exc = MoodleError("message")
        assert isinstance(exc, MoodleError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(MoodleError):
            raise MoodleError("message")


class TestResponseError:
    def test_inheritance(self):
        exc = ResponseError("message")
        assert isinstance(exc, ResponseError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(ResponseError):
            raise ResponseError("message")


# WARNINGS


class TestVcmWarning:
    def test_inheritance(self):
        warn = VcmWarning("message")
        assert isinstance(warn, VcmWarning)
        assert isinstance(warn, Warning)

    def test_warn(self):
        with pytest.warns(VcmWarning):
            warnings.warn("message", VcmWarning)


class TestUnkownIconWarning:
    def test_inheritance(self):
        warn = UnkownIconWarning("message")
        assert isinstance(warn, UnkownIconWarning)
        assert isinstance(warn, VcmWarning)

    def test_warn(self):
        with pytest.warns(UnkownIconWarning):
            warnings.warn("message", UnkownIconWarning)


class TestFilenameWarning:
    def test_inheritance(self):
        warn = FilenameWarning("message")
        assert isinstance(warn, FilenameWarning)
        assert isinstance(warn, VcmWarning)

    def test_warn(self):
        with pytest.warns(FilenameWarning):
            warnings.warn("message", FilenameWarning)

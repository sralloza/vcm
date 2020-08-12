import warnings

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
        exc = VcmError()
        assert isinstance(exc, VcmError)
        assert isinstance(exc, Exception)

    def test_raises(self):
        with pytest.raises(VcmError):
            raise VcmError


class TestLoginError:
    def test_inheritance(self):
        exc = LoginError()
        assert isinstance(exc, LoginError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(LoginError):
            raise LoginError


class TestLogoutError:
    def test_inheritance(self):
        exc = LogoutError()
        assert isinstance(exc, LogoutError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(LogoutError):
            raise LogoutError


class TestDownloaderError:
    def test_inheritance(self):
        exc = DownloaderError()
        assert isinstance(exc, DownloaderError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(DownloaderError):
            raise DownloaderError


class TestCredentialError:
    def test_inheritance(self):
        exc = CredentialError()
        assert isinstance(exc, CredentialError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(CredentialError):
            raise CredentialError


class TestNoCredentialsFoundError:
    def test_inheritance(self):
        exc = NoCredentialsFoundError()
        assert isinstance(exc, NoCredentialsFoundError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(NoCredentialsFoundError):
            raise NoCredentialsFoundError


class TestIdError:
    def test_inheritance(self):
        exc = IdError()
        assert isinstance(exc, IdError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(IdError):
            raise IdError


class TestAliasNotFoundError:
    def test_inheritance(self):
        exc = AliasNotFoundError()
        assert isinstance(exc, AliasNotFoundError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AliasNotFoundError):
            raise AliasNotFoundError


class TestAliasFatalError:
    def test_inheritance(self):
        exc = AliasFatalError()
        assert isinstance(exc, AliasFatalError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AliasFatalError):
            raise AliasFatalError


class TestFileCacheError:
    def test_inheritance(self):
        exc = FileCacheError()
        assert isinstance(exc, FileCacheError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(FileCacheError):
            raise FileCacheError


class TestInvalidLanguageError:
    def test_inheritance(self):
        exc = InvalidLanguageError()
        assert isinstance(exc, InvalidLanguageError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(InvalidLanguageError):
            raise InvalidLanguageError


class TestOptionError:
    def test_inheritance(self):
        exc = OptionError()
        assert isinstance(exc, OptionError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(OptionError):
            raise OptionError


class TestInvalidStateError:
    def test_inheritance(self):
        exc = InvalidStateError()
        assert isinstance(exc, InvalidStateError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(InvalidStateError):
            raise InvalidStateError


class TestInvalidSettingsFileError:
    def test_inheritance(self):
        exc = InvalidSettingsFileError()
        assert isinstance(exc, InvalidSettingsFileError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(InvalidSettingsFileError):
            raise InvalidSettingsFileError


class TestSettingsError:
    def test_inheritance(self):
        exc = SettingsError()
        assert isinstance(exc, SettingsError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(SettingsError):
            raise SettingsError


class TestAlreadyExcludedError:
    def test_inheritance(self):
        exc = AlreadyExcludedError()
        assert isinstance(exc, AlreadyExcludedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AlreadyExcludedError):
            raise AlreadyExcludedError


class TestNotExcludedError:
    def test_inheritance(self):
        exc = NotExcludedError()
        assert isinstance(exc, NotExcludedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(NotExcludedError):
            raise NotExcludedError


class TestAlreadyIndexedError:
    def test_inheritance(self):
        exc = AlreadyIndexedError()
        assert isinstance(exc, AlreadyIndexedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(AlreadyIndexedError):
            raise AlreadyIndexedError


class TestNotIndexedError:
    def test_inheritance(self):
        exc = NotIndexedError()
        assert isinstance(exc, NotIndexedError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(NotIndexedError):
            raise NotIndexedError


class TestMoodleError:
    def test_inheritance(self):
        exc = MoodleError()
        assert isinstance(exc, MoodleError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(MoodleError):
            raise MoodleError


class TestResponseError:
    def test_inheritance(self):
        exc = ResponseError()
        assert isinstance(exc, ResponseError)
        assert isinstance(exc, VcmError)

    def test_raises(self):
        with pytest.raises(ResponseError):
            raise ResponseError


# WARNINGS


class TestVcmWarning:
    def test_inheritance(self):
        warn = VcmWarning()
        assert isinstance(warn, VcmWarning)
        assert isinstance(warn, Warning)

    def test_warn(self):
        with pytest.warns(VcmWarning):
            warnings.warn("message", VcmWarning)


class TestUnkownIconWarning:
    def test_inheritance(self):
        warn = UnkownIconWarning()
        assert isinstance(warn, UnkownIconWarning)
        assert isinstance(warn, VcmWarning)

    def test_warn(self):
        with pytest.warns(UnkownIconWarning):
            warnings.warn("message", UnkownIconWarning)


class TestFilenameWarning:
    def test_inheritance(self):
        warn = FilenameWarning()
        assert isinstance(warn, FilenameWarning)
        assert isinstance(warn, VcmWarning)

    def test_warn(self):
        with pytest.warns(FilenameWarning):
            warnings.warn("message", FilenameWarning)

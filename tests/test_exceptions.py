import pytest

from core.exceptions import BaseVCDException, BaseDownloaderError, BaseFileCacheError, \
    AliasNotFoundError, AliasFatalError, BaseAliasError, IdError, NoCredentialsFoundError, \
    CredentialError, BaseCredentialError, FileCacheError, BaseTimeOperationError, \
    InvalidLanguageError, BaseOptionError, OptionError, DownloaderError


def test_base_vcd_exception():
    with pytest.raises(BaseVCDException):
        raise BaseVCDException

    assert issubclass(BaseVCDException, Exception)


class TestDownloaderExceptions:
    def test_base_downloader_error(self):
        with pytest.raises(BaseDownloaderError):
            raise BaseDownloaderError

        assert issubclass(BaseDownloaderError, BaseVCDException)

    def test_downloader_error(self):
        with pytest.raises(DownloaderError):
            raise DownloaderError

        assert issubclass(DownloaderError, BaseDownloaderError)


class TestCredentialExceptions:
    def test_base_credential_error(self):
        with pytest.raises(BaseCredentialError):
            raise BaseDownloaderError

        assert issubclass(BaseCredentialError, BaseVCDException)

    def test_credential_error(self):
        with pytest.raises(CredentialError):
            raise CredentialError

        assert issubclass(CredentialError, BaseCredentialError)

    def test_no_credentials_found_error(self):
        with pytest.raises(NoCredentialsFoundError):
            raise NoCredentialsFoundError

        assert issubclass(NoCredentialsFoundError, BaseCredentialError)

    def test_id_error(self):
        with pytest.raises(IdError):
            raise IdError

        assert issubclass(IdError, BaseCredentialError)


class TestAliasExceptions:
    def test_base_alias_error(self):
        with pytest.raises(BaseAliasError):
            raise BaseAliasError

        assert issubclass(BaseAliasError, BaseVCDException)

    def test_alias_not_found_error(self):
        with pytest.raises(AliasNotFoundError):
            raise AliasNotFoundError

        assert issubclass(AliasNotFoundError, BaseAliasError)

    def test_alias_fatal_error(self):
        with pytest.raises(AliasFatalError):
            raise AliasFatalError

        assert issubclass(AliasFatalError, BaseAliasError)


class TestFileCacheExceptions:
    def test_base_file_cache_error(self):
        with pytest.raises(BaseFileCacheError):
            raise BaseFileCacheError

        assert issubclass(BaseFileCacheError, BaseVCDException)

    def test_file_cache_error(self):
        with pytest.raises(FileCacheError):
            raise FileCacheError

        assert issubclass(FileCacheError, BaseFileCacheError)


class TestTimeOperationExceptions:
    def test_base_time_operation_error(self):
        with pytest.raises(BaseTimeOperationError):
            raise BaseTimeOperationError

        assert issubclass(BaseTimeOperationError, BaseVCDException)

    def test_invalid_language_error(self):
        with pytest.raises(InvalidLanguageError):
            raise InvalidLanguageError

        assert issubclass(InvalidLanguageError, BaseTimeOperationError)


class TestOptionExceptions:
    def test_base_option_error(self):
        with pytest.raises(BaseOptionError):
            raise BaseOptionError

        assert issubclass(BaseOptionError, BaseVCDException)

    def test_option_error(self):
        with pytest.raises(OptionError):
            raise OptionError

        assert issubclass(OptionError, BaseOptionError)

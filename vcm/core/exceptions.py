class VcmError(Exception):
    """Vcm error."""


class LoginError(VcmError):
    """Login error."""


class LogoutError(VcmError):
    """Logout error."""


class DownloaderError(VcmError):
    """Downloader error."""


class CredentialError(VcmError):
    """Credential error."""


class NoCredentialsFoundError(VcmError):
    """No credentials found error."""


class IdError(VcmError):
    """Id error."""


class AliasNotFoundError(VcmError):
    """Alias not found error."""


class AliasFatalError(VcmError):
    """Alias fatal error."""


class FileCacheError(VcmError):
    """File cache error."""


class InvalidLanguageError(VcmError):
    """Invalid language error."""


class OptionError(VcmError):
    """Option error."""


class InvalidStateError(VcmError):
    """Invalid state error."""


class InvalidSettingsFileError(VcmError):
    """Invalid settings file error."""


class SettingsError(VcmError):
    """Settings error."""


class AlreadyExcludedError(VcmError):
    """Already excluded error."""


class NotExcludedError(VcmError):
    """Not excluded error."""

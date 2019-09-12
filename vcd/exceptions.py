class VcdError(Exception):
    """Vcd error."""


class LoginError(VcdError):
    """Login error."""


class LogoutError(VcdError):
    """Logout error."""


class DownloaderError(VcdError):
    "Downloader error."


class CredentialError(VcdError):
    """Credential error."""


class NoCredentialsFoundError(VcdError):
    """No credentials found error."""


class IdError(VcdError):
    """Id error."""


class AliasNotFoundError(VcdError):
    """Alias not found error."""


class AliasFatalError(VcdError):
    """Alias fatal error."""


class FileCacheError(VcdError):
    """File cache error."""


class InvalidLanguageError(VcdError):
    """Invalid language error."""


class OptionError(VcdError):
    """Option error."""

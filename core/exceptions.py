class BaseVCDException(Exception):
    pass


# Downloader exceptions
class BaseDownloaderError(BaseVCDException):
    pass


class DownloaderError(BaseDownloaderError):
    pass


# Credentials exceptions
class BaseCredentialError(BaseVCDException):
    pass


class CredentialError(BaseCredentialError):
    pass


class NoCredentialsFoundError(BaseCredentialError):
    pass


class IdError(BaseCredentialError):
    pass


# Alias exceptions
class BaseAliasError(BaseVCDException):
    pass


class AliasNotFoundError(BaseAliasError):
    pass


class AliasFatalError(BaseAliasError):
    pass


# Filecache exceptions
class BaseFileCacheError(BaseVCDException):
    pass


class FileCacheError(BaseFileCacheError):
    pass


# Time operations exceptions
class BaseTimeOperationError(BaseVCDException):
    pass


class InvalidLanguageError(BaseTimeOperationError):
    pass


# Option exceptions
class BaseOptionError(BaseVCDException):
    pass


class OptionError(BaseOptionError):
    pass

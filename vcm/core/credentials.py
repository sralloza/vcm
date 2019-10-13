"""Credentials manager for the web page of the University of Valladolid."""
import toml
from colorama import Fore

from vcm.core.settings import CoreSettings


class EmailCredentials:
    """Represents the data of a mailbox."""

    def __init__(self, username, password, smtp_server=None, smtp_port=None):
        self.username = str(username)
        self.password = str(password)

        # Using gmail as default
        if smtp_server is None:
            self.smtp_server = "smtp.gmail.com"
        else:
            self.smtp_server = str(smtp_server)

        if smtp_port is None:
            self.smtp_port = 587
        else:
            self.smtp_port = int(smtp_port)

    def __str__(self):
        return "%s(username=%r)" % (self.__class__.__name__, self.username)

    def to_json(self):
        return vars(self).copy()


class VirtualCampusCredentials:
    """Represents a student with credentials."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return f"{self.__class__.__name__}(username={self.username!r})"

    def to_json(self):
        """Returns self json serialized."""
        return vars(self).copy()


class _Credentials:
    """Credentials manager."""

    _path = CoreSettings.credentials_path
    VirtualCampus: VirtualCampusCredentials = None
    Email: EmailCredentials = None

    def __init__(self, _auto=False):
        self.load()

    @classmethod
    def make_default(cls, reason):
        cls.make_example()
        exit(Fore.RED + reason + Fore.RESET)

    @classmethod
    def read_credentials(cls):
        if not cls._path.exists():
            cls.make_default(reason="Credentials file does not exist")

        with cls._path.open(encoding="utf-8") as pointer:
            try:
                return toml.load(pointer)
            except toml.TomlDecodeError:
                exit(Fore.RED + "Invalid TOML file: %r" % cls._path + Fore.RESET)

    def load(self):
        """Loads the credentials settings."""
        if not self._path.exists():

            self.make_example()
            self.save()
            return exit(
                Fore.RED
                + f"Credentials file not found, created sample ({self._path})"
                + Fore.RESET
            )

        yaml_data = self.read_credentials()

        _Credentials.VirtualCampus = VirtualCampusCredentials(
            **yaml_data["VirtualCampus"]
        )
        _Credentials.Email = EmailCredentials(**yaml_data["Email"])

    @classmethod
    def save(cls):
        """Saves the credentials to the file."""

        data = {
            "VirtualCampus": _Credentials.VirtualCampus.to_json(),
            "Email": _Credentials.Email.to_json(),
        }

        with _Credentials._path.open("wt") as file_handler:
            toml.dump(data, file_handler)

    @classmethod
    def make_example(cls):
        """Makes a dummy Student with field description."""
        _Credentials.VirtualCampus = VirtualCampusCredentials(
            "username of the virtual campus", "password of the virtual campus"
        )

        _Credentials.Email = EmailCredentials(
            "email-username@domain.es", "email-password", "smtp.domain.es", 587
        )

        cls.save()


credentials = Credentials = _Credentials()

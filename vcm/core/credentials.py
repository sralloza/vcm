"""Credentials manager for the web page of the University of Valladolid."""
import sys

import toml
from colorama import Fore

from vcm.core.settings import CoreSettings


class EmailCredentials:
    """Represents the data of a mailbox."""

    def __init__(self, username, password, smtp_server=None, smtp_port=None):
        self.username = str(username)
        self.password = str(password)

        # Using gmail as default
        self.smtp_server = str(smtp_server) if smtp_server else "smtp.gmail.com"
        self.smtp_port = int(smtp_port) if smtp_port else 587

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
        return "%s(username=%r)" % (self.__class__.__name__, self.username)

    def to_json(self):
        """Returns self json serialized."""
        return vars(self).copy()


class _Credentials:
    """Credentials manager."""

    _path = CoreSettings.credentials_path
    VirtualCampus: VirtualCampusCredentials = None
    Email: EmailCredentials = None

    def __init__(self):
        self.load()

    @classmethod
    def read_credentials(cls):
        with cls._path.open(encoding="utf-8") as pointer:
            try:
                return toml.load(pointer)
            except toml.TomlDecodeError:
                error = "Invalid TOML file: %r" % cls._path
                print(Fore.RED + error + Fore.RESET, file=sys.stderr)
                sys.exit(-1)

    def load(self):
        """Loads the credentials settings."""
        if not self._path.exists():
            self.make_example()
            self.save()
            error = "Credentials file not found, created sample (%s)" % self._path
            print(Fore.RED + error + Fore.RESET, file=sys.stderr)
            sys.exit(-1)

        toml_data = self.read_credentials()

        _Credentials.VirtualCampus = VirtualCampusCredentials(
            **toml_data["VirtualCampus"]
        )
        _Credentials.Email = EmailCredentials(**toml_data["Email"])

    @classmethod
    def save(cls):
        """Saves the credentials to the file."""

        data = {
            "VirtualCampus": cls.VirtualCampus.to_json(),
            "Email": cls.Email.to_json(),
        }

        with cls._path.open("wt") as file_handler:
            toml.dump(data, file_handler)

    @classmethod
    def make_example(cls):
        """Makes a dummy Student with field description."""
        cls.VirtualCampus = VirtualCampusCredentials(
            "username of the virtual campus", "password of the virtual campus"
        )

        cls.Email = EmailCredentials("email-username@domain.es", "email-password")

        cls.save()


credentials = Credentials = _Credentials()

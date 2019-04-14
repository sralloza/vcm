"""Credentials manager for the web page of the University of Valladolid."""
import os
from configparser import ConfigParser


class CredentialError(Exception):
    """Credential error."""


class NoCredentialsFoundError(Exception):
    """No credentials found error"""


class StudentCredentials:
    """Represents a student with credentials."""

    def __init__(self, alias, username, password):
        self.alias = alias
        self.username = username
        self.password = password

    def __str__(self):
        return f'{self.__class__.__name__}(alias={self.alias!r})'

    def to_json(self):
        """Returns self json serialized."""
        return vars(self)


class Credentials:
    """Credentials manager."""
    path = 'credentials.ini'

    def __init__(self, _auto=False):
        self._auto = _auto
        self.credentials = []
        self.load()

    def load(self):
        """Loads the credentials configuration."""
        if not os.path.isfile(self.path):
            if self._auto:
                return

            self.make_example()
            self.save()
            raise NoCredentialsFoundError('File not found, created sample')

        raw_data = ConfigParser()
        raw_data.read(self.path, encoding='utf-8')

        for student in raw_data:
            if student == 'DEFAULT':
                continue
            student_data = dict(raw_data[student])

            alias = student

            try:
                username = student_data.pop('username')
            except KeyError:
                raise CredentialError('username not found')

            try:
                password = student_data.pop('password')
            except KeyError:
                raise CredentialError('password not found')

            if student_data:
                raise CredentialError(f'Too much info: {student_data}')

            self.credentials.append(StudentCredentials(alias, username, password))

    def save(self):
        """Saves the credentials to the file."""
        config = ConfigParser()
        for person in self.credentials:
            config[person.alias] = {'username': person.username, 'password': person.password}

        with open(self.path, 'wt', encoding='utf-8') as fh:
            config.write(fh)

    @staticmethod
    def get(alias: str) -> StudentCredentials:
        """Gets the credentials from the alias.

        Args:
            alias (str): alias of the user.

        Returns:
             StudentCredentials: with alias 'alias'.

        """
        self = Credentials.__new__(Credentials)
        self.__init__()

        for user in self.credentials:
            if user.alias == alias:
                return user

        raise RuntimeError(f'User not found: {alias}')

    def make_example(self):
        """Makes a dummy Student with field description."""
        user = StudentCredentials('insert alias',
                                  'username of the virtual campus',
                                  'password of the virtual campus')

        self.credentials.append(user)
        self.save()

    @staticmethod
    def add(alias: str, username: str, password: str):
        """Adds new credentials.

        Args:
            alias (str): alias of the user.
            username (str): username of the user.
            password (str): password of the user.

        """

        self = Credentials.__new__(Credentials)
        self.__init__(_auto=True)

        user = StudentCredentials(alias, username, password)
        self.credentials.append(user)
        self.save()

"""Credentials manager for the web page of the University of Valladolid."""
import json
import os


class CredentialError(BaseException):
    """Credential error."""


class StudentCredentials:
    """Represents a student with credentials."""

    def __init__(self, alias, username, password):
        self.alias = alias
        self.username = username
        self.password = password

    def __str__(self):
        return f'{self.__class__.__name__}(alias={self.alias})'

    def to_json(self):
        """Returns self json serialized."""
        return vars(self)


class Credentials:
    """Credentials manager."""
    def __init__(self):
        self.path = 'credentials.json'
        self.credentials = []
        self.load()

    def load(self):
        """Loads the credentials configuration."""
        if not os.path.isfile(self.path):
            self.make_example()
            self.save()
            raise RuntimeError('File not found, created sample')

        try:
            with open(self.path, encoding='utf-8') as file_handler:
                raw_data = json.load(file_handler)
        except json.JSONDecodeError:
            raise RuntimeError('Credential json decode error')

        for student in raw_data:
            student_data = dict(**student)

            try:
                alias = student_data.pop('alias')
            except KeyError:
                raise CredentialError('alias not found')

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
        serial = [x.to_json() for x in self.credentials]
        with open(self.path, 'wt', encoding='utf-8') as file_handler:
            json.dump(serial, file_handler, indent=4, ensure_ascii=False)

    @staticmethod
    def get(alias):
        """Gets the credentials from the alias.

        Args:
            alias (str): alias

        Returns:
             StudentCredentials: with alias 'alias'.

        """
        self = Credentials.__new__(Credentials)
        self.__init__()

        for user in self.credentials:
            if user.alias == alias:
                return user

        raise RuntimeError('User not found')

    def make_example(self):
        """Makes a dummy Student with field description."""
        user = StudentCredentials('real name or alias to use in code',
                                  'username of the virtual campus',
                                  'password of the virtual campus')

        self.credentials.append(user)
        self.save()

import os
from configparser import ConfigParser

import pytest

from vcd.credentials import CredentialError, StudentCredentials, NoCredentialsFoundError, \
    Credentials


class TestExceptions:
    def test_credentials_error(self):
        with pytest.raises(CredentialError):
            raise CredentialError

    def test_no_credentials_found_error(self):
        with pytest.raises(NoCredentialsFoundError):
            raise NoCredentialsFoundError


class TestStudentCredentials:
    def setup_class(self):
        self.creds = StudentCredentials('peter87', 'peterpan', 'peter_passwd')

    def test_str(self):
        assert str(self.creds) == "StudentCredentials(alias='peter87')"

    def to_json(self):
        expected = {'alias': self.creds.alias, 'username': self.creds.username,
                    'password': self.creds.password}
        assert self.creds.to_json() == expected


class TestCredentials:
    def test_emtpy(self, clear_credentials):
        with pytest.raises(NoCredentialsFoundError, match='File not found, created sample'):
            Credentials.get('Something')

        config = ConfigParser()
        config.read(Credentials.path)

        assert 'insert alias' in config
        assert config['insert alias']['username'] == 'username of the virtual campus'
        assert config['insert alias']['password'] == 'password of the virtual campus'

    def test_add(self, clear_credentials):
        Credentials.add('foo', 'foo-321', 'foo-passwd')
        Credentials.add('bar', 'bar-321', 'bar-passwd')
        Credentials.add('baz', 'baz-321', 'baz-passwd')

    def test_get(self):
        foo = Credentials.get('foo')
        assert foo.alias == 'foo'
        assert foo.username == 'foo-321'
        assert foo.password == 'foo-passwd'

        bar = Credentials.get('bar')
        assert bar.alias == 'bar'
        assert bar.username == 'bar-321'
        assert bar.password == 'bar-passwd'

        baz = Credentials.get('baz')
        assert baz.alias == 'baz'
        assert baz.username == 'baz-321'
        assert baz.password == 'baz-passwd'


@pytest.fixture
def clear_credentials():
    if os.path.isfile(Credentials.path):
        os.remove(Credentials.path)

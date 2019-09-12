# -*- coding: utf-8 -*-

"""Custom downloader with retries control."""

import logging

import requests
from bs4 import BeautifulSoup

from .credentials import Credentials
from .exceptions import DownloaderError, LoginError, LogoutError

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
logger = logging.getLogger(__name__)


class Connection:
    def __init__(self):
        self._downloader = Downloader()
        self._logout_response = None
        self._login_response = None
        self._sesskey = None

    @property
    def sesskey(self):
        return self._sesskey

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def logout(self):
        self._logout_response = self.post(
            'https://campusvirtual.uva.es/login/logout.php?sesskey=%s' % self.sesskey,
            data={'sesskey': self.sesskey})

        if 'Usted no se ha identificado' not in self._logout_response.text:
            raise LogoutError

    def login(self):
        response = self.get('https://campusvirtual.uva.es/login/index.php')
        soup = BeautifulSoup(response.text, 'html.parser')

        login_token = soup.find('input', {'type': 'hidden', 'name': 'logintoken'})['value']
        logger.debug('Login token: %s', login_token)

        user = Credentials.get()

        self._login_response = self.post(
            'https://campusvirtual.uva.es/login/index.php',
            data={
                'anchor': '', 'username': user.username, 'password': user.password,
                'logintoken': login_token
            })

        soup = BeautifulSoup(self._login_response.text, 'html.parser')
        self._sesskey = soup.find('input', {'type': 'hidden', 'name': 'sesskey'})['value']

        if 'Usted se ha identificado' not in self._login_response.text:
            raise LoginError

    def get(self, url, **kwargs):
        return self._downloader.get(url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self._downloader.post(url, data=data, json=json, **kwargs)

    def delete(self, url, **kwargs):
        return self._downloader.delete(url, **kwargs)


class Downloader(requests.Session):
    """Downloader with retries control."""

    def __init__(self, retries=10, silenced=False):
        self.logger = logging.getLogger(__name__)

        if silenced is True:
            self.logger.setLevel(logging.CRITICAL)

        self._retries = retries
        super().__init__()

    def get(self, url, **kwargs):
        self.logger.debug('GET %r', url)
        retries = self._retries

        while retries > 0:
            try:
                return super().get(url, **kwargs)
            except requests.exceptions.ConnectionError:
                retries -= 1
                self.logger.warning('Connection error in GET, retries=%s', retries)
            except requests.exceptions.ReadTimeout:
                retries -= 1
                self.logger.warning('Timeout error in GET, retries=%s', retries)

        self.logger.critical('Download error in GET %r', url)
        raise DownloaderError('max retries failed.')

    def post(self, url, data=None, json=None, **kwargs):
        self.logger.debug('POST %r', url)
        retries = self._retries

        while retries > 0:
            try:
                return super().post(url=url, data=data, json=json, **kwargs)
            except requests.exceptions.ConnectionError:
                retries -= 1
                self.logger.warning('Connection error in POST, retries=%s', retries)
            except requests.exceptions.ReadTimeout:
                retries -= 1
                self.logger.warning('Timeout error in POST, retries=%s', retries)

        self.logger.critical('Download error in POST %r', url)
        raise DownloaderError('max retries failed.')

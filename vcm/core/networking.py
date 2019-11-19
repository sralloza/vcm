# -*- coding: utf-8 -*-

"""Custom downloader with retries control."""

import logging

import requests
from bs4 import BeautifulSoup

from .credentials import Credentials
from .exceptions import DownloaderError, LoginError, LogoutError
from .settings import GeneralSettings

logger = logging.getLogger(__name__)


class MetaSingleton(type):
    """Metaclass to always make class return the same instance."""

    def __init__(cls, name, bases, dict):
        super(MetaSingleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(MetaSingleton, cls).__call__(*args, **kw)
        return cls._instance


class Connection(metaclass=MetaSingleton):
    def __init__(self):
        self._downloader = Downloader()
        self._logout_response: requests.Response = None
        self._login_response: requests.Response = None
        self._sesskey: str = None
        self._user_url: str = None
        self._login_attempts = 0

    @property
    def sesskey(self):
        return self._sesskey

    @property
    def user_url(self):
        return self._user_url

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def get(self, url, **kwargs):
        return self._downloader.get(url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self._downloader.post(url, data, json, **kwargs)

    def delete(self, url, **kwargs):
        return self._downloader.delete(url, **kwargs)

    def logout(self):
        self._logout_response = self.post(
            "https://campusvirtual.uva.es/login/logout.php?sesskey=%s" % self.sesskey,
            data={"sesskey": self.sesskey},
        )

        if "Usted no se ha identificado" not in self._logout_response.text:
            raise LogoutError

    def login(self):
        try:
            self._login()
        except (KeyError, TypeError, LoginError) as exc:
            logger.warning("Needed to call again Connection.login() due to %r", exc)
            self._login_attempts += 1

            if self._login_attempts >= 10:
                raise LoginError("10 login attempts, unkwown error. See logs.") from exc
            return self.login()

    def _login(self):
        response = self.get("https://campusvirtual.uva.es/login/index.php")
        soup = BeautifulSoup(response.text, "html.parser")

        login_token = soup.find("input", {"type": "hidden", "name": "logintoken"})
        login_token = login_token["value"]

        logger.debug("Login token: %s", login_token)

        logger.info("Logging in with user %r", Credentials.VirtualCampus.username)

        self._login_response = self.post(
            "https://campusvirtual.uva.es/login/index.php",
            data={
                "anchor": "",
                "username": Credentials.VirtualCampus.username,
                "password": Credentials.VirtualCampus.password,
                "logintoken": login_token,
            },
        )

        if not self._login_response.ok:
            raise LoginError(
                "Got response with HTTP code %d" % self._login_response.status_code
            )

        soup = BeautifulSoup(self._login_response.text, "html.parser")

        if "Usted se ha identificado" not in self._login_response.text:
            raise LoginError

        self._sesskey = soup.find("input", {"type": "hidden", "name": "sesskey"})[
            "value"
        ]

        self._user_url = (
            soup.find("a", {"aria-labelledby": "actionmenuaction-2"})["href"]
            + "&showallcourses=1"
        )


class Downloader(requests.Session):
    """Downloader with retries control."""

    def __init__(self, silenced=False):
        self.logger = logging.getLogger(__name__)

        if silenced is True:
            self.logger.setLevel(logging.CRITICAL)

        super().__init__()
        self.headers.update(
            {
                "User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
            }
        )

    def get(self, url, **kwargs):
        self.logger.debug("GET %r", url)
        retries = GeneralSettings.retries

        while retries > 0:
            try:
                return super().get(url, **kwargs)
            except requests.exceptions.ConnectionError:
                retries -= 1
                self.logger.warning("Connection error in GET, retries=%s", retries)
            except requests.exceptions.ReadTimeout:
                retries -= 1
                self.logger.warning("Timeout error in GET, retries=%s", retries)

        self.logger.critical("Download error in GET %r", url)
        raise DownloaderError("max retries failed.")

    def post(self, url, data=None, json=None, **kwargs):
        self.logger.debug("POST %r", url)
        retries = GeneralSettings.retries

        while retries > 0:
            try:
                return super().post(url=url, data=data, json=json, **kwargs)
            except requests.exceptions.ConnectionError:
                retries -= 1
                self.logger.warning("Connection error in POST, retries=%s", retries)
            except requests.exceptions.ReadTimeout:
                retries -= 1
                self.logger.warning("Timeout error in POST, retries=%s", retries)

        self.logger.critical("Download error in POST %r", url)
        raise DownloaderError("max retries failed.")


connection = Connection()

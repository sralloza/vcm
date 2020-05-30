# -*- coding: utf-8 -*-

"""Custom downloader with retries control."""
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .credentials import Credentials
from .exceptions import DownloaderError, LoginError, LogoutError, MoodleError
from .settings import GeneralSettings
from .utils import save_crash_context

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/76.0.3809.100 Safari/537.36"
)


class MetaSingleton(type):
    """Metaclass to always make class return the same instance."""

    def __init__(cls, name, bases, attrs):
        super(MetaSingleton, cls).__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MetaSingleton, cls).__call__(*args, **kwargs)

        # Uncomment line to check possible singleton errors
        # logger.info("Requested Connection (id=%d)", id(cls._instance))
        return cls._instance


class Connection(metaclass=MetaSingleton):
    def __init__(self):
        self._downloader = Downloader()
        self._logout_response: Optional[requests.Response] = None
        self._login_response: Optional[requests.Response] = None
        self._sesskey: Optional[str] = None
        self._user_url: Optional[str] = None
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
        logger.debug("Logging out")
        logout_retries = 5

        while True:
            self._logout_response = self.post(
                "https://campusvirtual.uva.es/login/logout.php?sesskey=%s"
                % self.sesskey,
                data={"sesskey": self.sesskey},
            )
            if 500 <= self._logout_response.status_code <= 599:
                logout_retries -= 1

                logger.warning(
                    "Server Error during logout [%d], %d retries left",
                    self._logout_response.status_code,
                    logout_retries,
                )

                if logout_retries <= 0:
                    raise LogoutError("Logout retries expired")

                continue
            break

        if "Usted no se ha identificado" not in self._logout_response.text:
            save_crash_context(
                self._logout_response, "logout-error", "unkown error happened"
            )
            raise LogoutError("Unkown error happened")

        logger.info("Logged out")

    def login(self):
        login_attempts = 5
        try:
            logger.debug("Logging in")
            self._login()
            logger.info("Logged in")
        except Exception as exc:
            logger.warning("Needed to call again Connection.login() due to %r", exc)
            self._login_attempts += 1

            if self._login_attempts >= login_attempts:
                if self._login_response:
                    save_crash_context(
                        self._login_response, "login-error", "Login retries expired"
                    )

                raise LoginError(
                    f"{login_attempts} login attempts, unkwown error. See logs."
                ) from exc
            return self.login()

    def _login(self):
        response = self.get("https://campusvirtual.uva.es/login/index.php")
        if response.status_code == 503:
            if "maintenance" in response.reason:
                logger.critical(
                    "Moodle under maintenance (%d - %s)",
                    response.status_code,
                    response.reason,
                )
            else:
                logger.critical(
                    "Moodle error (%d - %s)", response.status_code, response.reason
                )

                raise MoodleError(
                    f"Moodle error ({response.status_code} - {response.reason})",
                )

            exit(-1)

        soup = BeautifulSoup(response.text, "html.parser")

        # Detect if user is already logged in
        if "Usted ya está en el sistema" in response.text:
            logger.info("User already logged in")
            response = self.get("https://campusvirtual.uva.es/my/")
            self.find_sesskey_and_user_url(BeautifulSoup(response.text, "html.parser"))
            return

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

        self.find_sesskey_and_user_url(soup)

    def find_sesskey_and_user_url(self, soup: BeautifulSoup):
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
        self.headers.update({"User-Agent": USER_AGENT})

    def request(self, method, url, **kwargs):
        self.logger.debug("%s %r", method, url)
        retries = GeneralSettings.retries

        while retries > 0:
            try:
                return super().request(method, url, **kwargs)
            except requests.exceptions.ConnectionError:
                retries -= 1
                self.logger.warning(
                    "Connection error in %s, retries=%s", method, retries
                )
            except requests.exceptions.ReadTimeout:
                retries -= 1
                self.logger.warning("Timeout error in %s, retries=%s", method, retries)

        self.logger.critical("Download error in %s %r", method, url)
        raise DownloaderError("max retries failed.")


connection = Connection()

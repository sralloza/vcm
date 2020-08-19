"""Custom downloader with retries control."""

import logging
import sys
from typing import Optional

from bs4 import BeautifulSoup
import requests

from vcm.settings import settings

from .credentials import Credentials
from .exceptions import DownloaderError, LoginError, LogoutError, MoodleError
from .utils import MetaSingleton, save_crash_context

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/76.0.3809.100 Safari/537.36"
)


class Connection(metaclass=MetaSingleton):
    """Manages HTTP connection with the university's servers."""

    def __init__(self):
        self._downloader = Downloader()
        self._logout_response: Optional[requests.Response] = None
        self._login_response: Optional[requests.Response] = None
        self._sesskey: Optional[str] = None
        self._user_url: Optional[str] = None
        self._login_attempts = 0

    @property
    def sesskey(self) -> str:
        """Returns the sesskey.

        Raises:
            RuntimeError: if sesskey is not defined.

        Returns:
            str: sesskey.
        """

        if not self._sesskey:
            raise RuntimeError("Sesskey not set, try to login")
        return self._sesskey

    @property
    def user_url(self) -> str:
        """Returns the user url.

        Raises:
            RuntimeError: if user-url is not set.

        Returns:
            str: user url.
        """

        if not self._user_url:
            raise RuntimeError("User url not set, try to login")
        return self._user_url

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def get(self, url, **kwargs) -> requests.Response:
        """Sends an HTTP GET request.

        Args:
            url (str): url of the request.

        Returns:
            request.Response: response.
        """

        return self._downloader.get(url, **kwargs)

    def post(self, url: str, data: dict = None, **kwargs) -> requests.Response:
        """Sends an HTTP POST request.

        Args:
            url (str): url of the request.
            data (dict, optional): data to send. Defaults to None.

        Returns:
            requests.Response: response.
        """

        return self._downloader.post(url, data, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """Sends an HTTP DELETE request.

        Args:
            url (str): url of the request.

        Returns:
            requests.Response: response.
        """

        return self._downloader.delete(url, **kwargs)

    def logout(self):
        """Logs out of the virtual campus web page.

        Raises:
            LogoutError: if the system couldn't log out.
        """

        logout_retries = settings.logout_retries
        logger.debug("Logging out (%d retries)", logout_retries)

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
        """Wrapper of real loging function.

        Raises:
            LoginError: if login was unsuccessfull.
        """

        login_retries = settings.login_retries

        while True:
            try:
                logger.debug("Logging in (%d retries left)", login_retries)
                self._login()
                logger.info("Logged in")
                return
            except Exception as exc: # pylint: disable=broad-except
                logger.warning("Needed to call again Connection.login() due to %r", exc)
                login_retries -= 1

                if login_retries <= 0:
                    if self._login_response:
                        save_crash_context(
                            self._login_response, "login-error", "Login retries expired"
                        )

                    raise LoginError(
                        f"{settings.login_retries} login attempts, unkwown error. See logs."
                    ) from exc

    def _login(self):
        """Logs into the webpage of the virtual campus. Needed to make HTTP requests.

        Raises:
            MoodleError: if moodle is under maintenance.
            LoginError: if login HTTP POST request returned wrong status.
            LoginError: if login was unsuccessfull.
        """

        response = self.get("https://campusvirtual.uva.es/login/index.php")

        if not response.ok:
            if "maintenance" in response.reason:
                logger.critical(
                    "Moodle under maintenance (%d - %s)",
                    response.status_code,
                    response.reason,
                )
                sys.exit(-1)

            logger.critical(
                "Moodle error (%d - %s)", response.status_code, response.reason
            )

            raise MoodleError(
                f"Moodle error ({response.status_code} - {response.reason})",
            )

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
        """Given a `BeautifulSoup` object parses the `user_url` and the `sesskey`.

        Args:
            soup (BeautifulSoup): HTTP response parsed with bs4.
        """

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

    #pylint: disable=arguments-differ
    def request(self, method, url, **kwargs) -> requests.Response:
        """Makes an HTTP request.

        Args:
            method (str): HTTP method of the request.
            url (str): url of the request.

        Raises:
            DownloaderError: if all retries failed.

        Returns:
            requests.Response: HTTP response.
        """

        self.logger.debug("%s %r", method, url)
        retries = settings.retries

        while retries > 0:
            try:
                return super().request(method, url, **kwargs)
            except requests.exceptions.RequestException as exc:
                excname = type(exc).__name__
                retries -= 1
                self.logger.warning(
                    "Catched %s in %s, retries=%s", excname, method, retries
                )

        self.logger.critical("Download error in %s %r", method, url)
        raise DownloaderError("max retries failed.")


connection = Connection()

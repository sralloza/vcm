from contextlib import nullcontext
import logging
from typing import Any
from unittest import mock

import pytest
import requests

from vcm.core.exceptions import DownloaderError, LoginError, LogoutError, MoodleError
from vcm.core.networking import Connection, Downloader, USER_AGENT


class TestConnection:
    @classmethod
    def setup_class(cls):
        cls.url = "https://example.com"
        cls.logger_name = "vcm.core.networking"

    @pytest.fixture(autouse=True)
    def mocks(self):
        self.downloader_m = mock.patch("vcm.core.networking.Downloader").start()
        self.scc_m = mock.patch("vcm.core.networking.save_crash_context").start()
        self.vc_creds = mock.patch(
            "vcm.core.networking.Credentials.VirtualCampus"
        ).start()
        self.vc_creds.username = "<username>"
        self.vc_creds.password = "<password>"

        self.logout_retries = 10
        self.login_retries = 10
        self.settings_m = mock.patch("vcm.core.networking.settings").start()
        self.settings_m.logout_retries = self.logout_retries
        self.settings_m.login_retries = self.login_retries

        # Restart singleton stored
        Connection._instance = None
        yield

        mock.patch.stopall()

    def test_singleton(self):
        conn1 = Connection()
        conn2 = Connection()
        conn3 = Connection()

        assert conn1 is conn2
        assert conn2 is conn3
        assert conn3 is conn1

    def test_init(self):
        conn = Connection()
        assert conn._downloader is self.downloader_m.return_value
        assert conn._logout_response is None
        assert conn._login_response is None
        assert conn._sesskey is None
        assert conn._user_url is None
        assert conn._login_attempts == 0

    @pytest.mark.parametrize(
        "sesskey,expected_raises",
        ((None, pytest.raises(RuntimeError)), ("<sesskey>", nullcontext())),
    )
    def test_sesskey_property(self, sesskey, expected_raises):
        conn = Connection()
        conn._sesskey = sesskey
        with expected_raises:
            assert conn.sesskey

    @pytest.mark.parametrize(
        "user_url,expected_raises",
        ((None, pytest.raises(RuntimeError)), ("<user-url>", nullcontext())),
    )
    def test_user_url_property(self, user_url, expected_raises):
        conn = Connection()
        conn._user_url = user_url
        with expected_raises:
            assert conn.user_url

    def test_logout_url_property(self):
        conn = Connection()
        conn._sesskey = "<sesskey>"
        assert "<sesskey>" in conn.logout_url
        assert conn._logout_url_template[:-2] in conn.logout_url

    def test_login_url_property(self):
        conn = Connection()
        assert conn._login_url_template[:-2] in conn.login_url

    @mock.patch("vcm.core.networking.Connection.logout")
    @mock.patch("vcm.core.networking.Connection.login")
    def test_context_manager(self, login_m, logout_m):
        login_m.assert_not_called()
        logout_m.assert_not_called()

        # disable false positive pylint: disable=not-context-manager
        with Connection() as conn:
            login_m.assert_called_once_with()
            logout_m.assert_not_called()
            assert conn

        login_m.assert_called_once_with()
        logout_m.assert_called_once_with()

    def test_get(self):
        conn = Connection()
        conn.get(self.url)
        self.downloader_m.return_value.get.assert_called_once_with(self.url)

    def test_post(self):
        conn = Connection()
        data = {"hello": "world"}
        conn.post(self.url, data=data)
        self.downloader_m.return_value.post.assert_called_once_with(self.url, data)

    def test_delete(self):
        conn = Connection()
        conn.delete(self.url)
        self.downloader_m.return_value.delete.assert_called_once_with(self.url)

    def test_make_logout_request(self):
        conn = Connection()
        conn._sesskey = "<sesskey>"
        response = conn.make_logout_request()
        assert response == self.downloader_m.return_value.post.return_value
        self.downloader_m.return_value.post.assert_called_once_with(
            conn.logout_url, {"sesskey": "<sesskey>"}
        )

    @mock.patch("vcm.core.networking.Connection.make_logout_request")
    def test_inner_logout_ok(self, mlr_m):
        # TODO: put real text
        text = "Usted no se ha identificado. Pulse aquí para hacerlo."
        response = mock.MagicMock(ok=True, status_code=200, text=text)
        mlr_m.return_value = response

        conn = Connection()
        conn.inner_logout()

        mlr_m.assert_called_once_with()
        self.scc_m.assert_not_called()

    @mock.patch("vcm.core.networking.Connection.make_logout_request")
    def test_inner_logout_exception(self, mlr_m):
        mlr_m.side_effect = DownloaderError

        conn = Connection()
        with pytest.raises(LogoutError, match="Logout request raised DownloaderError"):
            conn.inner_logout()

        mlr_m.assert_called_once_with()
        self.scc_m.assert_not_called()

    @pytest.mark.parametrize("status_code", [401, 501])
    @mock.patch("vcm.core.networking.Connection.make_logout_request")
    def test_inner_logout_http_status_error(self, mlr_m, status_code):
        response = mock.MagicMock(ok=False, status_code=status_code)
        mlr_m.return_value = response

        conn = Connection()
        with pytest.raises(LogoutError, match=f"Logout returned {status_code}"):
            conn.inner_logout()

        mlr_m.assert_called_once_with()
        self.scc_m.assert_not_called()

    @mock.patch("vcm.core.networking.Connection.make_logout_request")
    def test_inner_logout_fatal_logout(self, mlr_m):
        # TODO: put real text
        text = "Identificado como FEDERICO GARCÍA LORCA."
        response = mock.MagicMock(ok=True, status_code=200, text=text)
        mlr_m.return_value = response

        conn = Connection()
        with pytest.raises(LogoutError, match="Unkown error during logout"):
            conn.inner_logout()

        mlr_m.assert_called_once_with()
        self.scc_m.assert_called_once_with(conn, mock.ANY, mock.ANY)

    @mock.patch("vcm.core.networking.Connection.inner_logout")
    def test_logout_ok(self, logout_m, caplog):
        caplog.set_level(10)
        conn = Connection()
        conn.logout()

        logout_m.assert_called_once_with()
        assert caplog.record_tuples == [
            (self.logger_name, 10, "Logging out (%s retries)" % self.logout_retries),
            (self.logger_name, 20, "Logged out"),
        ]

    @pytest.mark.parametrize("nerrors", range(1, 10))
    @mock.patch("vcm.core.networking.Connection.inner_logout")
    def test_logout_some_errors(self, logout_m, caplog, nerrors):
        caplog.set_level(10)
        logout_m.side_effect = [LogoutError] * nerrors + [None]
        conn = Connection()
        conn._logout_response = mock.MagicMock(status_code=501, ok=False)
        conn.logout()

        logout_m.assert_called()
        assert logout_m.call_count == nerrors + 1

        records_expected: Any = [(10, "Logging out (%s retries)" % self.logout_retries)]
        for i in range(1, nerrors + 1):
            retries_left = self.logout_retries - i
            records_expected.append(
                (30, "Error during logout [501], %d retries left" % retries_left)
            )
        records_expected.append((20, "Logged out"))
        records_expected = [(self.logger_name,) + x for x in records_expected]
        assert caplog.record_tuples == records_expected

    @mock.patch("vcm.core.networking.Connection.inner_logout")
    def test_logout_fatal(self, logout_m, caplog):
        caplog.set_level(10)
        logout_m.side_effect = [LogoutError] * self.logout_retries + [None]
        conn = Connection()
        conn._logout_response = mock.MagicMock(status_code=501, ok=False)
        with pytest.raises(LogoutError, match="Logout retries expired"):
            conn.logout()

        logout_m.assert_called()
        assert logout_m.call_count == self.logout_retries

        records_expected: Any = [(10, "Logging out (%s retries)" % self.logout_retries)]
        for i in range(1, self.logout_retries + 1):
            retries_left = self.logout_retries - i
            records_expected.append(
                (30, "Error during logout [501], %d retries left" % retries_left)
            )
        records_expected.append((50, "Logout retries expired"))
        records_expected = [(self.logger_name,) + x for x in records_expected]
        assert caplog.record_tuples == records_expected

    def test_get_login_page(self):
        conn = Connection()
        response = conn.get_login_page()
        assert response == self.downloader_m.return_value.get.return_value
        self.downloader_m.return_value.get.assert_called_once_with(conn.login_url)

        # Test lru_cache
        response = conn.get_login_page()
        assert response == self.downloader_m.return_value.get.return_value
        self.downloader_m.return_value.get.assert_called_once_with(conn.login_url)

    @mock.patch("vcm.core.networking.Credentials.VirtualCampus")
    def test_make_login_request(self, vc_creds_m):
        conn = Connection()
        response = conn.make_login_request(login_token="<login-token>")

        assert response == self.downloader_m.return_value.post.return_value
        data = {
            "anchor": "",
            "username": vc_creds_m.username,
            "password": vc_creds_m.password,
            "logintoken": "<login-token>",
        }
        self.downloader_m.return_value.post.assert_called_once_with(
            conn.login_url, data
        )

    def test_handle_maintenance_mode(self, caplog):
        caplog.set_level(10)
        conn = Connection()
        with pytest.raises(SystemExit):
            conn.handle_maintenance_mode(404, "Not Found")

        assert caplog.record_tuples == [
            (self.logger_name, 50, "Moodle under maintenance (404 - Not Found)")
        ]

    @mock.patch("vcm.core.networking.Connection.get_login_page")
    @mock.patch("vcm.core.networking.Connection.handle_maintenance_mode")
    def test_check_already_logged_in_maintenance(self, hmm_m, glp_m, caplog):
        caplog.set_level(10)
        response = mock.MagicMock(
            ok=False, reason="Moodle is under maintenance until Monday", status_code=501
        )
        glp_m.return_value = response

        conn = Connection()

        assert conn.check_already_logged_in() == hmm_m.return_value
        glp_m.assert_called_once_with()
        hmm_m.assert_called_once_with(501, response.reason)
        assert caplog.record_tuples == []

    @mock.patch("vcm.core.networking.Connection.get_login_page")
    @mock.patch("vcm.core.networking.Connection.handle_maintenance_mode")
    def test_check_already_logged_in_server_error(self, hmm_m, glp_m, caplog):
        caplog.set_level(10)
        response = mock.MagicMock(ok=False, reason="<reason>", status_code=501)
        glp_m.return_value = response

        conn = Connection()
        with pytest.raises(MoodleError, match=r"Moodle error \(501 - <reason>\)"):
            conn.check_already_logged_in()

        glp_m.assert_called_once_with()
        hmm_m.assert_not_called()
        assert caplog.record_tuples == [
            (self.logger_name, 50, "Moodle error (501 - <reason>)")
        ]

    @mock.patch("vcm.core.networking.Connection.get_login_page")
    @mock.patch("vcm.core.networking.Connection.handle_maintenance_mode")
    def test_check_already_logged_in_server_true(self, hmm_m, glp_m, caplog):
        caplog.set_level(10)
        # TODO: put real text
        response = mock.MagicMock(
            ok=True,
            reason="<reason>",
            status_code=200,
            text="Usted ya está en el sistema como FEDERICO GARCÍA LORCA",
        )
        glp_m.return_value = response

        conn = Connection()
        assert conn.check_already_logged_in() is True

        glp_m.assert_called_once_with()
        hmm_m.assert_not_called()
        assert caplog.record_tuples == [
            (self.logger_name, 20, "User already logged in")
        ]

    @mock.patch("vcm.core.networking.Connection.get_login_page")
    @mock.patch("vcm.core.networking.Connection.handle_maintenance_mode")
    def test_check_already_logged_in_server_false(self, hmm_m, glp_m, caplog):
        caplog.set_level(10)
        # TODO: put real text
        response = mock.MagicMock(
            ok=True,
            reason="<reason>",
            status_code=200,
            text="Identificado como FEDERICO GARCÍA LORCA",
        )
        glp_m.return_value = response

        conn = Connection()
        assert conn.check_already_logged_in() is False

        glp_m.assert_called_once_with()
        hmm_m.assert_not_called()
        assert caplog.record_tuples == []

    @pytest.mark.skip(reason="Web under maintenance, no example data")
    def test_get_login_token(self):
        assert 0, "Not implemented"

    @mock.patch("vcm.core.networking.Connection.make_login_request")
    @mock.patch("vcm.core.networking.Connection.get_login_token")
    @mock.patch("vcm.core.networking.Connection.check_already_logged_in")
    def test_inner_login_already_logged_in(self, cali_m, glt_m, mlr_m, caplog):
        caplog.set_level(10)
        cali_m.return_value = True

        conn = Connection()
        assert conn.inner_login() is None

        cali_m.assert_called_once_with()
        glt_m.assert_not_called()
        mlr_m.assert_not_called()
        assert caplog.record_tuples == []

    @mock.patch("vcm.core.networking.Connection.make_login_request")
    @mock.patch("vcm.core.networking.Connection.get_login_token")
    @mock.patch("vcm.core.networking.Connection.check_already_logged_in")
    def test_inner_login_server_error(self, cali_m, glt_m, mlr_m, caplog):
        caplog.set_level(10)
        cali_m.return_value = False
        glt_m.return_value = "<token>"
        response = mock.MagicMock(ok=False, status_code=501, reason="<reason>")
        mlr_m.return_value = response

        conn = Connection()
        with pytest.raises(LoginError, match=r"Server returned 501 \(<reason>\)"):
            conn.inner_login()

        cali_m.assert_called_once_with()
        glt_m.assert_called_once_with()
        mlr_m.assert_called_once_with("<token>")
        assert caplog.record_tuples == [
            (self.logger_name, 20, "Logging in with user '<username>'")
        ]

    @mock.patch("vcm.core.networking.Connection.make_login_request")
    @mock.patch("vcm.core.networking.Connection.get_login_token")
    @mock.patch("vcm.core.networking.Connection.check_already_logged_in")
    def test_inner_login_error(self, cali_m, glt_m, mlr_m, caplog):
        caplog.set_level(10)
        cali_m.return_value = False
        glt_m.return_value = "<token>"
        # TODO: put real text
        response = mock.MagicMock(
            ok=True, status_code=200, reason="OK", text="Usted no se ha identificado"
        )
        mlr_m.return_value = response

        conn = Connection()
        with pytest.raises(LoginError, match="Unsuccessfull login"):
            conn.inner_login()

        cali_m.assert_called_once_with()
        glt_m.assert_called_once_with()
        mlr_m.assert_called_once_with("<token>")
        assert caplog.record_tuples == [
            (self.logger_name, 20, "Logging in with user '<username>'")
        ]

    @mock.patch("vcm.core.networking.Connection.make_login_request")
    @mock.patch("vcm.core.networking.Connection.get_login_token")
    @mock.patch("vcm.core.networking.Connection.check_already_logged_in")
    def test_inner_login_ok(self, cali_m, glt_m, mlr_m, caplog):
        caplog.set_level(10)
        cali_m.return_value = False
        glt_m.return_value = "<token>"
        # TODO: put real text
        response = mock.MagicMock(
            ok=True,
            status_code=200,
            reason="OK",
            text="Usted se ha identificado como FEDERICO GARCÍA LORCA",
        )
        mlr_m.return_value = response

        conn = Connection()
        conn.inner_login()

        cali_m.assert_called_once_with()
        glt_m.assert_called_once_with()
        mlr_m.assert_called_once_with("<token>")
        assert caplog.record_tuples == [
            (self.logger_name, 20, "Logging in with user '<username>'")
        ]

    @mock.patch("vcm.core.networking.save_crash_context")
    @mock.patch("vcm.core.networking.Connection.inner_login")
    def test_login_ok(self, inner_login_m, scc_m, caplog):
        caplog.set_level(10)

        conn = Connection()
        conn.login()

        inner_login_m.assert_called_once_with()
        scc_m.assert_not_called()

        assert caplog.record_tuples == [
            (self.logger_name, 10, "Logging in (10 retries left)"),
            (self.logger_name, 20, "Logged in"),
        ]

    @pytest.mark.parametrize("nerrors", range(1, 10))
    @mock.patch("vcm.core.networking.save_crash_context")
    @mock.patch("vcm.core.networking.Connection.inner_login")
    def test_login_some_errors(self, inner_login_m, scc_m, nerrors, caplog):
        caplog.set_level(10)
        inner_login_m.side_effect = [LoginError] * nerrors + [None]

        conn = Connection()
        conn.login()

        assert inner_login_m.call_count == nerrors + 1
        scc_m.assert_not_called()

        expected = []
        for i in range(nerrors + 1):
            retries_left = self.login_retries - i
            expected.append((10, "Logging in (%d retries left)" % (retries_left)))
            if i != nerrors:
                expected.append((30, "Trying to log again due to LoginError()"))

        expected.append((20, "Logged in"))
        expected = [(self.logger_name,) + x for x in expected]

        assert caplog.record_tuples == expected

    @pytest.mark.parametrize("has_login_response", [True, False])
    @mock.patch("vcm.core.networking.save_crash_context")
    @mock.patch("vcm.core.networking.Connection.inner_login")
    def test_login_fatal_error(self, inner_login_m, scc_m, caplog, has_login_response):
        caplog.set_level(10)
        inner_login_m.side_effect = [LoginError] * self.login_retries + [None]

        conn = Connection()
        if has_login_response:  # For historical reasons.
            conn._login_response = mock.MagicMock()
        with pytest.raises(LoginError, match="unknown error"):
            conn.login()

        assert inner_login_m.call_count == self.login_retries
        scc_m.assert_called_once_with(conn, mock.ANY, mock.ANY)

        expected = []
        for i in range(self.login_retries):
            retries_left = self.login_retries - i
            expected.append((10, "Logging in (%d retries left)" % (retries_left)))
            expected.append((30, "Trying to log again due to LoginError()"))

        expected = [(self.logger_name,) + x for x in expected]

        assert caplog.record_tuples == expected

    @pytest.mark.skip(reason="Web under maintenance, no example data")
    def test_find_sesskey_and_user_url(self):
        assert 0, "Not implemented"


class TestDownloader:
    @classmethod
    def setup_class(cls):
        cls.url = "https://example.com"
        cls.retries = 10

    @pytest.fixture(autouse=True)
    def mocks(self):
        self.request_m = mock.patch("requests.Session.request").start()
        self.settings_m = mock.patch("vcm.core.networking.settings").start()
        self.settings_m.retries = self.retries

        # Reset module logger
        self.logger_name = "vcm.core.networking"
        logging.getLogger(self.logger_name).setLevel(0)
        yield
        mock.patch.stopall()

    def test_not_singleton(self):
        downloader_1 = Downloader()
        downloader_2 = Downloader()
        downloader_3 = Downloader()

        assert downloader_1 is not downloader_2
        assert downloader_2 is not downloader_3
        assert downloader_3 is not downloader_1

    @pytest.mark.parametrize("silenced", [True, False])
    def test_init(self, silenced):
        downloader = Downloader(silenced=silenced)

        assert hasattr(downloader, "logger")
        if silenced:
            assert downloader.logger.level == 50
        else:
            assert downloader.logger.level == 0

        assert downloader.headers["user-agent"] == USER_AGENT
        self.request_m.assert_not_called()

    def test_request_get(self):
        Downloader().get(self.url)
        self.request_m.assert_called_once_with(
            "GET", self.url, allow_redirects=mock.ANY
        )

    def test_request_post(self):
        Downloader().post(self.url, data={"hello": "world"})
        self.request_m.assert_called_once_with(
            "POST", self.url, data={"hello": "world"}, json=mock.ANY
        )

    def test_request_delete(self):
        Downloader().delete(self.url)
        self.request_m.assert_called_once_with("DELETE", self.url)

    def test_request_put(self):
        Downloader().put(self.url)
        self.request_m.assert_called_once_with("PUT", self.url, data=mock.ANY)

    requests_exceptions = [
        "RequestException",
        "HTTPError",
        "ConnectionError",
        "Timeout",
        "URLRequired",
        "TooManyRedirects",
        "MissingSchema",
        "InvalidSchema",
        "InvalidURL",
        "InvalidHeader",
        "ChunkedEncodingError",
        "ContentDecodingError",
        "StreamConsumedError",
        "RetryError",
        "UnrewindableBodyError",
    ]

    @pytest.fixture(params=requests_exceptions)
    def exception(self, request):
        return getattr(requests.exceptions, request.param)()

    def test_request_one_error(self, exception, caplog):
        caplog.set_level(10)
        self.request_m.side_effect = [exception, mock.DEFAULT]

        Downloader().get(self.url)

        self.request_m.assert_called()
        assert self.request_m.call_count == 2

        excname = type(exception).__name__
        assert caplog.record_tuples == [
            (self.logger_name, 10, "GET %r" % self.url),
            (self.logger_name, 30, "Catched %s in GET, retries=9" % excname),
        ]

    @pytest.mark.parametrize("nerrors", range(1, 10))
    def test_request_several_errors_no_fatal(self, exception, caplog, nerrors):
        caplog.set_level(10)
        self.request_m.side_effect = [exception] * nerrors + [mock.DEFAULT]

        Downloader().get(self.url)

        self.request_m.assert_called()
        assert self.request_m.call_count == nerrors + 1

        excname = type(exception).__name__
        records_expected: Any = [(self.logger_name, 10, "GET %r" % self.url)]

        for i in range(nerrors):
            records_expected.append(
                (
                    self.logger_name,
                    30,
                    "Catched %s in GET, retries=%d" % (excname, self.retries - i + 1),
                ),
            )

    def test_request_fatal(self, exception, caplog):
        caplog.set_level(10)
        self.request_m.side_effect = [exception] * self.retries + [mock.DEFAULT]

        with pytest.raises(DownloaderError, match="max retries failed"):
            Downloader().get(self.url)

        self.request_m.assert_called()
        assert self.request_m.call_count == self.retries

        excname = type(exception).__name__
        records_expected: Any = [(10, "GET %r" % self.url)]

        for i in range(1, self.retries + 1):
            retries_left = self.retries - i
            records_expected.append(
                (30, "Catched %s in GET, retries=%d" % (excname, retries_left),),
            )

        records_expected.append((50, "Download error in GET %r" % self.url))
        records_expected = [(self.logger_name,) + x for x in records_expected]
        assert caplog.record_tuples == records_expected

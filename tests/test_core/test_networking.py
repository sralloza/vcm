import logging
from collections import Counter
from unittest import mock

import pytest
from bs4 import BeautifulSoup
from requests import exceptions as req_exc

from vcm.core.exceptions import DownloaderError, LoginError, LogoutError
from vcm.core.networking import USER_AGENT, Connection, Downloader
from vcm.core.utils import MetaSingleton


class TestConnection:
    @pytest.fixture(scope="function", autouse=True)
    def reset_connection(self):
        Connection._instance = None
        yield

    def test_use_singleton(self):
        assert type(Connection) == MetaSingleton

        a = Connection()
        b = Connection()
        c = Connection()

        assert a is b
        assert b is c
        assert c is a

    def test_init_declaration(self):
        connection = Connection()

        assert hasattr(connection, "_downloader")
        assert hasattr(connection, "_logout_response")
        assert hasattr(connection, "_login_response")
        assert hasattr(connection, "_sesskey")
        assert hasattr(connection, "_user_url")
        assert hasattr(connection, "_login_attempts")

    def test_properties(self):
        connection = Connection()

        assert hasattr(connection, "sesskey")
        assert hasattr(connection, "user_url")

        assert connection.sesskey is None
        assert connection.user_url is None

    @mock.patch("vcm.core.networking.Connection.logout")
    @mock.patch("vcm.core.networking.Connection.login")
    def test_context_manager(self, login_m, logout_m):
        with Connection():
            login_m.assert_called()
            logout_m.assert_not_called()

        logout_m.assert_called_once()
        login_m.assert_called_once()

    @mock.patch("vcm.core.networking.Downloader.get")
    def test_get(self, get_m):
        connection = Connection()
        connection.get("url")
        get_m.assert_called_once_with("url")

    @mock.patch("vcm.core.networking.Downloader.post")
    def test_post(self, post_m):
        connection = Connection()
        connection.post("url", "data", "json")
        post_m.assert_called_once_with("url", "data", "json")

    @mock.patch("vcm.core.networking.Downloader.delete")
    def test_delete(self, delete_m):
        connection = Connection()
        connection.delete("url")
        delete_m.assert_called_once_with("url")

    @mock.patch("vcm.core.networking.Connection.post")
    @pytest.mark.parametrize("logout_success", [True, False])
    def test_logout(self, post_m, logout_success, caplog):
        caplog.set_level(10, logger="vcm.core.networking")
        interface = mock.MagicMock()
        if logout_success:
            interface.text = (
                '<div class="usermenu"><span class="login">'
                'Usted no se ha identificado. (<a href="https://campusvirtual'
                '.uva.es/login/index.php">Acceder</a>)</span></div>'
            )
        else:
            interface.text = ""

        post_m.return_value = interface

        connection = Connection()
        connection._sesskey = "<sesskey>"

        if not logout_success:
            with pytest.raises(LogoutError):
                connection.logout()
        else:
            connection.logout()

        post_m.assert_called_once()
        assert ("vcm.core.networking", 10, "Logging out") in caplog.record_tuples

    class TestLogin:
        @pytest.fixture(params=[KeyError, TypeError, LoginError])
        def exception(self, request):
            return request.param

        @pytest.fixture(scope="function", autouse=True)
        def mocks(self):
            self.log_in_m = mock.patch("vcm.core.networking.Connection._login").start()
            self.gs_m = mock.patch("vcm.core.networking.GeneralSettings").start()
            self.dt_m = mock.patch("vcm.core.networking.datetime").start()

            self.now_m = mock.MagicMock()
            self.now_m.strftime.return_value = "<now>"
            self.dt_m.now.return_value = self.now_m

            yield

            mock.patch.stopall()

        def test_ok(self, caplog):
            caplog.set_level(10, "vcm.core.networking")

            connection = Connection()
            connection.login()

            assert connection._login_attempts == 0
            self.log_in_m.assert_called_once()

            assert caplog.records[0].message == "Logging in"
            assert caplog.records[-1].message == "Logged in"

            log_calls = Counter([x.levelname for x in caplog.records])

            assert log_calls["DEBUG"] == 1
            assert log_calls["INFO"] == 1
            assert log_calls["WARNING"] == 0
            assert log_calls["CRITICAL"] == 0

        @pytest.mark.parametrize("nerrors", range(1, 10))
        def test_some_errors(self, caplog, nerrors, exception):
            caplog.set_level(10, "vcm.core.networking")

            self.log_in_m.side_effect = [exception] * nerrors + [None]

            connection = Connection()
            connection.login()

            assert caplog.records[0].message == "Logging in"
            assert caplog.records[-1].message == "Logged in"
            assert "Needed to call again Connection.login" in caplog.records[-3].message

            log_calls = Counter([x.levelname for x in caplog.records])

            assert log_calls["DEBUG"] == nerrors + 1
            assert log_calls["INFO"] == 1
            assert log_calls["WARNING"] == nerrors
            assert log_calls["CRITICAL"] == 0

        @pytest.mark.parametrize("nerrors", range(10, 16))
        def test_fatal_error(self, caplog, nerrors, exception):
            caplog.set_level(10, "vcm.core.networking")

            self.log_in_m.side_effect = [exception] * nerrors + [None]

            connection = Connection()
            connection._login_response = mock.MagicMock(text="")

            with pytest.raises(LoginError):
                connection.login()

            assert caplog.records[0].message == "Logging in"
            assert caplog.records[-1].message != "Logged in"
            log_id = "login.error.<now>.html"
            critical = "Unkown error. saved with id='%s'" % log_id
            assert caplog.records[-1].message == critical
            assert caplog.records[-1].levelname == "CRITICAL"
            assert "Needed to call again Connection.login" in caplog.records[-2].message

            log_calls = Counter([x.levelname for x in caplog.records])

            assert log_calls["DEBUG"] == 10
            assert log_calls["INFO"] == 0
            assert log_calls["WARNING"] == 10
            assert log_calls["CRITICAL"] == 1

            jp_m = self.gs_m.root_folder.joinpath
            jp_m.assert_called_once_with(log_id)
            jp_m.return_value.write_text.assert_called_once_with("", encoding="utf-8")

    class TestHiddenLogin:
        @pytest.fixture(scope="function", autouse=True)
        def mocks(self):
            self.get_m = mock.patch("vcm.core.networking.Connection.get").start()
            self.post_m = mock.patch("vcm.core.networking.Connection.post").start()
            self.creds_m = mock.patch("vcm.core.networking.Credentials").start()
            self.fsauu_m = mock.patch(
                "vcm.core.networking.Connection.find_sesskey_and_user_url"
            ).start()
            yield
            mock.patch.stopall()

        def test_maintenance(self, caplog):
            text = "The site is undergoing maintenance and is currently not available"
            interface = mock.MagicMock()
            interface.text = text
            interface.reason = text
            interface.status_code = 503
            self.get_m.return_value = interface

            caplog.set_level(10, logger="vcm.core.networking")

            connection = Connection()

            with pytest.raises(SystemExit, match="-1"):
                connection._login()

            assert (
                "vcm.core.networking",
                50,
                "Moodle under maintenance (503 - %s)" % text,
            ) in caplog.record_tuples
            self.get_m.assert_called_once()
            self.post_m.assert_not_called()

        def test_already_logged_in(self, caplog):
            text = (
                '<div role="alert" data-aria-autofocus="true" id="modal-body" '
                'class="box modal-body py-3" tabindex="0"><p>Usted ya está en el sist'
                "ema como <surname> <second-surname>, <name>, es necesario cerrar la "
                "sesión antes de acceder como un usuario diferente.</p></div>"
            )
            interface_valid = mock.MagicMock(text=text)
            interface_invalid = mock.MagicMock(text="<invalid>")
            self.get_m.side_effect = [interface_valid, interface_invalid]

            caplog.set_level(10, logger="vcm.core.networking")

            connection = Connection()
            connection._login()

            assert (
                "vcm.core.networking",
                20,
                "User already logged in",
            ) in caplog.record_tuples
            self.get_m.assert_called()
            assert self.get_m.call_count == 2
            self.post_m.assert_not_called()

            self.fsauu_m.assert_called_once()

        def test_bad_response_login(self, caplog):
            self.creds_m.VirtualCampus.username = "<username>"
            self.creds_m.VirtualCampus.password = "<password>"

            self.get_m.return_value = mock.MagicMock(
                text='<input type="hidden" name="logintoken" value="<login-token>">'
            )
            self.post_m.return_value = mock.MagicMock(ok=False, status_code=404)

            caplog.set_level(10, "vcm.core.networking")

            connection = Connection()
            with pytest.raises(LoginError, match="Got response with HTTP code 404"):
                connection._login()

            assert (
                "vcm.core.networking",
                10,
                "Login token: <login-token>",
            ) in caplog.record_tuples
            assert (
                "vcm.core.networking",
                20,
                "Logging in with user '<username>'",
            ) in caplog.record_tuples

            self.post_m.assert_called_once_with(
                "https://campusvirtual.uva.es/login/index.php",
                data={
                    "anchor": "",
                    "username": "<username>",
                    "password": "<password>",
                    "logintoken": "<login-token>",
                },
            )

        def test_bad_login(self, caplog):
            self.creds_m.VirtualCampus.username = "<username>"
            self.creds_m.VirtualCampus.password = "<password>"

            self.get_m.return_value = mock.MagicMock(
                text='<input type="hidden" name="logintoken" value="<login-token>">'
            )
            self.post_m.return_value = mock.MagicMock(ok=True, text="<incorrect-login>")

            caplog.set_level(10, "vcm.core.networking")

            connection = Connection()
            with pytest.raises(LoginError):
                connection._login()

            assert (
                "vcm.core.networking",
                10,
                "Login token: <login-token>",
            ) in caplog.record_tuples
            assert (
                "vcm.core.networking",
                20,
                "Logging in with user '<username>'",
            ) in caplog.record_tuples

            self.post_m.assert_called_once_with(
                "https://campusvirtual.uva.es/login/index.php",
                data={
                    "anchor": "",
                    "username": "<username>",
                    "password": "<password>",
                    "logintoken": "<login-token>",
                },
            )

            self.fsauu_m.assert_not_called()

        def test_ok(self, caplog):
            text = (
                ' <div class="logininfo">Usted se ha identificado como '
                '<a href="https://campusvirtual.uva.es/user/profile.php?id=<id'
                '>" title="Ver perfil"><surname> <second-surname>, <name></a> '
                '(<a href="https://campusvirtual.uva.es/login/logout.php?sessk'
                'ey=0iujR0AiRK">Salir</a>)</div>'
            )
            self.creds_m.VirtualCampus.username = "<username>"
            self.creds_m.VirtualCampus.password = "<password>"

            self.get_m.return_value = mock.MagicMock(
                text='<input type="hidden" name="logintoken" value="<login-token>">'
            )
            self.post_m.return_value = mock.MagicMock(ok=True, text=text)

            caplog.set_level(10, "vcm.core.networking")

            connection = Connection()
            connection._login()

            assert (
                "vcm.core.networking",
                10,
                "Login token: <login-token>",
            ) in caplog.record_tuples
            assert (
                "vcm.core.networking",
                20,
                "Logging in with user '<username>'",
            ) in caplog.record_tuples

            self.post_m.assert_called_once_with(
                "https://campusvirtual.uva.es/login/index.php",
                data={
                    "anchor": "",
                    "username": "<username>",
                    "password": "<password>",
                    "logintoken": "<login-token>",
                },
            )

            self.fsauu_m.assert_called_once()

    def test_find_sesskey_and_user_url(self):
        text = (
            '<input type="hidden" name="sesskey" value="<sesskey>">'
            '<a href="https://campusvirtual.uva.es/user/profile.php?id=<id>"'
            ' class="dropdown-item menu-action" role="menuitem" data-title="'
            'profile,moodle" aria-labelledby="actionmenuaction-2"><i class="'
            'icon fa fa-user fa-fw" aria-hidden="true"></i><span class="men'
            'u-action-text" id="actionmenuaction-2">Perfil</span></a>'
        )

        soup = BeautifulSoup(text, "html.parser")
        connection = Connection()
        connection.find_sesskey_and_user_url(soup)

        assert connection.sesskey == "<sesskey>"
        assert (
            connection.user_url == "https://campusvirtual.uva.es/user/profile.php?"
            "id=<id>&showallcourses=1"
        )


REQUESTS_EXCEPTIONS = (
    req_exc.URLRequired,
    req_exc.TooManyRedirects,
    req_exc.HTTPError,
    req_exc.ConnectionError,
    req_exc.ConnectTimeout,
    req_exc.ReadTimeout,
)


@mock.patch("requests.Session.request")
class TestDownloader:
    def test_use_singleton(self, req_m):
        assert type(Downloader) == MetaSingleton

        a = Downloader()
        b = Downloader()
        c = Downloader()

        assert a is b
        assert b is c
        assert c is a

        req_m.assert_not_called()
        assert req_m._mock_children == {}

    @pytest.fixture(scope="function", autouse=True)
    def reset_singleton(self):
        Downloader._instance = None
        logging.getLogger("vcm.core.networking").setLevel(10)

    @pytest.mark.parametrize("silenced", [False, True])
    def test_init_declaration(self, req_m, silenced):
        downloader = Downloader(silenced=silenced)
        assert hasattr(downloader, "logger")
        assert downloader.headers["User-Agent"] == USER_AGENT

        if silenced:
            assert downloader.logger.level == 50
        else:
            # Force level=DEBUG in reset_singleton (autouse fixture)
            assert downloader.logger.level == 10

        req_m.assert_not_called()
        assert req_m._mock_children == {}

    def test_get(self, req_m, caplog):
        downloader = Downloader()
        downloader.get("some-url")
        req_m.assert_called_with("GET", "some-url", allow_redirects=True)
        assert "GET 'some-url'" in caplog.text

    def test_post(self, req_m, caplog):
        downloader = Downloader()
        downloader.post("some-url", data="data", json="json")
        req_m.assert_called_with("POST", "some-url", data="data", json="json")
        assert "POST 'some-url'" in caplog.text

    def test_delete(self, req_m, caplog):
        downloader = Downloader()
        downloader.delete("some-url")
        req_m.assert_called_with("DELETE", "some-url")
        assert "DELETE 'some-url'" in caplog.text

    def test_put(self, req_m, caplog):
        downloader = Downloader()
        downloader.put("some-url", data="data")
        req_m.assert_called_with("PUT", "some-url", data="data")
        assert "PUT 'some-url'" in caplog.text

    def test_head(self, req_m, caplog):
        downloader = Downloader()
        downloader.head("some-url")
        # Default allow_redirects for HEAD is false
        req_m.assert_called_with("HEAD", "some-url", allow_redirects=False)
        assert "HEAD 'some-url'" in caplog.text

    @pytest.fixture(params=REQUESTS_EXCEPTIONS)
    def error_class(self, request):
        return request.param

    @pytest.fixture(params=range(1, 5))
    def retries(self, request):
        return request.param

    @pytest.fixture(params=range(5))
    def nerrors(self, request):
        return request.param

    @mock.patch("vcm.core.networking.GeneralSettings")
    def test_retry_control(self, gs_m, req_m, caplog, nerrors, retries, error_class):
        req_m.side_effect = [error_class] * nerrors + ["response"]
        gs_m.retries = retries
        caplog.set_level(10)

        downloader = Downloader()

        if nerrors > retries:
            with pytest.raises(DownloaderError):
                downloader.post("some-url", "data", "json")
        else:
            downloader.post("some-url", "data", "json")

        req_m.assert_called()
        logger_method_count = Counter([x.levelname for x in caplog.records])

        if nerrors:
            assert "%s in POST" % error_class.__name__ in caplog.text

        if nerrors > retries:
            assert req_m.call_count == retries + 1
            assert logger_method_count["DEBUG"] == 1
            assert logger_method_count["INFO"] == 0
            assert logger_method_count["WARNING"] == retries + 1
            assert logger_method_count["CRITICAL"] == 1
        else:
            assert req_m.call_count == nerrors + 1
            assert logger_method_count["DEBUG"] == 1
            assert logger_method_count["INFO"] == 0
            assert logger_method_count["WARNING"] == nerrors
            assert logger_method_count["CRITICAL"] == 0

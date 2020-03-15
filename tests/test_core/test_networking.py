import logging
from collections import Counter
from unittest import mock

import pytest
from requests import exceptions as req_exc

from vcm.core.exceptions import DownloaderError
from vcm.core.networking import USER_AGENT, Connection, Downloader
from vcm.core.utils import MetaSingleton


class TestConnection:
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

    def test_logout(self):
        assert 0, "Not implemented"

    def test_login(self):
        assert 0, "Not implemented"

    def test_hidden_login(self):
        assert 0, "Not implemented"

    def test_find_sesskey_and_user_url(self):
        assert 0, "Not implemented"


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

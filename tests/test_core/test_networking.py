import logging
from typing import Any
from unittest import mock

import pytest
import requests

from vcm.core.exceptions import DownloaderError
from vcm.core.networking import Downloader, USER_AGENT


class TestDownloader:
    @classmethod
    def setup_class(cls):
        cls.url = "https://www.google.es"
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
        d1 = Downloader()
        d2 = Downloader()
        d3 = Downloader()

        assert d1 is not d2
        assert d2 is not d3
        assert d3 is not d1

    @pytest.mark.parametrize("silenced", [True, False])
    def test_init(self, silenced):
        d = Downloader(silenced=silenced)

        assert hasattr(d, "logger")
        if silenced:
            assert d.logger.level == 50
        else:
            assert d.logger.level == 0

        assert d.headers["user-agent"] == USER_AGENT
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
        records_expected: Any = [(self.logger_name, 10, "GET %r" % self.url)]

        for i in range(self.retries):
            records_expected.append(
                (
                    self.logger_name,
                    30,
                    "Catched %s in GET, retries=%d" % (excname, self.retries - i + 1),
                ),
            )

        records_expected.append(
            (self.logger_name, 50, "Downloader error in GET %r" % self.url)
        )

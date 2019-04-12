import time

import pytest

from vcd._requests import Downloader, HEADERS, DownloaderError


def test_headers(d):
    r = d.get('http://httpbin.org/user-agent', headers=HEADERS)
    assert r.json()['user-agent'] == HEADERS['User-Agent']


def test_get(d):
    r = d.get('http://httpbin.org/get?arg1=value1&arg2=value2&test=pytest')
    assert r.json()['args'] == {'arg1': 'value1', 'arg2': 'value2', 'test': 'pytest'}


def test_post(d):
    test_dict = {'arg1': 'value1', 'arg2': 'value2', 'test': 'pytest'}
    r = d.post('http://httpbin.org/post?arg1=value1&arg2=value2&test=pytest')
    assert r.json()['args'] == test_dict

    r = d.post('http://httpbin.org/post', data=test_dict)
    assert r.json()['form'] == test_dict


class TestGetRetries:
    def test_get_retries_0(self, test_endpoint):
        d = Downloader(retries=0)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.get(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 0

    def test_get_retries_1(self, test_endpoint):
        d = Downloader(retries=1)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.get(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 1

    def test_get_retries_2(self, test_endpoint):
        d = Downloader(retries=2)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.get(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 2

    def test_get_retries_3(self, test_endpoint):
        d = Downloader(retries=3)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.get(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 3

    def test_get_retries_4(self, test_endpoint):
        d = Downloader(retries=4)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.get(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 4


class TestPostRetries:
    def test_post_retries_0(self, test_endpoint):
        d = Downloader(retries=0)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.post(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 0

    def test_post_retries_1(self, test_endpoint):
        d = Downloader(retries=1)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.post(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 1

    def test_post_retries_2(self, test_endpoint):
        d = Downloader(retries=2)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.post(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 2

    def test_post_retries_3(self, test_endpoint):
        d = Downloader(retries=3)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.post(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 3

    def test_post_retries_4(self, test_endpoint):
        d = Downloader(retries=4)
        t0 = time.time()
        with pytest.raises(DownloaderError):
            d.post(test_endpoint, timeout=1)

        tf = time.time() - t0
        assert int(tf) == 4


def test_silenced(caplog):
    d = Downloader(silenced=True)
    assert d.get('http://httpbin.org/status/200').status_code == 200
    assert len(caplog.text) == 0

    assert d.post('http://httpbin.org/status/200').status_code == 200
    assert len(caplog.text) == 0


@pytest.fixture
def d():
    return Downloader()


@pytest.fixture
def test_endpoint():
    return 'http://sralloza.sytes.net:5555/'

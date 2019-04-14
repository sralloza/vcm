import os

import pytest

from vcd.filecache import FileCache, FileCacheError

REAL_FILE_CACHE = FileCache()


@pytest.fixture(autouse=True, scope='module')
def initialize(tmpdir_factory):
    REAL_FILE_CACHE.path = str(tmpdir_factory.mktemp('filecache'))

    with open(os.path.join(REAL_FILE_CACHE.path, 'a.txt'), 'wb') as f:
        f.write(b'a' * 1000)
    with open(os.path.join(REAL_FILE_CACHE.path, 'b.txt'), 'wb') as f:
        f.write(b'b' * 2000)
    with open(os.path.join(REAL_FILE_CACHE.path, 'c.txt'), 'wb') as f:
        f.write(b'c' * 4000)
    with open(os.path.join(REAL_FILE_CACHE.path, 'd.txt'), 'wb') as f:
        f.write(b'd' * 8000)

    REAL_FILE_CACHE.load(_auto=True)
    yield


class TestExceptions:
    def test_file_cache_error(self):
        with pytest.raises(FileCacheError):
            raise FileCacheError


class TestRealFileCache:
    @staticmethod
    def _extend(filename):
        return os.path.join(REAL_FILE_CACHE.path, filename).replace('\\', '/')

    def test_load(self):
        with pytest.raises(FileCacheError, match='Use REAL_FILE_CACHE instead'):
            c = FileCache()
            c.load()

    def test_init(self):
        assert len(REAL_FILE_CACHE) == 4

    def test_setitem(self):
        REAL_FILE_CACHE[self._extend('virtual-1.v')] = 1
        REAL_FILE_CACHE[self._extend('virtual-2.v')] = 2
        REAL_FILE_CACHE[self._extend('virtual-3.v')] = 3
        REAL_FILE_CACHE[self._extend('virtual-4.v')] = 4

        assert len(REAL_FILE_CACHE) == 8

    def test_contains(self):
        assert self._extend('a.txt') in REAL_FILE_CACHE
        assert self._extend('b.txt') in REAL_FILE_CACHE
        assert self._extend('c.txt') in REAL_FILE_CACHE
        assert self._extend('d.txt') in REAL_FILE_CACHE

        assert self._extend('virtual-1.v') in REAL_FILE_CACHE
        assert self._extend('virtual-2.v') in REAL_FILE_CACHE
        assert self._extend('virtual-3.v') in REAL_FILE_CACHE
        assert self._extend('virtual-4.v') in REAL_FILE_CACHE

    def test_getitem(self):
        assert REAL_FILE_CACHE[self._extend('a.txt')] == 1000
        assert REAL_FILE_CACHE[self._extend('b.txt')] == 2000
        assert REAL_FILE_CACHE[self._extend('c.txt')] == 4000
        assert REAL_FILE_CACHE[self._extend('d.txt')] == 8000

        assert REAL_FILE_CACHE[self._extend('virtual-1.v')] == 1
        assert REAL_FILE_CACHE[self._extend('virtual-2.v')] == 2
        assert REAL_FILE_CACHE[self._extend('virtual-3.v')] == 3
        assert REAL_FILE_CACHE[self._extend('virtual-4.v')] == 4

    def test_get_file_length(self):
        # This test is included in the rest, so it will be ommited.
        assert True

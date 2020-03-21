from pathlib import Path
from threading import Lock

import pytest

from vcm.core.results import Counters, Results


class TestCounters:
    @pytest.fixture(autouse=True)
    def reset(self):
        Counters.updated = 0
        Counters.new = 0

        yield

        Counters.updated = 0
        Counters.new = 0

    def test_attributes(self):
        assert hasattr(Counters, "updated")
        assert hasattr(Counters, "new")

        assert isinstance(Counters.updated, int)
        assert isinstance(Counters.new, int)

    def test_count_updated(self):
        Counters.updated = 0
        internal_counter = 0
        for i in range(20):
            Counters.count_updated()
            internal_counter += 1
            assert Counters.updated == internal_counter

    def test_count_new(self):
        Counters.new = 0
        internal_counter = 0
        for i in range(20):
            Counters.count_new()
            internal_counter += 1
            assert Counters.new == internal_counter


class TestResults:
    def test_attributes(self):
        assert hasattr(Results, "print_lock")
        assert hasattr(Results, "file_lock")
        assert hasattr(Results, "result_path")

        lock_type = type(Lock())
        assert isinstance(Results.print_lock, lock_type)
        assert isinstance(Results.file_lock, lock_type)
        assert isinstance(Results.result_path, Path)

    @pytest.mark.xfail
    def test_print_updated(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_print_new(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_add_to_result_file(self):
        assert 0, "Not implemented"

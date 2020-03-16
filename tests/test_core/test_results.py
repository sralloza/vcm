from pathlib import Path
from threading import Lock

import pytest

from vcm.core.results import Counters, Results


class TestCounters:
    def test_attributes(self):
        assert hasattr(Counters, "updated")
        assert hasattr(Counters, "new")

        assert isinstance(Counters.updated, int)
        assert isinstance(Counters.new, int)

    @pytest.mark.xfail
    def test_count_updated(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_count_new(self):
        assert 0, "Not implemented"


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

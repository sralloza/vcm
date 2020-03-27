from pathlib import Path
from threading import Lock
from unittest import mock

import pytest
from colorama import Fore

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
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.counters_m = mock.patch("vcm.core.results.Counters").start()
        self.print_m = mock.patch("vcm.core.results.Printer.print", print).start()
        self.print_lock_p = mock.patch("vcm.core.results.Results.print_lock")
        self.file_lock_p = mock.patch("vcm.core.results.Results.file_lock")
        self.print_lock_m = self.print_lock_p.start()
        self.file_lock_m = self.file_lock_p.start()

        yield
        mock.patch.stopall()

    def test_attributes(self):
        # Don't mock locks
        self.print_lock_p.stop()
        self.file_lock_p.stop()

        assert hasattr(Results, "print_lock")
        assert hasattr(Results, "file_lock")
        assert hasattr(Results, "result_path")

        lock_type = type(Lock())
        assert isinstance(Results.print_lock, lock_type)
        assert isinstance(Results.file_lock, lock_type)
        assert isinstance(Results.result_path, Path)

    @mock.patch("vcm.core.results.Results.add_to_result_file")
    def test_print_updated(self, atrf_m, capsys):
        self.counters_m.updated = 25
        Results.print_updated("/path/to/file")
        message = "File updated no.  25: /path/to/file"
        color_message = Fore.LIGHTYELLOW_EX + message + Fore.RESET

        self.counters_m.count_updated.assert_called_once()
        atrf_m.assert_called_with(message)
        captured = capsys.readouterr()
        assert captured.out == color_message + "\n"
        assert captured.err == ""

        self.print_lock_m.__enter__.assert_called_once()
        self.print_lock_m.__exit__.assert_called_once()

    @mock.patch("vcm.core.results.Results.add_to_result_file")
    def test_print_new(self, atrf_m, capsys):
        self.counters_m.new = 25
        Results.print_new("/path/to/file")
        message = "New file no.  25: /path/to/file"
        color_message = Fore.LIGHTGREEN_EX + message + Fore.RESET

        self.counters_m.count_new.assert_called_once()
        atrf_m.assert_called_with(message)
        captured = capsys.readouterr()
        assert captured.out == color_message + "\n"
        assert captured.err == ""

        self.print_lock_m.__enter__.assert_called_once()
        self.print_lock_m.__exit__.assert_called_once()

    @mock.patch("vcm.core.results.Results.result_path")
    def test_add_to_result_file(self, res_path_m):
        Results.add_to_result_file("/path/to/file")

        res_path_m.open.assert_called_once_with("at", encoding="utf-8")
        res_path_m.open.return_value.__enter__.assert_called_once()
        res_path_m.open.return_value.__enter__.return_value.write.assert_called_once()
        res_path_m.open.return_value.__exit__.assert_called_once()

        self.file_lock_m.__enter__.assert_called_once()
        self.file_lock_m.__exit__.assert_called_once()

from unittest import mock

import pytest
from colorama.ansi import Fore

import vcm
from vcm.core.utils import Patterns, Printer, check_updates, exception_exit


class TestPatterns:
    filename_data = (
        ('filename="a.txt"', "a.txt"),
        ('filename="cool.html"', "cool.html"),
        ('filename="hello-there-93.jpg"', "hello-there-93.jpg"),
        ('filename="consider spacing true.txt"', "consider spacing true.txt"),
        ('filename="IS_BI_2_20.xlsx"', "IS_BI_2_20.xlsx"),
        ('filename="important (2020_2021).pdf"', "important (2020_2021).pdf"),
        ('filename="accents [áéíóúñÁÉÍÓÚÑ]()"', "accents [áéíóúñÁÉÍÓÚÑ]()"),
        ('filename="-.,_;~+`^´¨{[]\'¡¿!@#·$%&/€"', "-.,_;~+`^´¨{[]'¡¿!@#·$%&/€"),
        ('filename="-.,_:;~+`*^´¨{[]\'¡¿?!|@#·$%&/"', None),
    )

    @pytest.mark.parametrize("input_str, expected", filename_data)
    def test_filename_pattern(self, input_str, expected):
        match = Patterns.FILENAME_PATTERN.search(input_str)

        if expected:
            assert match.group(1) == expected
        else:
            assert match is None


class TestExceptionExit:
    exceptions = (
        (ValueError, "Invalid path"),
        (TypeError, ("Invalid type", "Expected int")),
        (ImportError, "Module not found: math"),
    )

    @pytest.mark.parametrize("red", [True, False])
    @pytest.mark.parametrize("to_stderr", [True, False])
    @pytest.mark.parametrize("exception, args", exceptions)
    def test_ok(self, exception, args, to_stderr, red, capsys):
        if not isinstance(args, str):
            message = ", ".join(args)
        else:
            message = args
            args = (args,)

        with pytest.raises(SystemExit):
            exception_exit(exception(*args), to_stderr=to_stderr, red=red)

        captured = capsys.readouterr()

        if to_stderr:
            assert message in captured.err

            if red:
                assert Fore.LIGHTRED_EX in captured.err
                assert Fore.RESET in captured.err
            else:
                assert Fore.LIGHTRED_EX not in captured.err
                assert Fore.RESET not in captured.err
        else:
            assert message in captured.out

            if red:
                assert Fore.LIGHTRED_EX in captured.out
                assert Fore.RESET in captured.out
            else:
                assert Fore.LIGHTRED_EX not in captured.out
                assert Fore.RESET not in captured.out

    def test_error(self):
        with pytest.raises(
            TypeError, match="exception should be a subclass of Exception"
        ):
            exception_exit("hi")


class TestPrinter:
    @pytest.fixture(scope="function", autouse=True)
    def autoreset_printer(self):
        Printer.reset()
        yield
        Printer.reset()

    def test_reset(self):
        assert Printer._print == print
        Printer._print = 0.25
        assert Printer._print == 0.25

        Printer.reset()
        assert Printer._print == print

    def test_silence(self, capsys):
        assert Printer._print == print
        Printer.silence()
        assert Printer._print == Printer.useless
        Printer.print("hola")

        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    def test_print(self, capsys):
        assert Printer._print == print
        Printer.print("hello")

        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == "hello\n"

    def test_useless(self, capsys):
        Printer.useless("a", 1, float=0.23, complex=1 + 2j)

        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""


class TestCheckUpdates:
    version_data = (
        ("3.0.1", "3.0.2", True),
        ("3.0.0", "3.0.1", True),
        ("2.1.1", "3.0.0", True),
        ("2.1.0", "2.1.1", True),
        ("2.0.1", "2.1.0", True),
    )

    version_data = version_data + tuple([[x[1], x[0], False] for x in version_data])

    @pytest.fixture
    def mocks(self):
        con_mock = mock.patch("vcm.core.networking.connection").start()
        print_mock = mock.patch("vcm.core.utils.Printer.print").start()

        yield con_mock, print_mock

        mock.patch.stopall()

    @pytest.mark.parametrize("version1, version2, new_update", version_data)
    def test_check_updates(self, mocks, version1, version2, new_update):
        con_mock, print_mock = mocks

        response_mock = mock.MagicMock()
        response_mock.text = version2
        con_mock.get.return_value = response_mock

        vcm.version = version1

        result = check_updates()

        assert result == new_update
        print_mock.assert_called_once()


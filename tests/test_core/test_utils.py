from unittest import mock

import pytest
from colorama.ansi import Fore

import vcm
from vcm.core.utils import (
    MetaSingleton,
    Patterns,
    Printer,
    check_updates,
    exception_exit,
    secure_filename,
    setup_vcm,
)


class TestSecureFilename:
    test_data_no_spaces = [
        ("file name.txt", "file_name.txt"),
        ("file/other.pdf", "file_other.pdf"),
        ("file name_v2.pdf", "file_name_v2.pdf"),
        ("My cool movie.mov", "My_cool_movie.mov"),
        ("../../../etc/passwd", "etc_passwd"),
        (u"i contain cool \xfcml\xe4uts.txt", "i_contain_cool_umlauts.txt"),
    ]
    test_data_spaces = [
        ("file name.txt", "file name.txt"),
        ("file/other.pdf", "file other.pdf"),
        ("enigma_v3.zip", "enigma v3.zip"),
        ("My cool movie.mov", "My cool movie.mov"),
        ("../../../etc/passwd", "etc passwd"),
        (u"i contain cool \xfcml\xe4uts.txt", "i contain cool umlauts.txt"),
    ]

    @pytest.mark.parametrize("input_str, expected", test_data_no_spaces)
    def test_no_spaces(self, input_str, expected):
        real = secure_filename(input_str, spaces=False)
        assert real == expected

    @pytest.mark.parametrize("input_str, expected", test_data_spaces)
    def test_spaces(self, input_str, expected):
        real = secure_filename(input_str, spaces=True)
        assert real == expected


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

    def test_error_1(self):
        match = "exception should be a subclass of Exception"
        with pytest.raises(TypeError, match=match):
            exception_exit("hi")

    def test_error_2(self):
        class Dummy:
            pass

        match = "exception should be a subclass of Exception"
        with pytest.raises(TypeError, match=match):
            exception_exit(Dummy)


@mock.patch("vcm.core.utils.configure_logging")
@mock.patch("vcm.core.utils.more_settings_check")
def test_setup_vcm(msc_mock, cl_mock):
    setup_vcm()
    msc_mock.assert_called_once_with()
    cl_mock.assert_called_once_with()


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


class TestMetaSingleton:
    def test_one_class(self):
        class Class(metaclass=MetaSingleton):
            def __init__(self, value):
                self.value = value

        instance_1 = Class(1)
        instance_2 = Class(2)

        assert instance_1.value == 1
        assert instance_2.value == 1
        assert instance_1 is instance_2

    def test_multiple_classes(self):
        class Class1(metaclass=MetaSingleton):
            def __init__(self, value):
                self.value = value

        class Class2(metaclass=MetaSingleton):
            def __init__(self, value):
                self.value = value

        class Class3(metaclass=MetaSingleton):
            def __init__(self, value):
                self.value = value

        instance_11 = Class1(11)
        instance_12 = Class1(12)
        instance_13 = Class1(13)

        instance_21 = Class2(21)
        instance_22 = Class2(22)
        instance_23 = Class2(23)

        instance_31 = Class3(31)
        instance_32 = Class3(32)
        instance_33 = Class3(33)

        assert instance_11.value == instance_12.value == instance_13.value == 11
        assert instance_21.value == instance_22.value == instance_23.value == 21
        assert instance_31.value == instance_32.value == instance_33.value == 31

        assert instance_11 is instance_12 is instance_13
        assert instance_21 is instance_22 is instance_23
        assert instance_31 is instance_32 is instance_33

        assert instance_11.value != instance_21.value != instance_31.value
        assert instance_12.value != instance_22.value != instance_32.value
        assert instance_13.value != instance_23.value != instance_33.value

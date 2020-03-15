import logging
import os
from unittest import mock

import pytest
from colorama.ansi import Fore

import vcm
from vcm.core.utils import (
    MetaSingleton,
    Patterns,
    Printer,
    check_updates,
    configure_logging,
    exception_exit,
    more_settings_check,
    secure_filename,
    setup_vcm,
    str2bool,
    timing,
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


class TestTiming:
    @pytest.fixture
    def mocks(self):
        time_m = mock.patch("vcm.core.utils.time").start()
        sts_m = mock.patch("vcm.core.utils.seconds_to_str").start()

        yield time_m, sts_m

        mock.patch.stopall()

    @pytest.mark.parametrize("name", ["hello", None])
    @pytest.mark.parametrize("level", [10, 20, 30, 40, 50, None])
    def test_ok(self, mocks, caplog, name, level):
        @timing(name=name, level=level)
        def custom_function():
            pass

        time_m, sts_m = mocks
        time_m.side_effect = [0, 30]
        sts_m.return_value = "30 seconds"

        logging.getLogger("vcm.core.utils").setLevel(10)
        caplog.at_level(10, logger="vcm.core.utils")
        custom_function()

        log_name = name or "custom_function"
        log_level = level or 20
        log_str = "%s executed in %s" % (log_name, sts_m.return_value)

        assert caplog.record_tuples == [("vcm.core.utils", log_level, log_str)]

    @pytest.mark.parametrize("exception", [ValueError, SystemExit, TypeError])
    @pytest.mark.parametrize("name", ["hello", None])
    @pytest.mark.parametrize("level", [10, 20, 30, 40, 50, None])
    def test_exception(self, mocks, caplog, name, level, exception):
        @timing(name=name, level=level)
        def custom_function():
            raise exception

        time_m, sts_m = mocks
        time_m.side_effect = [0, 30]
        sts_m.return_value = "30 seconds"

        logging.getLogger("vcm.core.utils").setLevel(10)
        caplog.at_level(10, logger="vcm.core.utils")
        with pytest.raises(exception):
            custom_function()

        log_name = name or "custom_function"
        log_level = level or 20
        log_str = "%s executed in %s" % (log_name, sts_m.return_value)

        assert caplog.record_tuples == [("vcm.core.utils", log_level, log_str)]


class TestStrToBool:
    test_data = [
        (True, True),
        (False, False),
        ("true", True),
        ("True", True),
        ("false", False),
        ("False", False),
        ("no", False),
        ("n", False),
        ("No", False),
        ("N", False),
        ("yes", True),
        ("y", True),
        ("Yes", True),
        ("Y", True),
        ("t", True),
        ("T", True),
        ("f", False),
        ("F", False),
        ("1", True),
        ("0", False),
        ("Sí", True),
        ("Si", True),
        ("si", True),
        ("S", True),
        ("s", True),
        ("invalid", None),
    ]

    @pytest.mark.parametrize("input_str, expected", test_data)
    def test_str2bool(self, input_str, expected):
        if expected is not None:
            real = str2bool(input_str)
            assert real == expected
        else:
            with pytest.raises(ValueError, match="Invalid bool string"):
                str2bool(input_str)


class TestConfigureLogging:
    @pytest.fixture
    def mocks(self):
        gs_m = mock.patch("vcm.core.settings.GeneralSettings").start()
        lpe_m = gs_m.log_path.exists
        ct_m = mock.patch("vcm.core.utils.current_thread").start()
        rfh_m = mock.patch("vcm.core.utils.RotatingFileHandler").start()
        lbc_m = mock.patch("logging.basicConfig").start()
        lgl_m = mock.patch("logging.getLogger").start()

        yield gs_m, lpe_m, ct_m, rfh_m, lbc_m, lgl_m

        mock.patch.stopall()

    @pytest.mark.parametrize("do_roll", [True, False])
    def test_testing_none(self, mocks, do_roll):
        if os.environ.get("TESTING"):
            del os.environ["TESTING"]
        gs_m, lpe_m, ct_m, rfh_m, lbc_m, lgl_m = mocks
        lpe_m.return_value = do_roll

        fmt = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
        configure_logging()

        rfh_m.assert_called_once_with(
            filename=gs_m.log_path,
            maxBytes=2500000,
            encoding="utf-8",
            backupCount=gs_m.max_logs,
        )
        handler = rfh_m.return_value

        ct_m.return_value.setName.assert_called_with("MT")

        if do_roll:
            handler.doRollover.assert_called_once()
        else:
            handler.doRollover.assert_not_called()

        lbc_m.assert_called_once_with(
            handlers=[handler], level=gs_m.logging_level, format=fmt
        )
        lgl_m.assert_called_with("urllib3")
        lgl_m.return_value.setLevel.assert_called_once_with(40)

    @pytest.mark.parametrize("do_roll", [True, False])
    def test_testing_true(self, mocks, do_roll):
        os.environ["TESTING"] = "True"
        _, lpe_m, ct_m, rfh_m, lbc_m, lgl_m = mocks
        lpe_m.return_value = do_roll

        configure_logging()

        rfh_m.assert_not_called()
        handler = rfh_m.return_value

        ct_m.return_value.setName.assert_not_called()

        handler.doRollover.assert_not_called()

        lbc_m.assert_not_called()
        lgl_m.assert_called_with("urllib3")
        lgl_m.return_value.setLevel.assert_called_once_with(40)


class TestMoreSettingsCheck:
    @classmethod
    def setup_class(cls):
        cls.default_root_folder = "<default-root-folder>"
        cls.no_default_root_folder = "<no-default-root-folder>"

        cls.default_email = "<default-email>"
        cls.no_default_email = "<no-default-email>"

        cls.defaults = {
            "general": {"root-folder": cls.default_root_folder},
            "notify": {"email": cls.default_email},
        }

    @pytest.fixture(scope="function", autouse=True)
    def ensure_default_environ(self):
        assert not os.environ.get("VCM_DISABLE_CONSTRUCTS")
        yield
        assert not os.environ.get("VCM_DISABLE_CONSTRUCTS")

    @pytest.fixture
    def mocks(self):
        gs_mock = mock.patch("vcm.core.settings.GeneralSettings").start()
        ns_mock = mock.patch("vcm.core.settings.NotifySettings").start()
        mock.patch("vcm.core._settings.defaults", self.defaults).start()
        mkdirs_mock = mock.patch("os.makedirs").start()

        gs_mock.root_folder = self.no_default_root_folder
        ns_mock.email = self.no_default_email

        yield gs_mock, ns_mock, mkdirs_mock
        mock.patch.stopall()

    def test_ok(self, mocks):
        gs_mock, _, mkdirs_mock = mocks
        more_settings_check()

        mkdirs_mock.assert_any_call(self.no_default_root_folder, exist_ok=True)
        mkdirs_mock.assert_any_call(gs_mock.logs_folder, exist_ok=True)
        assert mkdirs_mock.call_count == 2

    def test_default_root_folder(self, mocks):
        gs_mock, _, mkdirs_mock = mocks
        gs_mock.root_folder = self.default_root_folder

        with pytest.raises(Exception, match="Must set 'general.root-folder'"):
            more_settings_check()

        mkdirs_mock.assert_not_called()

    def test_default_email(self, mocks):
        _, ns_mock, mkdirs_mock = mocks
        ns_mock.email = self.default_email

        with pytest.raises(Exception, match="Must set 'notify.email'"):
            more_settings_check()

        mkdirs_mock.assert_not_called()
        mkdirs_mock.assert_not_called()

    def test_default_root_folder_and_email(self, mocks):
        gs_mock, ns_mock, mkdirs_mock = mocks
        gs_mock.root_folder = self.default_root_folder
        ns_mock.email = self.default_email

        with pytest.raises(Exception, match="Must set 'general.root-folder'"):
            more_settings_check()

        mkdirs_mock.assert_not_called()


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

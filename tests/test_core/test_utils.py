from collections import defaultdict
import logging
import os
from copy import Error, deepcopy
from unittest import mock
from requests.exceptions import ConnectionError, ProxyError
import pytest
from colorama.ansi import Fore

import vcm
from vcm.core.utils import (
    ErrorCounter,
    Key,
    MetaSingleton,
    Patterns,
    Printer,
    check_updates,
    configure_logging,
    exception_exit,
    handle_fatal_error_exit,
    more_settings_check,
    safe_exit,
    save_crash_context,
    secure_filename,
    setup_vcm,
    str2bool,
    timing,
)


class TestKey:
    def test_attributes(self):
        assert Key(b"a", b"a").is_int is False
        assert Key(b"a").is_int is False
        assert Key(25).is_int is True
        assert Key(15, 15).is_int is True

        with pytest.raises(TypeError, match="key1 must be bytes or int"):
            Key(None)

        with pytest.raises(TypeError, match="key1 must be bytes or int"):
            Key(1 + 2j)

        with pytest.raises(TypeError, match="key2 must be bytes or int"):
            Key(1, 1 + 5j)

        with pytest.raises(ValueError, match="key1 must have only one byte"):
            Key(b"11")

        with pytest.raises(ValueError, match="key2 must have only one byte"):
            Key(b"1", b"11")

        with pytest.raises(TypeError, match="key1 and key2 must be of the same type"):
            Key(b"1", 5)

    def test_string(self):
        assert str(Key(b"r")) == "Key(key1=b'r', key2=None)"
        assert str(Key(b"a", b"b")) == "Key(key1=b'a', key2=b'b')"
        assert str(Key(22)) == "Key(key1=22, key2=None)"
        assert str(Key(23, 26)) == "Key(key1=23, key2=26)"

    def test_repr(self):
        key = Key(12, 21)
        assert repr(key) == str(key)

    def test_eq(self):
        kn1 = Key(1, 2)
        kn2 = Key(1, 2)
        kb1 = Key(b"1", b"2")
        kb2 = Key(b"1", b"2")

        assert kn1 != kb1
        assert kn2 != kb2

        assert kn1 == kn2
        assert kb1 == kb2

    def test_to_int(self):
        with pytest.raises(ValueError, match="Key is already in int mode"):
            Key(1, 1).to_int()

        assert Key(b"\x01", b"\x01").to_int() == Key(1, 1)
        assert Key(b"\x31", b"\x31").to_int() == Key(49, 49)
        assert Key(b"1", b"1").to_int() == Key(49, 49)

    def test_to_char(self):
        with pytest.raises(ValueError, match="Key is already in char mode"):
            Key(b"\x01", b"\x01").to_char()

        assert Key(1, 1).to_char() == Key(b"\x01", b"\x01")
        assert Key(49, 49).to_char() == Key(b"\x31", b"\x31")
        assert Key(49, 49).to_char() == Key(b"1", b"1")


class TestSecureFilename:
    test_data_no_spaces = [
        ("file name.txt", "file_name.txt"),
        ("file/other.pdf", "file_other.pdf"),
        ("file name_v2.pdf", "file_name_v2.pdf"),
        ("My cool movie.mov", "My_cool_movie.mov"),
        ("../../../etc/passwd", "etc_passwd"),
        ("i contain cool \xfcml\xe4uts.txt", "i_contain_cool_umlauts.txt"),
    ]
    test_data_spaces = [
        ("file name.txt", "file name.txt"),
        ("file/other.pdf", "file other.pdf"),
        ("enigma_v3.zip", "enigma v3.zip"),
        ("My cool movie.mov", "My cool movie.mov"),
        ("../../../etc/passwd", "etc passwd"),
        ("i contain cool \xfcml\xe4uts.txt", "i contain cool umlauts.txt"),
    ]

    @pytest.mark.parametrize("input_str, expected", test_data_no_spaces)
    def test_no_spaces(self, input_str, expected):
        real = secure_filename(input_str, spaces=False)
        assert real == expected

    @pytest.mark.parametrize("input_str, expected", test_data_spaces)
    def test_spaces(self, input_str, expected):
        real = secure_filename(input_str, spaces=True)
        assert real == expected

    def test_windows_special_names(self):
        assert secure_filename("aux", spaces=True) == "_aux"
        assert secure_filename("aux", spaces=False) == "_aux"

        assert secure_filename("con", spaces=True) == "_con"
        assert secure_filename("con", spaces=False) == "_con"

        assert secure_filename("com2", spaces=True) == "_com2"
        assert secure_filename("com2", spaces=False) == "_com2"


class TestPatterns:
    filename_data = (
        ('filename="a.txt"', "a.txt"),
        ('filename="cool.html"', "cool.html"),
        ('filename="hello-there-93.jpg"', "hello-there-93.jpg"),
        ('filename="consider spacing true.txt"', "consider spacing true.txt"),
        ('filename="IS_BI_2_20.xlsx"', "IS_BI_2_20.xlsx"),
        ('filename="important (2020_2021).pdf"', "important (2020_2021).pdf"),
        ('filename="accents [áéíóúñÁÉÍÓÚÑ]()"', "accents [áéíóúñÁÉÍÓÚÑ]()"),
        ('filename="-.,_;+`^´¨{[]\'¡¿!@#·$%&€"', "-.,_;+`^´¨{[]'¡¿!@#·$%&€"),
        ('filename="~+*?!|"', None),
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
        (ValueError, "Invalid path", True),
        (TypeError, ("Invalid type", "Expected int"), True),
        (ImportError, "Module not found: math", True),
        (SystemExit, "exit program", False),
    )

    @pytest.mark.parametrize("red", [True, False])
    @pytest.mark.parametrize("to_stderr", [True, False])
    @pytest.mark.parametrize("exception, args, should_exit", exceptions)
    def test_ok(self, exception, args, should_exit, to_stderr, red, capsys):
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


class TestSafeExit:
    @pytest.fixture(params=[True, False])
    def to_stderr(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def red(self, request):
        return request.param

    @pytest.fixture(params=[ValueError, TypeError, AttributeError, SystemExit])
    def exception(self, request):
        return request.param

    @mock.patch("vcm.core.utils.exception_exit")
    def test_safe_exit(self, ee_m, red, to_stderr, exception):
        exc = exception()
        is_system_exit = isinstance(exc, SystemExit)

        @safe_exit(to_stderr=to_stderr, red=red)
        def custom_function():
            raise exc

        if is_system_exit:
            with pytest.raises(SystemExit):
                custom_function()
        else:
            custom_function()

            ee_m.assert_called_with(exc, to_stderr=to_stderr, red=red)


class TestTiming:
    @pytest.fixture
    def mocks(self):
        time_m = mock.patch("vcm.core.utils.time").start()
        sts_m = mock.patch("vcm.core.utils.seconds_to_str").start()
        err_counter_m = mock.patch("vcm.core.utils.ErrorCounter").start()

        yield time_m, sts_m, err_counter_m

        mock.patch.stopall()

    @pytest.fixture(params=["hello", None])
    def name(self, request):
        yield request.param

    @pytest.fixture(params=[10, 20, 30, 40, 50, None])
    def level(self, request):
        return request.param

    @pytest.fixture(params=[False, True])
    def errors(self, request):
        return request.param

    def test_ok(self, mocks, caplog, name, level, errors):
        @timing(name=name, level=level)
        def custom_function(arg1="arg1"):
            return arg1

        time_m, sts_m, err_counter_m = mocks
        time_m.side_effect = [0, 30]
        sts_m.return_value = "30 seconds"

        err_counter_m.report.return_value = "<error-report>"
        if errors:
            err_counter_m.has_errors.return_value = True
        else:
            err_counter_m.has_errors.return_value = False

        logging.getLogger("vcm.core.utils").setLevel(10)
        caplog.at_level(10, logger="vcm.core.utils")
        custom_function(arg1=25)

        log_name = name or "custom_function"
        log_level = level or 20
        log_str = "%s executed in %s" % (log_name, sts_m.return_value)

        expected_log_tuples = [
            ("vcm.core.utils", log_level, f"Starting execution of {log_name}"),
            ("vcm.core.utils", 30, "<error-report>"),
            ("vcm.core.utils", log_level, log_str),
        ]

        if not errors:
            expected_log_tuples.pop(1)

        assert caplog.record_tuples == expected_log_tuples

    @pytest.fixture(params=[ValueError, SystemExit, TypeError])
    def exception(self, request):
        return request.param

    def test_exception(self, mocks, caplog, name, level, exception, errors):
        @timing(name=name, level=level)
        def custom_function(arg1="arg1"):
            raise exception(arg1)

        time_m, sts_m, err_counter_m = mocks
        time_m.side_effect = [0, 30]
        sts_m.return_value = "30 seconds"

        err_counter_m.report.return_value = "<error-report>"
        if errors:
            err_counter_m.has_errors.return_value = True
        else:
            err_counter_m.has_errors.return_value = False

        logging.getLogger("vcm.core.utils").setLevel(10)
        caplog.at_level(10, logger="vcm.core.utils")
        with pytest.raises(exception):
            custom_function(arg1=25)

        log_name = name or "custom_function"
        log_level = level or 20
        log_str = "%s executed in %s" % (log_name, sts_m.return_value)

        expected_log_tuples = [
            ("vcm.core.utils", log_level, f"Starting execution of {log_name}"),
            ("vcm.core.utils", 30, "<error-report>"),
            ("vcm.core.utils", log_level, log_str),
        ]

        if not errors:
            expected_log_tuples.pop(1)

        assert caplog.record_tuples == expected_log_tuples


class TestStr2Bool:
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
    def test_str2bool_ok(self, input_str, expected):
        if expected is not None:
            real = str2bool(input_str)
            assert real == expected
        else:
            with pytest.raises(ValueError, match="Invalid bool string"):
                str2bool(input_str)

    def test_type_error(self):
        with pytest.raises(TypeError, match="Invalid value type: 'int'"):
            str2bool(4)
        with pytest.raises(TypeError, match="Invalid value type: 'complex'"):
            str2bool(4 + 2j)
        with pytest.raises(TypeError, match="Invalid value type: 'float'"):
            str2bool(4.5)
        with pytest.raises(TypeError, match="Invalid value type: 'list'"):
            str2bool([])


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
        # assert not os.environ.get("VCM_DISABLE_CONSTRUCTS")
        yield
        # assert not os.environ.get("VCM_DISABLE_CONSTRUCTS")

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

        vcm.__version__ = version1

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


class TestErrorCounter:
    @pytest.fixture(scope="function", autouse=True)
    def reset_error_map(self):
        error_map = deepcopy(ErrorCounter.error_map)
        yield
        ErrorCounter.error_map = error_map

    def test_has_errors(self):
        assert not ErrorCounter.has_errors()
        ErrorCounter.error_map["a"] += 1
        assert ErrorCounter.has_errors()
        ErrorCounter.error_map["b"] += 1
        assert ErrorCounter.has_errors()

    def test_record_error(self):
        error_map = ErrorCounter.error_map

        def compute_length() -> int:
            return sum(error_map.values())

        assert compute_length() == 0
        ErrorCounter.record_error(ArithmeticError())
        assert compute_length() == 1
        assert error_map[ArithmeticError] == 1
        assert error_map[TypeError] == 0
        assert error_map[ProxyError] == 0

        ErrorCounter.record_error(TypeError())
        assert compute_length() == 2
        assert error_map[ArithmeticError] == 1
        assert error_map[TypeError] == 1
        assert error_map[ProxyError] == 0

        ErrorCounter.record_error(ArithmeticError())
        assert compute_length() == 3
        assert error_map[ArithmeticError] == 2
        assert error_map[TypeError] == 1
        assert error_map[ProxyError] == 0

        ErrorCounter.record_error(TypeError())
        assert compute_length() == 4
        assert error_map[ArithmeticError] == 2
        assert error_map[TypeError] == 2
        assert error_map[ProxyError] == 0

        ErrorCounter.record_error(ProxyError())
        assert compute_length() == 5
        assert error_map[ArithmeticError] == 2
        assert error_map[TypeError] == 2
        assert error_map[ProxyError] == 1

        ErrorCounter.record_error(ArithmeticError())
        assert compute_length() == 6
        assert error_map[ArithmeticError] == 3
        assert error_map[TypeError] == 2
        assert error_map[ProxyError] == 1

    def test_report(self):
        dict1 = {TypeError: 2, ProxyError: 3, ValueError: 1}
        ErrorCounter.error_map = defaultdict(lambda: 0, dict1)
        expected = "6 errors found (ProxyError: 3, TypeError: 2, ValueError: 1)"
        assert ErrorCounter.report() == expected

        dict2 = {ZeroDivisionError: 0, TypeError: 2, ProxyError: 3, ValueError: 5}
        ErrorCounter.error_map = defaultdict(lambda: 0, dict2)
        expected = "10 errors found (ValueError: 5, ProxyError: 3, TypeError: 2)"
        assert ErrorCounter.report() == expected


class TestSaveCrashContent:
    @pytest.fixture
    def mocks(self):
        gs_m = mock.patch("vcm.core.settings.GeneralSettings").start()
        dt_m = mock.patch("vcm.core.utils.datetime").start()
        dt_m.now.return_value.strftime.return_value = "<current datetime>"
        pkl_m = mock.patch("pickle.dumps").start()
        dcpy_m = mock.patch("vcm.core.utils.deepcopy").start()
        dcpy_m.side_effect = lambda x: x

        yield gs_m, dt_m, pkl_m, dcpy_m

        mock.patch.stopall()

    @pytest.fixture(params=range(6))
    def exists(self, request):
        yield request.param

    @pytest.fixture(params=["class-instance", "normal-string"])
    def crash_object(self, request):
        if request.param != "class-instance":
            yield request.param
        else:
            from dataclasses import dataclass

            @dataclass
            class B:
                a = 25

            yield B()

    @pytest.fixture(params=[None, "<reason>"])
    def reason(self, request):
        return request.param

    def test_save_crash_context(self, mocks, exists, crash_object, reason):
        gs_m, dt_m, pkl_m, dcpy_m = mocks
        crash_path = gs_m.root_folder.joinpath.return_value
        crash_path.exists.return_value = bool(exists)
        new_path = crash_path.with_name.return_value
        new_path.exists.side_effect = [True] * (exists - 1) + [False]

        save_crash_context(crash_object, "<object_name>", reason=reason)

        if exists:
            crash_path.with_name.assert_called()
            assert crash_path.with_name.call_count == exists
        else:
            crash_path.with_name.assert_not_called()

        crash_name = "<object_name>.<current datetime>.pkl"
        gs_m.root_folder.joinpath.assert_called_with(crash_name)
        dt_m.now.assert_called_once_with()
        dt_m.now.return_value.strftime.assert_called_with("%Y.%m.%d-%H.%M.%S")

        crash_object_saved = pkl_m.call_args[0][0]
        if reason:
            if not isinstance(crash_object, str):
                crash_object.vcm_reason = "<reason>"
                assert crash_object_saved == crash_object
                dcpy_m.assert_called_once_with(crash_object)
            else:
                assert crash_object_saved == {
                    "real_object": crash_object,
                    "vcm_crash_reason": reason,
                }
                assert crash_object_saved["real_object"] == crash_object
                dcpy_m.assert_called_once_with(crash_object)
        else:
            assert crash_object_saved == crash_object
            dcpy_m.assert_called_once_with(crash_object)

        if not exists:
            crash_path.write_bytes.assert_called_once_with(pkl_m.return_value)
        else:
            new_path.write_bytes.assert_called_once_with(pkl_m.return_value)


@pytest.mark.parametrize("message", ("error", "real error", 4532))
@pytest.mark.parametrize("exit_code", range(-3, 4))
def test_handle_fatal_error_exit(capsys, message, exit_code):
    real_message = Fore.RED + str(message) + Fore.RESET
    with pytest.raises(SystemExit, match=str(exit_code)):
        handle_fatal_error_exit(message, exit_code=exit_code)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == real_message

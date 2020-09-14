from collections import defaultdict
from copy import deepcopy
import logging
import os
from unittest import mock

import pytest
from requests.exceptions import ConnectionError, ProxyError

import vcm
from vcm.core.exceptions import FilenameWarning
from vcm.core.utils import (
    ErrorCounter,
    MetaSingleton,
    Patterns,
    Printer,
    check_updates,
    configure_logging,
    handle_fatal_error_exit,
    open_http_status_server,
    save_crash_context,
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

    @mock.patch("os.name", "nt")
    def test_windows_special_names(self):
        with pytest.warns(FilenameWarning, match="Couldn't allow spaces"):
            assert secure_filename("aux", spaces=True) == "_aux"
        assert secure_filename("aux", spaces=False) == "_aux"

        with pytest.warns(FilenameWarning, match="Couldn't allow spaces"):
            assert secure_filename("con", spaces=True) == "_con"
        assert secure_filename("con", spaces=False) == "_con"

        with pytest.warns(FilenameWarning, match="Couldn't allow spaces"):
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
    def test_filename(self, input_str, expected):
        match = Patterns.FILENAME.search(input_str)

        if expected:
            assert match.group(1) == expected
        else:
            assert match is None

    email_data = (
        ("asdf@adsf.asdf", True),
        ("adsf++-dsafads-fsaf@adsfsdalkfj.clkdsjflksjdf", True),
        (".@gmail.com", False),
        ("kidding", False),
    )

    @pytest.mark.parametrize("input_str, expected", email_data)
    def test_email(self, input_str, expected):
        match = Patterns.EMAIL.search(input_str)

        if expected:
            assert match.group(0) == input_str
        else:
            assert match is None


class TestTiming:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.time_m = mock.patch("vcm.core.utils.time").start()
        self.sts_m = mock.patch("vcm.core.utils.seconds_to_str").start()
        self.err_counter_m = mock.patch("vcm.core.utils.ErrorCounter").start()

        yield

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

    def test_ok(self, caplog, name, level, errors):
        @timing(name=name, level=level)
        def custom_function(arg1="arg1"):
            return arg1

        self.time_m.side_effect = [0, 30]
        self.sts_m.return_value = "30 seconds"

        self.err_counter_m.report.return_value = "<error-report>"
        if errors:
            self.err_counter_m.has_errors.return_value = True
        else:
            self.err_counter_m.has_errors.return_value = False

        logging.getLogger("vcm.core.utils").setLevel(10)
        caplog.at_level(10, logger="vcm.core.utils")
        custom_function(arg1=25)

        log_name = name or "custom_function"
        log_level = level or 20
        log_str = "%r executed in %s [%s]" % (log_name, self.sts_m.return_value, 25)

        expected_log_tuples = [
            ("vcm.core.utils", log_level, f"Starting execution of {log_name!r}"),
            ("vcm.core.utils", 30, "<error-report>"),
            ("vcm.core.utils", log_level, log_str),
        ]

        if not errors:
            expected_log_tuples.pop(1)

        assert caplog.record_tuples == expected_log_tuples

    @pytest.fixture(params=[ValueError, SystemExit, TypeError])
    def exception(self, request):
        return request.param

    def test_exception(self, caplog, name, level, exception, errors):
        @timing(name=name, level=level)
        def custom_function(arg1="arg1"):
            raise exception(arg1)

        self.time_m.side_effect = [0, 30]
        self.sts_m.return_value = "30 seconds"

        self.err_counter_m.report.return_value = "<error-report>"
        if errors:
            self.err_counter_m.has_errors.return_value = True
        else:
            self.err_counter_m.has_errors.return_value = False

        logging.getLogger("vcm.core.utils").setLevel(10)
        caplog.at_level(10, logger="vcm.core.utils")
        with pytest.raises(exception):
            custom_function(arg1=25)

        log_name = name or "custom_function"
        log_level = level or 20
        log_str = "%r executed in %s [%s]" % (log_name, self.sts_m.return_value, None)

        expected_log_tuples = [
            ("vcm.core.utils", log_level, f"Starting execution of {log_name!r}"),
            ("vcm.core.utils", 30, "<error-report>"),
            ("vcm.core.utils", log_level, log_str),
        ]

        if not errors:
            expected_log_tuples.pop(1)

        assert caplog.record_tuples == expected_log_tuples

    def test_decorate_not_called(self, name, level):
        # Defaults: name=None, level=None
        @timing
        def custom_function():
            """Dummy function."""

        custom_function()

    def test_decorate_called_mixed_args(self, name, level):
        msg = "Use keyword arguments in the timing decorator"
        with pytest.raises(ValueError, match=msg):

            @timing(name, level=level)
            def custom_function():
                """Dummy function."""

        with pytest.raises(UnboundLocalError):
            custom_function()


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
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.settings_m = mock.patch("vcm.settings.settings").start()
        self.lpe_m = self.settings_m.log_path.exists
        self.ct_m = mock.patch("vcm.core.utils.current_thread").start()
        self.rfh_m = mock.patch("vcm.core.utils.RotatingFileHandler").start()
        self.lbc_m = mock.patch("logging.basicConfig").start()
        self.lgl_m = mock.patch("logging.getLogger").start()

        yield

        mock.patch.stopall()

    @pytest.mark.parametrize("do_roll", [True, False])
    def test_testing_none(self, do_roll):
        if os.environ.get("TESTING"):
            del os.environ["TESTING"]

        self.lpe_m.return_value = do_roll

        fmt = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
        configure_logging()

        self.rfh_m.assert_called_once_with(
            filename=self.settings_m.log_path,
            maxBytes=2500000,
            encoding="utf-8",
            backupCount=self.settings_m.max_logs,
        )
        handler = self.rfh_m.return_value

        self.ct_m.return_value.setName.assert_called_with("MT")

        if do_roll:
            handler.doRollover.assert_called_once()
        else:
            handler.doRollover.assert_not_called()

        self.lbc_m.assert_called_once_with(
            handlers=[handler], level=self.settings_m.logging_level, format=fmt
        )
        self.lgl_m.assert_called_with("urllib3")
        self.lgl_m.return_value.setLevel.assert_called_once_with(40)

    @pytest.mark.parametrize("do_roll", [True, False])
    def test_testing_true(self, do_roll):
        os.environ["TESTING"] = "True"
        self.lpe_m.return_value = do_roll

        configure_logging()

        self.rfh_m.assert_not_called()
        handler = self.rfh_m.return_value

        self.ct_m.return_value.setName.assert_not_called()

        handler.doRollover.assert_not_called()

        self.lbc_m.assert_not_called()
        self.lgl_m.assert_called_with("urllib3")
        self.lgl_m.return_value.setLevel.assert_called_once_with(40)


@mock.patch("vcm.settings.CheckSettings.check")
@mock.patch("vcm.core.utils.configure_logging")
def test_setup_vcm(cl_mock, check_settings_m):
    setup_vcm()
    cl_mock.assert_called_once_with()
    check_settings_m.assert_called_once_with()


class TestPrinter:
    @pytest.fixture(scope="function", autouse=True)
    def autoreset_printer(self):
        Printer.reset()
        yield
        Printer.reset()

    def test_reset(self):
        assert Printer.can_print == True
        Printer.can_print = 0.25
        assert Printer.can_print == 0.25

        Printer.reset()
        assert Printer.can_print == True

    def test_silence(self, capsys):
        assert Printer.can_print == True
        Printer.silence()
        assert Printer.can_print == False
        Printer.print("hola")

        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    @pytest.mark.parametrize("should_print", [False, True])
    @mock.patch("vcm.core.utils.Modules.should_print")
    def test_print(self, sp_m, should_print, capsys):
        sp_m.return_value = should_print
        assert Printer.can_print == True
        Printer.print("hello")

        captured = capsys.readouterr()
        assert captured.err == ""
        if should_print:
            assert captured.out == "hello\n"
        else:
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

    @pytest.fixture(autouse=True)
    def mocks(self):
        self.con_m = mock.patch("vcm.core.networking.connection").start()
        self.print_m = mock.patch("vcm.core.utils.Printer.print").start()

        yield

        mock.patch.stopall()

    @pytest.mark.parametrize("version1, version2, new_update", version_data)
    def test_check_updates(self, version1, version2, new_update):
        response_mock = mock.MagicMock()
        response_mock.json.return_value = [
            {"name": version2},
        ]
        self.con_m.get.return_value = response_mock

        vcm.__version__ = version1

        result = check_updates()

        assert result == new_update
        self.print_m.assert_called_once()

        if new_update:
            assert "Newer version available" in self.print_m.call_args[0][0]
        else:
            assert "No updates available" in self.print_m.call_args[0][0]


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
        ErrorCounter.error_map = defaultdict(int, dict1)
        expected = "6 errors found (ProxyError: 3, TypeError: 2, ValueError: 1)"
        assert ErrorCounter.report() == expected

        dict2 = {ZeroDivisionError: 0, TypeError: 2, ProxyError: 3, ValueError: 5}
        ErrorCounter.error_map = defaultdict(int, dict2)
        expected = "10 errors found (ValueError: 5, ProxyError: 3, TypeError: 2)"
        assert ErrorCounter.report() == expected


class TestSaveCrashContent:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.settings_m = mock.patch("vcm.settings.settings").start()
        self.dt_m = mock.patch("vcm.core.utils.datetime").start()
        self.dt_m.now.return_value.strftime.return_value = "<current datetime>"
        self.pkl_m = mock.patch("pickle.dumps").start()
        self.dcpy_m = mock.patch("vcm.core.utils.deepcopy").start()
        self.dcpy_m.side_effect = lambda x: x

        yield

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

    def test_save_crash_context(self, exists, crash_object, reason):
        crash_path = self.settings_m.root_folder.joinpath.return_value
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
        self.settings_m.root_folder.joinpath.assert_called_with(crash_name)
        self.dt_m.now.assert_called_once_with()
        self.dt_m.now.return_value.strftime.assert_called_with("%Y.%m.%d-%H.%M.%S")

        crash_object_saved = self.pkl_m.call_args[0][0]
        if reason:
            if not isinstance(crash_object, str):
                crash_object.vcm_reason = "<reason>"
                assert crash_object_saved == crash_object
                self.dcpy_m.assert_called_once_with(crash_object)
            else:
                assert crash_object_saved == {
                    "real_object": crash_object,
                    "vcm_crash_reason": reason,
                }
                assert crash_object_saved["real_object"] == crash_object
                self.dcpy_m.assert_called_once_with(crash_object)
        else:
            assert crash_object_saved == crash_object
            self.dcpy_m.assert_called_once_with(crash_object)

        if not exists:
            crash_path.write_bytes.assert_called_once_with(self.pkl_m.return_value)
        else:
            new_path.write_bytes.assert_called_once_with(self.pkl_m.return_value)


@pytest.mark.parametrize("message", ("error", "real error", 4532))
@pytest.mark.parametrize("exit_code", range(-3, 4))
def test_handle_fatal_error_exit(capsys, message, exit_code):
    with pytest.raises(SystemExit, match=str(exit_code)):
        handle_fatal_error_exit(str(message), exit_code=exit_code)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == str(message)


@mock.patch("vcm.settings.settings")
@mock.patch("vcm.core.utils.Printer.print")
@mock.patch("vcm.core.utils.get_webbrowser")
def test_open_http_status_server(browser_m, print_m, settings_m):
    settings_m.http_status_port = "<http-port>"
    open_http_status_server()

    print_m.assert_called_once_with("Opening state server")
    browser_m.assert_called_once()
    open_m = browser_m.return_value.open_new
    open_m.assert_called_once()
    assert "--new-window" in open_m.call_args[0][0]
    assert "http://localhost:<http-port>" in open_m.call_args[0][0]

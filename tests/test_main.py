from argparse import Namespace
from enum import Enum
import re
import shlex
from unittest import mock

import pytest

from vcm.main import (
    Command,
    NonKeyBasedSettingsSubcommand,
    Parser,
    execute_discover,
    execute_download,
    execute_notify,
    execute_settings,
    get_command,
    instructions,
    main,
    show_version,
)


class TestCommand:
    def test_inherintance(self):
        assert issubclass(Command, Enum)

    def test_length(self):
        assert len(Command) == 5

    def test_attributes(self):
        assert hasattr(Command, "notify")
        assert hasattr(Command, "download")
        assert hasattr(Command, "settings")
        assert hasattr(Command, "discover")
        assert hasattr(Command, "version")

    def test_types(self):
        assert isinstance(Command.notify.value, int)
        assert isinstance(Command.download.value, int)
        assert isinstance(Command.settings.value, int)
        assert isinstance(Command.discover.value, int)
        assert isinstance(Command.version.value, int)

    def test_to_str(self):
        assert Command.notify.to_str() == Command.notify.name
        assert Command.download.to_str() == Command.download.name
        assert Command.settings.to_str() == Command.settings.name
        assert Command.discover.to_str() == Command.discover.name
        assert Command.version.to_str() == Command.version.name


@mock.patch("sys.argv")
def set_args(string=None, sys_argv_m=None):
    real_args = ["test.py"] + shlex.split(string)
    sys_argv_m.__getitem__.side_effect = lambda s: real_args[s]
    try:
        args = Parser.parse_args()
        return args
    finally:
        sys_argv_m.__getitem__.assert_called_once_with(slice(1, None, None))


def test_parser():
    assert Parser
    assert hasattr(Parser, "init_parser")
    assert hasattr(Parser, "parse_args")
    assert hasattr(Parser, "error")


class TestParseArgs:
    class TestPositionalArguments:
        def test_no_args(self):
            opt = set_args("")
            assert opt.no_status_server is False
            assert opt.version is False
            assert opt.check_updates is False

        def test_nss(self):
            opt = set_args("-nss")
            assert opt.no_status_server is True
            assert opt.version is False
            assert opt.check_updates is False

        def test_version(self):
            opt = set_args("-v")
            assert opt.version is True
            assert opt.no_status_server is False
            assert opt.check_updates is False

            opt = set_args("--v")
            assert opt.version is True
            assert opt.no_status_server is False
            assert opt.check_updates is False

            opt = set_args("--version")
            assert opt.version is True
            assert opt.no_status_server is False
            assert opt.check_updates is False

        def test_check_updates(self, capsys):
            with pytest.raises(SystemExit):
                opt = set_args("-check-updates")

            captured = capsys.readouterr()
            assert "unrecognized arguments: -check-updates" in captured.err
            assert captured.out == ""

            opt = set_args("--check-updates")
            assert opt.check_updates is True
            assert opt.no_status_server is False
            assert opt.version is False

            opt = set_args("--c")
            assert opt.check_updates is True
            assert opt.no_status_server is False
            assert opt.version is False

    class TestDownload:
        def test_no_arguments(self):
            opt = set_args("download")
            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is False

        def test_nthreads_ok(self):
            opt = set_args("download --nthreads 10")

            assert opt.command == "download"
            assert opt.nthreads == 10
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is False

        def test_nthreads_error(self, capsys):
            with pytest.raises(SystemExit):
                set_args("download --nthreads <invalid>")

            captured = capsys.readouterr()
            assert "invalid int value: '<invalid>'" in captured.err
            assert captured.out == ""

        def test_no_killer(self):
            opt = set_args("download --no-killer")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is True
            assert opt.debug is False
            assert opt.quiet is False

        def test_debug(self):
            opt = set_args("download --debug")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is True
            assert opt.quiet is False

            opt = set_args("download -d")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is True
            assert opt.quiet is False

        def test_quiet(self):
            opt = set_args("download --quiet")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is True

            opt = set_args("download -q")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is True

    class TestNotify:
        def test_no_arguments(self):
            opt = set_args("notify")

            assert opt.command == "notify"
            assert opt.nthreads == 20
            assert opt.no_icons is False

        def test_nthreads_ok(self):
            opt = set_args("notify --nthreads 10")

            assert opt.command == "notify"
            assert opt.nthreads == 10
            assert opt.no_icons is False

        def test_nthreads_error(self, capsys):
            with pytest.raises(SystemExit):
                set_args("notify --nthreads <invalid>")

            captured = capsys.readouterr()
            assert "invalid int value: '<invalid>'" in captured.err
            assert captured.out == ""

        def test_no_icons(self):
            opt = set_args("notify --no-icons")

            assert opt.command == "notify"
            assert opt.nthreads == 20
            assert opt.no_icons is True

    class TestSettings:
        def test_no_args(self, capsys):
            with pytest.raises(SystemExit):
                set_args("settings")

            captured = capsys.readouterr()
            expected = "the following arguments are required: settings_subcommand"
            assert expected in captured.err
            assert captured.out == ""

        def test_list(self):
            opt = set_args("settings list")

            assert opt.command == "settings"
            assert opt.settings_subcommand == "list"

        class TestSet:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings set")

                captured = capsys.readouterr()
                expected = "the following arguments are required: key, value"
                assert expected in captured.err
                assert captured.out == ""

            def test_no_value(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings set key")

                captured = capsys.readouterr()
                assert "the following arguments are required: value" in captured.err
                assert captured.out == ""

            def test_ok(self):
                opt = set_args("settings set key value")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "set"
                assert opt.key == "key"
                assert opt.value == "value"

        class TestShow:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings show")

                captured = capsys.readouterr()
                assert "the following arguments are required: key" in captured.err
                assert captured.out == ""

            def test_ok(self):
                opt = set_args("settings show key")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "show"
                assert opt.key == "key"

        class TestExclude:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings exclude")

                captured = capsys.readouterr()
                expected = "the following arguments are required: subject_id"
                assert expected in captured.err
                assert captured.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings exclude <subject-id>")

                captured = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in captured.err
                assert captured.out == ""

            def test_ok(self):
                opt = set_args("settings exclude 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "exclude"
                assert opt.subject_id == 654321

        class TestInclude:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings include")

                captured = capsys.readouterr()
                expected = "the following arguments are required: subject_id"
                assert expected in captured.err
                assert captured.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings include <subject-id>")

                captured = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in captured.err
                assert captured.out == ""

            def test_ok(self):
                opt = set_args("settings include 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "include"
                assert opt.subject_id == 654321

        class TestIndex:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings index")

                captured = capsys.readouterr()
                expected = "the following arguments are required: subject_id"
                assert expected in captured.err
                assert captured.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings index <subject-id>")

                captured = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in captured.err
                assert captured.out == ""

            def test_ok(self):
                opt = set_args("settings index 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "index"
                assert opt.subject_id == 654321

        class TestUnIndex:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings unindex")

                captured = capsys.readouterr()
                expected = "the following arguments are required: subject_id"
                assert expected in captured.err
                assert captured.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    set_args("settings unindex <subject-id>")

                captured = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in captured.err
                assert captured.out == ""

            def test_ok(self):
                opt = set_args("settings unindex 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "unindex"
                assert opt.subject_id == 654321

        def test_keys(self):
            opt = set_args("settings keys")

            assert opt.command == "settings"
            assert opt.settings_subcommand == "keys"

        def test_check(self):
            opt = set_args("settings check")

            assert opt.command == "settings"
            assert opt.settings_subcommand == "check"

    def test_discover(self):
        opt = set_args("discover")

        assert opt.command == "discover"

    def test_version_command(self):
        opt = set_args("version")
        assert opt.command == "version"


def test_parser_error(capsys):
    Parser.init_parser()
    with pytest.raises(SystemExit, match="2"):
        Parser.error("custom error")

    captured = capsys.readouterr()
    assert "custom error" in captured.err
    assert captured.out == ""


@pytest.mark.parametrize("command", list(Command) + [None, "invalid"])
@mock.patch("vcm.main.Parser.error")
def test_get_command(error_m, command):
    error_m.side_effect = SystemExit

    if command in [None, "invalid"]:
        with pytest.raises(SystemExit):
            get_command(command)

        error_m.assert_called_once()
        assert str(command) in error_m.call_args[0][0]
        assert "Invalid command" in error_m.call_args[0][0]
        return

    returned = get_command(command)
    error_m.assert_not_called()
    assert isinstance(returned, Command)


@mock.patch("vcm.main.version")
def test_show_version(version_m, capsys):
    version_m.__str__.return_value = "<version>"

    show_version()

    result = capsys.readouterr()
    assert result.out == "Version: <version>\n"
    assert result.err == ""


@mock.patch("vcm.main.download")
@mock.patch("vcm.main.Printer.silence")
def test_execute_discover(silence_m, download_m):
    opt = Namespace()  # Compatibility purposes
    execute_discover(opt)

    silence_m.assert_called_once_with()
    download_m.assert_called_once_with(
        nthreads=1, killer=False, status_server=False, discover_only=True
    )


class TestExecuteDownload:
    @pytest.fixture(autouse=True)
    def mocks(self):

        self.ohss_m = mock.patch("vcm.main.open_http_status_server").start()
        self.download_m = mock.patch("vcm.main.download").start()
        yield

        mock.patch.stopall()

    @pytest.fixture(params=[True, False])
    def debug(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def server(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def killer(self, request):
        return request.param

    @pytest.fixture(params=[1, 5, 10, 15, 20])
    def nthreads(self, request):
        return request.param

    def test_execute_download(self, debug, killer, nthreads, server):
        opt = Namespace(
            debug=debug,
            no_killer=not killer,
            nthreads=nthreads,
            no_status_server=not server,
        )
        execute_download(opt)

        if debug:
            self.ohss_m.assert_called_once_with()
        else:
            self.ohss_m.assert_not_called()

        self.download_m.assert_called_once_with(
            nthreads=nthreads, killer=killer, status_server=server
        )


class TestExecuteNotify:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.notify_m = mock.patch("vcm.main.notify").start()
        self.settings_m = mock.patch("vcm.main.settings").start()
        self.settings_m.email = "<email>"

        yield

        mock.patch.stopall()

    @pytest.fixture(params=[True, False])
    def icons(self, request):
        return request.param

    @pytest.fixture(params=[1, 10, 50])
    def nthreads(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def server(self, request):
        return request.param

    def test_execute_notify(self, icons, nthreads, server):
        opt = Namespace(
            no_icons=not icons, nthreads=nthreads, no_status_server=not server
        )
        execute_notify(opt)

        self.notify_m.assert_called_once_with(
            send_to="<email>", use_icons=icons, nthreads=nthreads, status_server=server
        )


class TestNonKeyBasedSettingsSubcommand:  # pylint: disable=too-many-instance-attributes
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.sts_m = mock.patch("vcm.main.settings_to_string").start()
        self.sts_m.return_value = "<settings-to-str>"
        self.check_m = mock.patch("vcm.main.CheckSettings.check").start()
        self.exclude_m = mock.patch("vcm.main.exclude").start()
        self.include_m = mock.patch("vcm.main.include").start()
        self.print_m = mock.patch("vcm.main.Printer.print").start()
        self.sect_idx_m = mock.patch("vcm.main.section_index").start()
        self.unsect_idx_m = mock.patch("vcm.main.un_section_index").start()
        self.settings_dict = {"key1": 1, "key2": True, "key3": "three"}
        mock.patch("vcm.main.settings", self.settings_dict).start()

        NonKeyBasedSettingsSubcommand.opt = None

        yield

        mock.patch.stopall()

    @mock.patch("vcm.main.getattr")
    def test_execute(self, getattr_m):
        opt = mock.MagicMock(settings_subcommand="<set-subcommand>")
        NonKeyBasedSettingsSubcommand.execute(opt)
        assert NonKeyBasedSettingsSubcommand.opt == opt

        getattr_m.assert_called_once_with(
            NonKeyBasedSettingsSubcommand, "<set-subcommand>"
        )
        self.sts_m.assert_not_called()
        self.check_m.assert_not_called()
        self.exclude_m.assert_not_called()
        self.include_m.assert_not_called()
        self.print_m.assert_not_called()
        self.sect_idx_m.assert_not_called()
        self.unsect_idx_m.assert_not_called()

    def test_list(self, capsys):
        NonKeyBasedSettingsSubcommand.list()

        result = capsys.readouterr()
        assert result.err == ""
        assert result.out == "<settings-to-str>\n"

        self.sts_m.assert_called_once_with()
        self.check_m.assert_not_called()
        self.exclude_m.assert_not_called()
        self.include_m.assert_not_called()
        self.print_m.assert_not_called()
        self.sect_idx_m.assert_not_called()
        self.unsect_idx_m.assert_not_called()

    def test_check(self, capsys):
        NonKeyBasedSettingsSubcommand.check()

        result = capsys.readouterr()
        assert result.err == ""
        assert result.out == "Checked\n"

        self.sts_m.assert_not_called()
        self.check_m.assert_called_once_with()
        self.exclude_m.assert_not_called()
        self.include_m.assert_not_called()
        self.print_m.assert_not_called()
        self.sect_idx_m.assert_not_called()
        self.unsect_idx_m.assert_not_called()

    def test_exclude(self):
        opt = Namespace(subject_id=9876543210)
        NonKeyBasedSettingsSubcommand.opt = opt
        NonKeyBasedSettingsSubcommand.exclude()

        self.sts_m.assert_not_called()
        self.check_m.assert_not_called()
        self.exclude_m.assert_called_once_with(9876543210)
        self.include_m.assert_not_called()
        self.print_m.assert_not_called()
        self.sect_idx_m.assert_not_called()
        self.unsect_idx_m.assert_not_called()

    def test_include(self):
        opt = Namespace(subject_id=9876543210)
        NonKeyBasedSettingsSubcommand.opt = opt
        NonKeyBasedSettingsSubcommand.include()

        self.sts_m.assert_not_called()
        self.check_m.assert_not_called()
        self.exclude_m.assert_not_called()
        self.include_m.assert_called_once_with(9876543210)
        self.print_m.assert_not_called()
        self.sect_idx_m.assert_not_called()
        self.unsect_idx_m.assert_not_called()

    def test_index(self):
        opt = Namespace(subject_id=9876543210)
        NonKeyBasedSettingsSubcommand.opt = opt
        NonKeyBasedSettingsSubcommand.index()

        self.sts_m.assert_not_called()
        self.check_m.assert_not_called()
        self.exclude_m.assert_not_called()
        self.include_m.assert_not_called()
        self.print_m.assert_called_once()
        self.sect_idx_m.assert_called_once_with(9876543210)
        self.unsect_idx_m.assert_not_called()

    def test_un_index(self):
        opt = Namespace(subject_id=9876543210)
        NonKeyBasedSettingsSubcommand.opt = opt
        NonKeyBasedSettingsSubcommand.un_index()

        self.sts_m.assert_not_called()
        self.check_m.assert_not_called()
        self.exclude_m.assert_not_called()
        self.include_m.assert_not_called()
        self.print_m.assert_called_once()
        self.sect_idx_m.assert_not_called()
        self.unsect_idx_m.assert_called_once_with(9876543210)

    def test_keys(self, capsys):
        NonKeyBasedSettingsSubcommand.keys()

        result = capsys.readouterr()
        assert result.err == ""
        assert result.out == " - key1\n - key2\n - key3\n"

        self.sts_m.assert_not_called()
        self.check_m.assert_not_called()
        self.exclude_m.assert_not_called()
        self.include_m.assert_not_called()
        self.print_m.assert_not_called()
        self.sect_idx_m.assert_not_called()
        self.unsect_idx_m.assert_not_called()


class TestExecuteSettings:
    key_based_commands = ["set", "show"]
    rest = ["list", "check", "exclude", "include", "index", "un_index", "keys"]

    class DummyClass:  # pylint: disable=too-few-public-methods
        pass

    @pytest.fixture(autouse=True)
    def mocks(self):
        self.execute_m = mock.patch(
            "vcm.main.NonKeyBasedSettingsSubcommand.execute"
        ).start()
        self.settings_m = mock.patch("vcm.main.settings").start()
        self.getattr_m = mock.patch("vcm.main.getattr").start()
        self.getattr_m.return_value = "requested-value"
        self.setattr_m = mock.patch("vcm.main.setattr").start()

        yield

        mock.patch.stopall()

    @pytest.mark.parametrize("command", key_based_commands)
    def test_key_based_settings(self, command, capsys):
        self.execute_m.side_effect = AttributeError

        opt = Namespace(
            settings_subcommand=command, value="value", key="key"
        )
        execute_settings(opt)

        result = capsys.readouterr()
        assert result.err == ""

        self.execute_m.assert_called_once_with(opt)

        if command == "set":
            self.getattr_m.assert_not_called()
            self.setattr_m.assert_called_once_with(
                self.settings_m, "key", "value"
            )
            assert result.out == ""
        if command == "show":
            self.getattr_m.assert_called_once_with(self.settings_m, "key")
            self.setattr_m.assert_not_called()
            assert result.out == "key: 'requested-value'\n"

    @pytest.mark.parametrize("command", rest)
    def test_not_key_based_settings(self, command, capsys):
        opt = Namespace(
            settings_subcommand=command, value="value", key="key"
        )
        executed_result = execute_settings(opt)
        assert executed_result == self.execute_m.return_value

        result = capsys.readouterr()
        assert result.err == ""
        assert result.out == ""

        self.execute_m.assert_called_once_with(opt)
        self.getattr_m.assert_not_called()
        self.setattr_m.assert_not_called()


class TestMain:
    @pytest.fixture(autouse=True)
    def mocks(self):
        mock.patch("vcm.main.version", "<version>").start()
        self.parse_args_m = mock.patch("vcm.main.Parser.parse_args").start()
        self.show_ver_m = mock.patch("vcm.main.show_version").start()
        self.check_up_m = mock.patch("vcm.main.check_updates").start()
        self.get_com_m = mock.patch("vcm.main.get_command").start()
        self.silence_m = mock.patch("vcm.main.Printer.silence").start()
        self.setup_m = mock.patch("vcm.main.setup_vcm").start()
        self.instructions_m = mock.patch("vcm.main.instructions").start()

        yield

        mock.patch.stopall()

    def set_args(self, **kwargs):
        real_args = {
            "version": False,
            "check_updates": False,
            "command": None,
            "quiet": False,
            "extra_kwarg1": 1,
            "extra_kwarg2": 2,
            "extra_kwarg3": 3,
        }

        real_args.update(kwargs)

        self.parse_args_m.return_value = Namespace(**real_args)

    def test_version_argument(self, caplog):
        caplog.set_level(10, "vcm.main")
        self.set_args(version=True)

        result = main()
        assert result == self.show_ver_m.return_value

        self.parse_args_m.assert_called_once_with()
        self.show_ver_m.assert_called_once_with()
        self.check_up_m.assert_not_called()
        self.get_com_m.assert_not_called()
        self.silence_m.assert_not_called()
        self.setup_m.assert_not_called()

        assert len(caplog.records) == 0

    def test_check_updates(self, caplog):
        caplog.set_level(10, "vcm.main")
        self.set_args(check_updates=True)

        result = main()
        assert result == self.check_up_m.return_value

        self.parse_args_m.assert_called_once_with()
        self.show_ver_m.assert_not_called()
        self.check_up_m.assert_called_once_with()
        self.get_com_m.assert_not_called()
        self.silence_m.assert_not_called()
        self.setup_m.assert_not_called()

        assert len(caplog.records) == 0

    @pytest.mark.parametrize("quiet", [True, False])
    def test_download(self, quiet, caplog):
        caplog.set_level(10, "vcm.main")
        self.set_args(quiet=quiet, command="download")
        self.get_com_m.return_value = Command.download

        result = main()
        assert result == self.instructions_m.__getitem__.return_value.return_value

        self.parse_args_m.assert_called_once_with()
        self.show_ver_m.assert_not_called()
        self.check_up_m.assert_not_called()
        self.get_com_m.assert_called_once_with("download")
        if quiet:
            self.silence_m.assert_called_once_with()
        else:
            self.silence_m.assert_not_called()
        self.setup_m.assert_called_once_with()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.message == "vcm version: <version>"
        assert record.levelname == "INFO"

    def test_notify(self, caplog):
        caplog.set_level(10, "vcm.main")
        self.set_args(command="notify")
        self.get_com_m.return_value = Command.notify

        result = main()
        assert result == self.instructions_m.__getitem__.return_value.return_value

        self.parse_args_m.assert_called_once_with()
        self.show_ver_m.assert_not_called()
        self.check_up_m.assert_not_called()
        self.get_com_m.assert_called_once_with("notify")
        self.silence_m.assert_not_called()
        self.setup_m.assert_called_once_with()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.message == "vcm version: <version>"
        assert record.levelname == "INFO"

    def test_discover(self, caplog):
        caplog.set_level(10, "vcm.main")
        self.set_args(command="discover")
        self.get_com_m.return_value = Command.discover

        result = main()
        assert result == self.instructions_m.__getitem__.return_value.return_value

        self.parse_args_m.assert_called_once_with()
        self.show_ver_m.assert_not_called()
        self.check_up_m.assert_not_called()
        self.get_com_m.assert_called_once_with("discover")
        self.silence_m.assert_not_called()
        self.setup_m.assert_called_once_with()

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.message == "vcm version: <version>"
        assert record.levelname == "INFO"

    def test_settings(self, caplog):
        caplog.set_level(10, "vcm.main")
        self.set_args(command="settings")
        self.get_com_m.return_value = Command.settings

        result = main()
        assert result == self.instructions_m.__getitem__.return_value.return_value

        self.parse_args_m.assert_called_once_with()
        self.show_ver_m.assert_not_called()
        self.check_up_m.assert_not_called()
        self.get_com_m.assert_called_once_with("settings")
        self.silence_m.assert_not_called()
        self.setup_m.assert_not_called()

        assert len(caplog.records) == 0


def test_instructions_dict():
    assert isinstance(instructions, dict)

    for key, value in instructions.items():
        assert isinstance(key, str)
        assert callable(value)

    for command in Command:
        assert command.name in instructions

    assert len(Command) == len(instructions)

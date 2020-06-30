import shlex
from argparse import Namespace
from enum import Enum
from unittest import mock

import pytest

from vcm.main import (
    Command,
    Parser,
    execute_discover,
    execute_download,
    execute_notify,
    get_command,
    show_version,
)


class TestCommand:
    def test_inherintance(self):
        assert issubclass(Command, Enum)

    def test_attributes(self):
        assert hasattr(Command, "notify")
        assert hasattr(Command, "download")
        assert hasattr(Command, "settings")
        assert hasattr(Command, "discover")

    def test_types(self):
        assert isinstance(Command.notify.value, int)
        assert isinstance(Command.download.value, int)
        assert isinstance(Command.settings.value, int)
        assert isinstance(Command.discover.value, int)

    def test_to_str(self):
        assert Command.notify.to_str() == Command.notify.name
        assert Command.download.to_str() == Command.download.name
        assert Command.settings.to_str() == Command.settings.name
        assert Command.discover.to_str() == Command.discover.name


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


class TestMain:
    @pytest.fixture(scope="function", autouse=True)
    def mocks(self):
        self.virtual_version = "1.0.1-a2"
        self.email = "support@example.com"
        self.set_classes = ["set_class_a", "set_class_b", "set_class_c"]

        self.ns_m = mock.patch("vcm.main.NotifySettings").start()
        self._parse_args_m = mock.patch("vcm.main.parse_args").start()
        self.version_m = mock.patch("vcm.main.version", self.virtual_version).start()
        self.cu_m = mock.patch("vcm.main.check_updates").start()
        self.printer_m = mock.patch("vcm.main.Printer").start()
        self.sts_m = mock.patch("vcm.main.settings_to_string").start()
        self.mrsc_m = mock.patch("vcm.main.more_settings_check").start()
        self.exclude_m = mock.patch("vcm.main.exclude").start()
        self.include_m = mock.patch("vcm.main.include").start()
        self.sect_indx_m = mock.patch("vcm.main.section_index").start()
        self.un_sect_indx_m = mock.patch("vcm.main.un_section_index").start()
        self.sntc_m = mock.patch("vcm.main.settings_name_to_class").start()
        self.sc_m = mock.patch("vcm.main.SETTINGS_CLASSES", self.set_classes).start()
        self.webbrowser_m_get = mock.patch("vcm.main.get_webbrowser").start()
        self.download_m = mock.patch("vcm.main.download").start()
        self.notify_m = mock.patch("vcm.main.notify").start()
        self.safe_exit_m = mock.patch("vcm.main.safe_exit").start()
        self.setattr_m = mock.patch("vcm.main.setattr").start()
        self.getattr_m = mock.patch("vcm.main.getattr").start()

        self.parse_args_m = mock.MagicMock()
        self.parser_m = mock.MagicMock()

        self.ns_m.email = self.email
        self._parse_args_m.return_value = (self.parse_args_m, self.parser_m)

        self.sntc_dict = {
            "set_class_a": {"a1": "a1.val.orig"},
            "set_class_b": {"b1": "b1.val.orig", "b2": "b2.val.orig"},
            "set_class_c": {
                "c1": "c1.val.orig",
                "c2": "c2.val.orig",
                "c3": "c3.val.orig",
            },
        }
        self.sntc_m.__getitem__.side_effect = lambda x: self.sntc_dict[x]

        # parser.error calls sys.exit(), so this helper does the same.
        def helper(message):
            import sys

            print(message, file=sys.stderr)
            sys.exit()

        self.parser_m.error = helper

        yield

        mock.patch.stopall()

    def set_namespace(self, **kwargs):
        def_kwargs = dict(
            version=False,
            check_updates=False,
            command=None,
            settings_subcommand=None,
            subject_id=None,
            no_status_server=False,
        )

        def_kwargs.update(kwargs)
        self._parse_args_m.return_value = (Namespace(**def_kwargs), self.parser_m)

    @pytest.mark.parametrize("mode", ("argument", "command"))
    def test_version(self, capsys, mode):
        if mode == "argument":
            self.set_namespace(version=True)
        else:
            self.set_namespace(command="version")

        # with pytest.raises(SystemExit):
        main()

        captured = capsys.readouterr()
        assert self.virtual_version in captured.out
        assert captured.err == ""

    def test_check_updates(self):
        self.set_namespace(check_updates=True)

        main()

        self.printer_m.silence.not_called()
        self.cu_m.assert_called_once_with()

    def test_settings_list(self):
        self.set_namespace(command="settings", settings_subcommand="list")

        main()

        self.printer_m.silence.not_called()
        self.sts_m.assert_called_once()

    def test_invalid_command(self, capsys):
        self.set_namespace(command="invalid-command")

        # parser.error calls exit()
        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Invalid command ('invalid-command'). Valid commands: " in captured.err
        assert captured.out == ""

    def test_settings_check(self):
        self.set_namespace(command="settings", settings_subcommand="check")

        main()

        self.printer_m.silence.not_called()
        self.mrsc_m.assert_called_once()

    def test_settings_exclude(self):
        self.set_namespace(
            command="settings", settings_subcommand="exclude", subject_id=23
        )

        main()

        self.printer_m.silence.not_called()
        self.exclude_m.assert_called_once_with(23)

    def test_settings_include(self):
        self.set_namespace(
            command="settings", settings_subcommand="include", subject_id=23
        )

        main()

        self.printer_m.silence.not_called()
        self.include_m.assert_called_once_with(23)

    def test_settings_index(self):
        self.set_namespace(
            command="settings", settings_subcommand="index", subject_id=23
        )

        main()

        self.printer_m.silence.not_called()
        self.sect_indx_m.assert_called_once_with(23)

        self.printer_m.print.assert_called_once()

    def test_settings_unindex(self):
        self.set_namespace(
            command="settings", settings_subcommand="unindex", subject_id=23
        )

        main()

        self.printer_m.silence.not_called()
        self.un_sect_indx_m.assert_called_once_with(23)

        self.printer_m.print.assert_called_once()

    def test_settings_keys(self, capsys):
        self.set_namespace(command="settings", settings_subcommand="keys")

        main()

        captured = capsys.readouterr()
        assert captured.err == ""

        for settings_class, settings_values in self.sntc_dict.items():
            for key in settings_values.keys():
                string = "- %s.%s" % (settings_class, key)
                assert string in captured.out

    def test_settings_invalid_key_format_error(self, capsys):
        self.set_namespace(
            command="settings", settings_subcommand="set", key="invalid.key.for.real"
        )

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Invalid key (must be section.setting)" in captured.err
        assert captured.out == ""

    def test_settings_invalid_class_error(self, capsys):
        self.set_namespace(
            command="settings", settings_subcommand="set", key="invalid.key"
        )

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Invalid setting class: 'invalid'" in captured.err
        assert captured.out == ""

    def test_settings_invalid_key_error(self, capsys):
        self.set_namespace(
            command="settings", setings_subcommand="set", key="set_class_b.invalid_key"
        )

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert (
            "'invalid_key' is not a valid set_class_b setting (valids are"
            in captured.err
        )
        assert captured.out == ""

    def test_settings_set(self):
        self.set_namespace(
            command="settings",
            settings_subcommand="set",
            key="set_class_b.b2",
            value="b2.value",
        )

        main()

        set_class = self.sntc_dict["set_class_b"]
        self.setattr_m.assert_called_once_with(set_class, "b2", "b2.value")

    def test_settings_show(self, capsys):
        def helper(cls, key):
            return cls[key]

        self.set_namespace(
            command="settings", settings_subcommand="show", key="set_class_b.b2"
        )
        self.getattr_m.side_effect = helper

        main()

        set_class = self.sntc_dict["set_class_b"]
        message = "set_class_b.b2: '%s'" % set_class["b2"]
        self.getattr_m.assert_called_once_with(set_class, "b2")

        captured = capsys.readouterr()
        assert message in captured.out
        assert captured.err == ""

    def test_discover(self):
        self.set_namespace(command="discover")

        # with pytest.raises(SystemExit):
        main()

        self.printer_m.silence.assert_called_once()
        self.download_m.assert_called_once_with(
            nthreads=1, no_killer=True, status_server=False, discover_only=True
        )

    @pytest.mark.parametrize("quiet", [True, False])
    @pytest.mark.parametrize("debug", [True, False])
    def test_download(self, quiet, debug):
        self.set_namespace(
            command="download",
            no_status_server=True,
            nthreads=15,
            no_killer=True,
            debug=debug,
            quiet=quiet,
        )

        main()

        if quiet:
            self.printer_m.silence.assert_called_once()
        else:
            self.printer_m.silence.assert_not_called()

        if debug:
            self.webbrowser_m_get.assert_called()
            self.webbrowser_m_get.return_value.open_new.assert_called_once_with(
                f'--new-window "http://localhost:{GeneralSettings.http_status_port}"'
            )
        else:
            self.webbrowser_m_get.assert_not_called()
            self.webbrowser_m_get.return_value.open_new.assert_not_called()

        self.download_m.assert_called_once_with(
            nthreads=15, no_killer=True, status_server=False,
        )

    def test_notify(self):
        self.set_namespace(
            command="notify", no_icons=True, nthreads=23, no_status_server=True
        )

        main()

        self.printer_m.silence.assert_not_called()
        self.notify_m.assert_called_once_with(
            use_icons=False, nthreads=23, status_server=False, send_to=self.email
        )

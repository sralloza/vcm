from argparse import ArgumentParser, Namespace
from enum import Enum

import pytest

from vcm.main import Command, parse_args


def modified_parse_args(string: str, return_parser=False):
    return parse_args(string.split(), return_parser=return_parser)


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

    def to_str(self):
        assert Command.notify.to_str() == Command.notify.name
        assert Command.download.to_str() == Command.download.name
        assert Command.settings.to_str() == Command.settings.name
        assert Command.discover.to_str() == Command.discover.name


class TestParseArgs:
    @pytest.mark.parametrize("return_parser", [True, False])
    def test_return_parser_arg(self, return_parser):
        opt = modified_parse_args("", return_parser=return_parser)

        if return_parser:
            assert isinstance(opt, tuple)
            assert len(opt) == 2
            assert isinstance(opt[0], Namespace)
            assert isinstance(opt[1], ArgumentParser)
        else:
            assert isinstance(opt, Namespace)

    class TestPositionalArguments:
        def test_no_args(self):
            opt = modified_parse_args("")
            assert opt.no_status_server is False
            assert opt.version is False
            assert opt.check_updates is False

        def test_nss(self):
            opt = modified_parse_args("-nss")
            assert opt.no_status_server is True
            assert opt.version is False
            assert opt.check_updates is False

        def test_version(self):
            opt = modified_parse_args("-v")
            assert opt.version is True
            assert opt.no_status_server is False
            assert opt.check_updates is False

            opt = modified_parse_args("--v")
            assert opt.version is True
            assert opt.no_status_server is False
            assert opt.check_updates is False

            opt = modified_parse_args("--version")
            assert opt.version is True
            assert opt.no_status_server is False
            assert opt.check_updates is False

        def test_check_updates(self, capsys):
            with pytest.raises(SystemExit):
                opt = modified_parse_args("-check-updates")

            result = capsys.readouterr()
            assert "unrecognized arguments: -check-updates" in result.err
            assert result.out == ""

            opt = modified_parse_args("--check-updates")
            assert opt.check_updates is True
            assert opt.no_status_server is False
            assert opt.version is False

            opt = modified_parse_args("--c")
            assert opt.check_updates is True
            assert opt.no_status_server is False
            assert opt.version is False

    class TestDownload:
        def test_no_arguments(self):
            opt = modified_parse_args("download")
            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is False

        def test_nthreads_ok(self):
            opt = modified_parse_args("download --nthreads 10")

            assert opt.command == "download"
            assert opt.nthreads == 10
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is False

        def test_nthreads_error(self, capsys):
            with pytest.raises(SystemExit):
                modified_parse_args("download --nthreads <invalid>")

            results = capsys.readouterr()
            assert "invalid int value: '<invalid>'" in results.err
            assert results.out == ""

        def test_no_killer(self):
            opt = modified_parse_args("download --no-killer")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is True
            assert opt.debug is False
            assert opt.quiet is False

        def test_debug(self):
            opt = modified_parse_args("download --debug")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is True
            assert opt.quiet is False

            opt = modified_parse_args("download -d")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is True
            assert opt.quiet is False

        def test_quiet(self):
            opt = modified_parse_args("download --quiet")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is True

            opt = modified_parse_args("download -q")

            assert opt.command == "download"
            assert opt.nthreads == 20
            assert opt.no_killer is False
            assert opt.debug is False
            assert opt.quiet is True

    class TestNotify:
        def test_no_arguments(self):
            opt = modified_parse_args("notify")

            assert opt.command == "notify"
            assert opt.nthreads == 20
            assert opt.no_icons is False

        def test_nthreads_ok(self):
            opt = modified_parse_args("notify --nthreads 10")

            assert opt.command == "notify"
            assert opt.nthreads == 10
            assert opt.no_icons is False

        def test_nthreads_error(self, capsys):
            with pytest.raises(SystemExit):
                modified_parse_args("notify --nthreads <invalid>")

            results = capsys.readouterr()
            assert "invalid int value: '<invalid>'" in results.err
            assert results.out == ""

        def test_no_icons(self):
            opt = modified_parse_args("notify --no-icons")

            assert opt.command == "notify"
            assert opt.nthreads == 20
            assert opt.no_icons is True

    class TestSettings:
        def test_no_args(self, capsys):
            with pytest.raises(SystemExit):
                modified_parse_args("settings")

            results = capsys.readouterr()
            assert (
                "the following arguments are required: settings_subcommand"
                in results.err
            )
            assert results.out == ""

        def test_list(self):
            opt = modified_parse_args("settings list")

            assert opt.command == "settings"
            assert opt.settings_subcommand == "list"

        class TestSet:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings set")

                results = capsys.readouterr()
                assert "the following arguments are required: key, value" in results.err
                assert results.out == ""

            def test_no_value(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings set key")

                results = capsys.readouterr()
                assert "the following arguments are required: value" in results.err
                assert results.out == ""

            def test_ok(self):
                opt = modified_parse_args("settings set key value")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "set"
                assert opt.key == "key"
                assert opt.value == "value"

        class TestShow:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings show")

                results = capsys.readouterr()
                assert "the following arguments are required: key" in results.err
                assert results.out == ""

            def test_ok(self):
                opt = modified_parse_args("settings show key")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "show"
                assert opt.key == "key"

        class TestExclude:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings exclude")

                result = capsys.readouterr()
                assert "the following arguments are required: subject_id" in result.err
                assert result.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings exclude <subject-id>")

                result = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in result.err
                assert result.out == ""

            def test_ok(self):
                opt = modified_parse_args("settings exclude 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "exclude"
                assert opt.subject_id == 654321

        class TestInclude:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings include")

                result = capsys.readouterr()
                assert "the following arguments are required: subject_id" in result.err
                assert result.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings include <subject-id>")

                result = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in result.err
                assert result.out == ""

            def test_ok(self):
                opt = modified_parse_args("settings include 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "include"
                assert opt.subject_id == 654321

        class TestIndex:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings index")

                result = capsys.readouterr()
                assert "the following arguments are required: subject_id" in result.err
                assert result.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings index <subject-id>")

                result = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in result.err
                assert result.out == ""

            def test_ok(self):
                opt = modified_parse_args("settings index 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "index"
                assert opt.subject_id == 654321

        class TestUnIndex:
            def test_no_args(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings unindex")

                result = capsys.readouterr()
                assert "the following arguments are required: subject_id" in result.err
                assert result.out == ""

            def test_type_error(self, capsys):
                with pytest.raises(SystemExit):
                    modified_parse_args("settings unindex <subject-id>")

                result = capsys.readouterr()
                assert "invalid int value: '<subject-id>'" in result.err
                assert result.out == ""

            def test_ok(self):
                opt = modified_parse_args("settings unindex 654321")

                assert opt.command == "settings"
                assert opt.settings_subcommand == "unindex"
                assert opt.subject_id == 654321

        def test_keys(self):
            opt = modified_parse_args("settings keys")

            assert opt.command == "settings"
            assert opt.settings_subcommand == "keys"

        def test_check(self):
            opt = modified_parse_args("settings check")

            assert opt.command == "settings"
            assert opt.settings_subcommand == "check"

    def test_discover(self):
        opt = modified_parse_args("discover")

        assert opt.command == "discover"


@pytest.mark.xfail
class TestMain:
    def test_main(self):
        assert 0, "Not implemented"

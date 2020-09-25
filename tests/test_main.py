from collections import defaultdict
from unittest import mock

from click.testing import CliRunner
import pytest

from vcm import __version__
from vcm.main import cli, main


@pytest.fixture(autouse=True)
def universal_mocks():
    current_mocker = mock.patch("vcm.main.Modules.set_current")
    setup_mocker = mock.patch("vcm.main.setup_vcm")

    universal_mocks.current = current_mocker.start()
    universal_mocks.setup = setup_mocker.start()

    yield

    current_mocker.stop()
    setup_mocker.stop()


@pytest.mark.parametrize("arg", ["-h", "--help"])
def test_help(arg):
    runner = CliRunner()
    result = runner.invoke(main, [arg])

    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Options:" in result.stdout
    assert "Commands:" in result.stdout

    universal_mocks.current.assert_not_called()
    universal_mocks.setup.assert_not_called()


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output
    assert "vcm" in result.output
    assert "version" in result.output

    universal_mocks.current.assert_not_called()
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.check_updates")
def test_check_updates(check_updates_m):
    universal_mocks.current.side_effect = ValueError
    runner = CliRunner()
    result = runner.invoke(main, ["check-updates"])

    assert result.exit_code == 0
    assert result.output == ""

    check_updates_m.assert_called_once_with()
    universal_mocks.current.assert_called_once_with("check-updates")
    universal_mocks.setup.assert_called_once_with()


@pytest.mark.parametrize("dev", [True, False])
@pytest.mark.parametrize("version", ["v1.2.3", None])
@mock.patch("vcm.main.update")
def test_update_command(update_m, dev, version):
    args = ["update"]
    if dev:
        args.append("--dev")
    if version:
        args.append("--version")
        args.append(version)

    runner = CliRunner()
    result = runner.invoke(main, args)

    assert result.exit_code == 0
    assert result.output == ""

    update_m.assert_called_once_with(dev=dev, version=version)


@pytest.mark.parametrize("nss", [True, False])
@pytest.mark.parametrize("nthreads", [10, 20, 30, None])
@pytest.mark.parametrize("no_killer", [True, False])
@pytest.mark.parametrize("debug", [True, False])
@pytest.mark.parametrize("quiet", [True, False])
@mock.patch("vcm.main.download")
@mock.patch("vcm.main.open_http_status_server")
@mock.patch("vcm.main.Printer.silence")
def test_download(
    silence_m, ohss_m, download_m, nthreads, no_killer, debug, quiet, nss
):
    args = []
    if nss:
        args.append("--no-status-server")

    args.append("download")

    if nthreads:
        args += ["--nthreads", nthreads]
    if no_killer:
        args += ["--no-killer"]
    if debug:
        args += ["--debug"]
    if quiet:
        args += ["--quiet"]

    runner = CliRunner()
    result = runner.invoke(main, args)

    assert result.exit_code == 0
    assert result.output == ""

    nthreads = nthreads or 20
    download_m.assert_called_once_with(
        nthreads=nthreads, killer=not no_killer, status_server=not nss
    )

    if quiet:
        silence_m.assert_called_once_with()
    else:
        silence_m.assert_not_called()

    if debug:
        ohss_m.assert_called_once_with()
    else:
        ohss_m.assert_not_called()

    universal_mocks.current.assert_called_once_with("download")
    universal_mocks.setup.assert_called_once_with()


@pytest.mark.parametrize("nss", [True, False])
@pytest.mark.parametrize("nthreads", [10, 20, 30, None])
@pytest.mark.parametrize("no_icons", [True, False])
@mock.patch("vcm.main.notify")
@mock.patch("vcm.main.settings")
def test_notify(settings_m, notify_m, nthreads, no_icons, nss):
    settings_m.email = "<email>"
    args = []
    if nss:
        args.append("--no-status-server")

    args.append("notify")

    if nthreads:
        args += ["--nthreads", nthreads]
    if no_icons:
        args += ["--no-icons"]

    runner = CliRunner()
    result = runner.invoke(main, args)

    assert result.exit_code == 0
    assert result.output == ""

    nthreads = nthreads or 20
    notify_m.assert_called_once_with(
        send_to="<email>",
        use_icons=not no_icons,
        nthreads=nthreads,
        status_server=not nss,
    )

    universal_mocks.current.assert_called_once_with("notify")
    universal_mocks.setup.assert_called_once_with()


@mock.patch("vcm.main.download")
def test_discover(download_m):
    runner = CliRunner()
    result = runner.invoke(main, ["discover"])

    assert result.exit_code == 0
    assert result.output == ""

    download_m.assert_called_once_with(
        nthreads=1, killer=False, status_server=False, discover_only=True
    )

    universal_mocks.current.assert_called_once_with("discover")
    universal_mocks.setup.assert_called_once_with()


@mock.patch("vcm.main.settings_to_string")
def test_list_settings(settings_to_string_m):
    settings_to_string_m.return_value = "<settings-as-str>"
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "list"])

    assert result.exit_code == 0
    assert result.output == "<settings-as-str>\n"

    settings_to_string_m.assert_called_once_with()

    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.settings")
def test_set_settings(settings_m):
    my_map = defaultdict(str)
    settings_m.__getitem__ = lambda *x: my_map.__getitem__(x[-1])
    settings_m.__setitem__ = lambda *x: my_map.__setitem__(*x[-2:])
    assert settings_m["key"] != "value"

    runner = CliRunner()
    result = runner.invoke(main, ["settings", "set", "key", "value"])

    assert result.exit_code == 0
    assert result.output == ""

    assert settings_m["key"] == "value"
    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.settings")
def test_show_settings(settings_m):
    my_map = defaultdict(str)
    settings_m.__getitem__ = lambda *x: my_map.__getitem__(x[-1])
    settings_m.__setitem__ = lambda *x: my_map.__setitem__(*x[-2:])
    settings_m["key"] = "<value>"

    runner = CliRunner()
    result = runner.invoke(main, ["settings", "show", "key"])

    assert result.exit_code == 0
    assert result.output == "key: '<value>'\n"

    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.exclude")
def test_exclude_subject(exclude_m):
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "exclude", "987654321"])

    assert result.exit_code == 0
    assert result.output == ""

    exclude_m.assert_called_once_with(987654321)
    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.include")
def test_include_subject(include_m):
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "include", "987654321"])

    assert result.exit_code == 0
    assert result.output == ""

    include_m.assert_called_once_with(987654321)
    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.section_index")
def test_section_index_subject(section_index_m):
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "index", "987654321"])

    assert result.exit_code == 0
    assert "Done. Remember removing alias" in result.output
    assert "987654321" in result.output

    section_index_m.assert_called_once_with(987654321)
    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.un_section_index")
def test_unsection_index_subject(un_section_index_m):
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "unindex", "987654321"])

    assert result.exit_code == 0
    assert "Done. Remember removing alias" in result.output
    assert "987654321" in result.output

    un_section_index_m.assert_called_once_with(987654321)
    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.settings")
def test_show_settings_keys(settings_m):
    new_settings = {"a": 1, "b": 2, "c": 3, "d": 4}
    settings_m.keys.return_value = new_settings.keys()
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "keys"])

    assert result.exit_code == 0
    assert result.output == " - a\n - b\n - c\n - d\n"

    settings_m.keys.assert_called_once_with()
    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.CheckSettings.check")
def test_check_settings(check_m):
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "check"])

    assert result.exit_code == 0
    assert "Checked" in result.output

    check_m.assert_called_once_with()
    universal_mocks.current.assert_called_once_with("settings")
    universal_mocks.setup.assert_not_called()


@mock.patch("vcm.main.main")
def test_cli(main_m):
    cli()
    main_m.assert_called_once_with(prog_name="vcm")

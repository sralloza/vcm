import argparse
from enum import Enum

from vcm.core.settings import (
    SETTINGS_CLASSES,
    NotifySettings,
    exclude,
    include,
    settings_name_to_class,
    settings_to_string,
)
from vcm.core.utils import (
    Printer,
    check_updates,
    more_settings_check,
    safe_exit,
    setup_vcm,
)
from vcm.downloader import download
from vcm.notifier import notify


class Command(Enum):
    notify = 1
    download = 2
    settings = 3
    discover = 4


def parse_args(args=None, parser=False):
    parser = argparse.ArgumentParser(prog="vcm")
    parser.add_argument(
        "-nss", "--no-status-server", action="store_true", help="Disable Status Server"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", dest="version", help="Show version"
    )
    parser.add_argument(
        "--check-updates", action="store_true", help="Check for updates"
    )

    subparsers = parser.add_subparsers(title="commands", dest="command")

    downloader_parser = subparsers.add_parser("download")
    downloader_parser.add_argument("--nthreads", default=20, type=int)
    downloader_parser.add_argument("--no-killer", action="store_true")
    downloader_parser.add_argument("-d", "--debug", action="store_true")
    downloader_parser.add_argument("-q", "--quiet", action="store_true")

    notifier_parser = subparsers.add_parser("notify")
    notifier_parser.add_argument("--nthreads", default=20, type=int)
    notifier_parser.add_argument("--no-icons", action="store_true")

    settings_parser = subparsers.add_parser("settings")
    settings_subparser = settings_parser.add_subparsers(
        title="settings-subcommand", dest="settings_subcommand"
    )
    settings_subparser.required = True

    settings_subparser.add_parser("list")

    set_sub_subparser = settings_subparser.add_parser("set")
    set_sub_subparser.add_argument("key", help="settings key (section.key)")
    set_sub_subparser.add_argument("value", help="new settings value")

    show_sub_subparser = settings_subparser.add_parser("show")
    show_sub_subparser.add_argument("key", help="settings key (section.key)")

    exclude_sub_subparser = settings_subparser.add_parser("exclude")
    exclude_sub_subparser.add_argument(
        "subject_id", help="subject ID to exclude", type=int
    )

    include_sub_subparser = settings_subparser.add_parser("include")
    include_sub_subparser.add_argument(
        "subject_id", help="subject ID to include", type=int
    )

    settings_subparser.add_parser("keys")
    settings_subparser.add_parser("check")

    subparsers.add_parser("discover")

    if parser:
        return parser.parse_args(args), parser

    return parser.parse_args(args)


@safe_exit
def main(args=None):
    opt, parser = parse_args(args, parser=True)

    if opt.version:
        from vcm import version

        exit("Version: %s" % version)

    if opt.check_updates:
        check_updates()
        exit()

    try:
        opt.command = Command(opt.command)
    except ValueError:
        try:
            opt.command = Command[opt.command]
        except KeyError:
            return parser.error("Invalid use: use download or notify")

    if opt.command == Command.download and opt.quiet:
        Printer.silence()

    if opt.command == Command.settings:
        if opt.settings_subcommand == "list":
            print(settings_to_string())
            exit()

        if opt.settings_subcommand == "check":
            more_settings_check()
            exit("Checked")

        if opt.settings_subcommand == "exclude":
            exclude(opt.subject_id)
            exit()

        if opt.settings_subcommand == "include":
            include(opt.subject_id)
            exit()

        if opt.settings_subcommand == "keys":
            keys = []
            for setting_class in SETTINGS_CLASSES:
                for key in settings_name_to_class[setting_class].keys():
                    keys.append(" - " + setting_class + "." + key)

            for key in keys:
                print(key)
            exit()

        if opt.key.count(".") != 1:
            return parser.error("Invalid key (must be section.setting)")

        # Now command can be show or set, both need to split the key
        cls, key = opt.key.split(".")

        try:
            settings_class = settings_name_to_class[cls]
        except KeyError:
            return parser.error(
                "Invalid setting class: %r (valids are %r)" % (cls, SETTINGS_CLASSES)
            )

        if key not in settings_class:
            message = "%r is not a valid %s setting (valids are %r)" % (
                key,
                cls,
                list(settings_class.keys()),
            )
            parser.error(message)

        if opt.settings_subcommand == "set":
            setattr(settings_class, key, opt.value)
        elif opt.settings_subcommand == "show":
            print("%s: %r" % (opt.key, getattr(settings_class, key)))
        exit()

    # Command executed is not 'settings', so check settings
    setup_vcm()

    if opt.command == Command.discover:
        Printer.silence()
        return download(
            nthreads=1, no_killer=True, status_server=False, discover_only=True
        )
    elif opt.command == Command.download:
        if opt.debug:
            import webbrowser

            chrome_path = (
                "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
            )
            webbrowser.get(chrome_path).open_new("localhost")

        return download(
            nthreads=opt.nthreads,
            no_killer=opt.no_killer,
            status_server=not opt.no_status_server,
        )

    elif opt.command == Command.notify:
        return notify(
            send_to=NotifySettings.email,
            use_icons=not opt.no_icons,
            nthreads=opt.nthreads,
            status_server=not opt.no_status_server,
        )
    else:
        return parser.error("Invalid command: %r" % opt.command)

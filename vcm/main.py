import argparse
from enum import Enum
import time

from vcm.core.settings import (
    SETTINGS_CLASSES,
    NotifySettings,
    settings_name_to_class,
    settings_to_string,
)
from vcm.core.utils import (
    is_called_from_shell,
    more_settings_check,
    setup_vcm,
    create_desktop_cmds,
)
from vcm.downloader import download
from vcm.notifier import notify


class Command(Enum):
    notify = 1
    download = 2
    settings = 3


def main(args=None):
    parser = argparse.ArgumentParser(prog="vcm")
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

    settings_subparser.add_parser("check")

    opt = parser.parse_args(args)

    try:
        opt.command = Command(opt.command)
    except ValueError:
        try:
            opt.command = Command[opt.command]
        except KeyError:
            if not is_called_from_shell():
                create_desktop_cmds()
                print("Created desktop cmds")
                time.sleep(10)
                return
            return parser.error("Invalid use: use download or notify")

    if opt.command == Command.settings:
        if opt.settings_subcommand == "list":
            print(settings_to_string())
            exit()

        if opt.settings_subcommand == "check":
            more_settings_check()
            exit("Checked")

        if opt.key.count(".") != 1:
            return parser.error("Invalid key (must be section.setting)")

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

        setattr(settings_class, key, opt.value)
        exit()

    # Command executed is not 'settings', so check settings
    setup_vcm()

    if opt.command == Command.download:
        if opt.debug:
            import webbrowser

            chrome_path = (
                "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
            )
            webbrowser.get(chrome_path).open_new("localhost")

        return download(nthreads=opt.nthreads, no_killer=opt.no_killer, quiet=opt.quiet)

    elif opt.command == Command.notify:
        return notify(NotifySettings.email, not opt.no_icons, nthreads=opt.nthreads)
    else:
        return parser.error("Invalid command: %r" % opt.command)

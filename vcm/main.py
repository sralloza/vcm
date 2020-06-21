from argparse import ArgumentParser, Namespace
from enum import Enum
import logging
from typing import NoReturn, Tuple

from . import __version__ as version
from .core.settings import (
    GeneralSettings,
    NotifySettings,
    SETTINGS_CLASSES,
    exclude,
    include,
    section_index,
    settings_name_to_class,
    settings_to_string,
    un_section_index,
)
from .core.utils import (
    Printer,
    check_updates,
    more_settings_check,
    open_http_status_server,
    safe_exit,
    setup_vcm,
)
from .downloader import download
from .notifier import notify

logger = logging.getLogger(__name__)
parser: ArgumentParser


class Command(Enum):
    notify = 1
    download = 2
    settings = 3
    discover = 4
    version = 5

    def to_str(self):
        return self.name


def show_version():
    print("Version: %s" % version)


def parser_error(msg) -> NoReturn:
    global parser
    parser.error(msg)


def parse_args(args=None):
    """Parses command line args.

    Args:
        args (List[str], optional): list of argument to parse instead of
            sys.argv[1:]. Defaults to None.

    Returns:
        Namespace: namespace containing the arguments parsed.
    """

    global parser
    parser = ArgumentParser(prog="vcm")
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

    section_index_subparser = settings_subparser.add_parser("index")
    section_index_subparser.add_argument("subject_id", type=int)

    un_section_index_subparser = settings_subparser.add_parser("unindex")
    un_section_index_subparser.add_argument("subject_id", type=int)

    settings_subparser.add_parser("keys")
    settings_subparser.add_parser("check")

    subparsers.add_parser("discover")
    subparsers.add_parser("version")

    return parser.parse_args(args)


@safe_exit
def main(args=None):
    """Main function."""

    opt = parse_args(args)

    if opt.version:
        show_version()
        return

    if opt.check_updates:
        check_updates()
        return

    try:
        opt.command = Command(opt.command)
    except ValueError:
        try:
            opt.command = Command[opt.command]
        except KeyError:
            commands = list(Command)
            commands.sort(key=lambda x: x.name)
            commands = ", ".join([x.to_str() for x in commands])
            return parser.error(
                "Invalid command (%r). Valid commands: %s" % (opt.command, commands)
            )

    if opt.command == Command.version:
        show_version()
        return

    if opt.command == Command.download and opt.quiet:
        Printer.silence()

    if opt.command == Command.settings:
        if opt.settings_subcommand == "list":
            print(settings_to_string())
            return

        if opt.settings_subcommand == "check":
            more_settings_check()
            print("Checked")
            return

        if opt.settings_subcommand == "exclude":
            exclude(opt.subject_id)
            return

        if opt.settings_subcommand == "include":
            include(opt.subject_id)
            return

        if opt.settings_subcommand == "index":
            section_index(opt.subject_id)
            Printer.print(
                "Done. Remember removing alias entries for subject with id=%d."
                % opt.subject_id
            )
            return

        if opt.settings_subcommand == "unindex":
            un_section_index(opt.subject_id)
            Printer.print(
                "Done. Remember removing alias entries for subject with id=%d."
                % opt.subject_id
            )
            return

        if opt.settings_subcommand == "keys":
            keys = []
            for setting_class in SETTINGS_CLASSES:
                for key in settings_name_to_class[setting_class].keys():
                    keys.append(" - " + setting_class + "." + key)

            for key in keys:
                print(key)
            return

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
        return

    # Command executed is not 'settings', so check settings
    setup_vcm()
    logger.info("vcm version: %s", version)

    if opt.command == Command.discover:
        Printer.silence()
        return download(
            nthreads=1, no_killer=True, status_server=False, discover_only=True
        )
    if opt.command == Command.download:
        if opt.debug:
            open_http_status_server()

        return download(
            nthreads=opt.nthreads,
            no_killer=opt.no_killer,
            status_server=not opt.no_status_server,
        )

    if opt.command == Command.notify:
        return notify(
            send_to=NotifySettings.email,
            use_icons=not opt.no_icons,
            nthreads=opt.nthreads,
            status_server=not opt.no_status_server,
        )

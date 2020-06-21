from argparse import ArgumentParser, Namespace
from enum import Enum
import logging
from typing import NoReturn, Tuple

from . import __version__ as version
from .core.settings import (
    BaseSettings,
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


def get_command(command):

    try:
        real_command = Command(command)
    except ValueError:
        try:
            real_command = Command[command]
        except KeyError:
            commands = list(Command)
            commands.sort(key=lambda x: x.name)
            commands = ", ".join([x.to_str() for x in commands])
            parser_error(
                "Invalid command (%r). Valid commands: %s" % (command, commands)
            )
    return real_command


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

    command = get_command(opt.command)

    if command == Command.version:
        show_version()
        return

    if command == Command.download and opt.quiet:
        Printer.silence()

    if command == Command.settings:
        return settings_subcommand(opt)

    # Command executed is not 'settings', so check settings
    setup_vcm()
    logger.info("vcm version: %s", version)

    if command == Command.discover:
        Printer.silence()
        return download(
            nthreads=1, no_killer=True, status_server=False, discover_only=True
        )
    if command == Command.download:
        if opt.debug:
            open_http_status_server()

        return download(
            nthreads=opt.nthreads,
            no_killer=opt.no_killer,
            status_server=not opt.no_status_server,
        )

    if command == Command.notify:
        return notify(
            send_to=NotifySettings.email,
            use_icons=not opt.no_icons,
            nthreads=opt.nthreads,
            status_server=not opt.no_status_server,
        )


class SettingsSubcommand:
    opt = None

    @classmethod
    def execute(cls, opt):
        cls.opt = opt
        return getattr(cls, opt.settings_subcommand)()

    @classmethod
    def list(cls):
        print(settings_to_string())

    @classmethod
    def check(cls):
        more_settings_check()
        print("Checked")

    @classmethod
    def exclude(cls):
        exclude(cls.opt.subject_id)

    @classmethod
    def include(cls):
        include(cls.opt.subject_id)

    @classmethod
    def index(cls):
        section_index(cls.opt.subject_id)
        Printer.print(
            "Done. Remember removing alias entries for subject with id=%d."
            % cls.opt.subject_id
        )

    @classmethod
    def un_index(cls):
        un_section_index(cls.opt.subject_id)
        Printer.print(
            "Done. Remember removing alias entries for subject with id=%d."
            % cls.opt.subject_id
        )

    @classmethod
    def keys(cls):
        keys = []
        for setting_class in SETTINGS_CLASSES:
            for key in settings_name_to_class[setting_class].keys():
                keys.append(" - " + setting_class + "." + key)

        for key in keys:
            print(key)


def parse_settings_key(opt) -> Tuple[BaseSettings, str]:
    if opt.key.count(".") != 1:
        return parser_error("Invalid key (must be section.setting)")

    # Now command can be show or set, both need to split the key
    cls, key = opt.key.split(".")

    try:
        settings_class = settings_name_to_class[cls]
    except KeyError:
        return parser_error(
            "Invalid setting class: %r (valids are %r)" % (cls, SETTINGS_CLASSES)
        )

    if key not in settings_class:
        message = "%r is not a valid %s setting (valids are %r)" % (
            key,
            cls,
            list(settings_class.keys()),
        )
        parser_error(message)
    return settings_class, key


def settings_subcommand(opt: Namespace):
    try:
        return SettingsSubcommand.execute(opt)
    except AttributeError:
        pass

    settings_class, key = parse_settings_key(opt)

    if opt.settings_subcommand == "set":
        setattr(settings_class, key, opt.value)
    elif opt.settings_subcommand == "show":
        print("%s: %r" % (opt.key, getattr(settings_class, key)))

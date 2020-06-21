"""Main module, controls the execution."""

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

parser: ArgumentParser  # pylint: disable=C0103


class Command(Enum):
    """Represents valid CLI commands."""

    notify = 1
    download = 2
    settings = 3
    discover = 4
    version = 5

    def to_str(self) -> str:
        """Returns the name of the command."""
        return self.name


def parse_args(args=None):
    """Parses command line args.

    Args:
        args (List[str], optional): list of argument to parse instead of
            sys.argv[1:]. Defaults to None.

    Returns:
        Namespace: namespace containing the arguments parsed.
    """

    global parser  # pylint: disable=W0603,C0103
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


def parser_error(msg) -> NoReturn:
    """Raises an error using ArgumentParser.error.

    Args:
        msg (str): error message.
    """

    global parser  # pylint: disable=W0603,C0103
    parser.error(msg)


def get_command(command) -> Command:
    """Returns the instance of Command class.

    Args:
        command (str): command as a string.

    Returns:
        Command: Command as an enumeration.
    """

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


def show_version():
    """Prints the current version."""
    print("Version: %s" % version)


def execute_discover(opt):  # pylint: disable=W0613
    """Executes command `discover`.

    Args:
        opt (Namespace): namespace returned by parser.
    """

    Printer.silence()
    return download(nthreads=1, no_killer=True, status_server=False, discover_only=True)


def execute_download(opt):
    """Executes command `download`.

    Args:
        opt (Namespace): namespace returned by parser.
    """

    if opt.debug:
        open_http_status_server()

    return download(
        nthreads=opt.nthreads,
        no_killer=opt.no_killer,
        status_server=not opt.no_status_server,
    )


def execute_notify(opt):
    """Executes command `notify`.

    Args:
        opt (Namespace): namespace returned by parser.
    """

    return notify(
        send_to=NotifySettings.email,
        use_icons=not opt.no_icons,
        nthreads=opt.nthreads,
        status_server=not opt.no_status_server,
    )


class SettingsSubcommand:
    """Wrapper for settings subcommands."""

    opt = None

    @classmethod
    def execute(cls, opt):
        """Executes a settings subcommand that doesn't alter settings.

        Args:
            opt (Namespace): namespace returned by parser.
        """

        cls.opt = opt
        return getattr(cls, opt.settings_subcommand)()

    @classmethod
    def list(cls):
        """Print settings keys and values."""
        print(settings_to_string())

    @classmethod
    def check(cls):
        """Forces checks of settings."""
        more_settings_check()
        print("Checked")

    @classmethod
    def exclude(cls):
        """Excludes a subject from parsing given its id."""
        exclude(cls.opt.subject_id)

    @classmethod
    def include(cls):
        """Includes a subject in parsing given its id."""
        include(cls.opt.subject_id)

    @classmethod
    def index(cls):
        """Makes a subject use section indexing given its id."""
        section_index(cls.opt.subject_id)
        Printer.print(
            "Done. Remember removing alias entries for subject with id=%d."
            % cls.opt.subject_id
        )

    @classmethod
    def un_index(cls):
        """Makes a subject not use section indexing given its id."""
        un_section_index(cls.opt.subject_id)
        Printer.print(
            "Done. Remember removing alias entries for subject with id=%d."
            % cls.opt.subject_id
        )

    @classmethod
    def keys(cls):
        """Prints the settings keys."""
        keys = []
        for setting_class in SETTINGS_CLASSES:
            for key in settings_name_to_class[setting_class].keys():
                keys.append(" - " + setting_class + "." + key)

        for key in keys:
            print(key)


def parse_settings_key(opt) -> Tuple[BaseSettings, str]:
    """Validates a settings key and splits it into the settings class and the key itself.

    Args:
        opt (Namespace): namespace returned by parser.

    Returns:
        Tuple[BaseSettings, str]: settings class and key.
    """

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


def execute_settings(opt: Namespace):
    """Executes command `settings`.

    Args:
        opt (Namespace): namespace returned by parser.
    """

    try:
        return SettingsSubcommand.execute(opt)
    except AttributeError:
        pass

    settings_class, key = parse_settings_key(opt)

    if opt.settings_subcommand == "set":
        setattr(settings_class, key, opt.value)
    elif opt.settings_subcommand == "show":
        print("%s: %r" % (opt.key, getattr(settings_class, key)))


@safe_exit
def main(args=None):
    """Main function."""

    logger = logging.getLogger(__name__)
    opt = parse_args(args)

    # Keyword arguments that make program exit
    if opt.version:
        return show_version()

    if opt.check_updates:
        return check_updates()

    # Commands
    command = get_command(opt.command)

    if command == Command.download and opt.quiet:
        Printer.silence()

    # Command executed is not 'settings', so check settings
    setup_vcm()
    logger.info("vcm version: %s", version)

    return instructions[command.to_str()](opt)


instructions = {
    "version": show_version,
    "settings": execute_settings,
    "discover": execute_discover,
    "download": execute_download,
    "notify": execute_notify,
}

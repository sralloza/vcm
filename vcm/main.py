"""Main module, controls the execution."""

from argparse import ArgumentParser, Namespace
from enum import Enum
import logging
from typing import NoReturn, Tuple

from vcm.core.modules import Modules

from . import __version__ as version
from .core.settings import (
    CheckSettings, exclude,
    include,
    section_index,
    settings,
    settings_to_string,
    un_section_index,
)
from .core.utils import (
    Printer,
    check_updates,
    open_http_status_server,
    safe_exit,
    setup_vcm,
)
from .downloader import download
from .notifier import notify


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


class Parser:
    """Wrapper for `argparse.ArgumentParser`."""

    _parser = None

    @classmethod
    def init_parser(cls):
        """Creates the parser."""

        cls._parser = ArgumentParser(prog="vcm")
        cls._parser.add_argument(
            "-nss",
            "--no-status-server",
            action="store_true",
            help="Disable Status Server",
        )
        cls._parser.add_argument(
            "-v", "--version", action="store_true", dest="version", help="Show version"
        )
        cls._parser.add_argument(
            "--check-updates", action="store_true", help="Check for updates"
        )

        subparsers = cls._parser.add_subparsers(title="commands", dest="command")

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

    @classmethod
    def parse_args(cls) -> Namespace:
        """Parses command line args.

        Returns:
            Namespace: namespace containing the arguments parsed.
        """
        if not cls._parser:
            cls.init_parser()
        return cls._parser.parse_args()

    @classmethod
    def error(cls, msg) -> NoReturn:
        """Raises an error using ArgumentParser.error.

        Args:
            msg (str): error message.
        """

        cls._parser.error(msg)


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
            Parser.error(
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
    return download(nthreads=1, killer=False, status_server=False, discover_only=True)


def execute_download(opt):
    """Executes command `download`.

    Args:
        opt (Namespace): namespace returned by parser.
    """

    if opt.debug:
        open_http_status_server()

    return download(
        nthreads=opt.nthreads,
        killer=not opt.no_killer,
        status_server=not opt.no_status_server,
    )


def execute_notify(opt):
    """Executes command `notify`.

    Args:
        opt (Namespace): namespace returned by parser.
    """

    return notify(
        send_to=settings.email,
        use_icons=not opt.no_icons,
        nthreads=opt.nthreads,
        status_server=not opt.no_status_server,
    )


class NonKeyBasedSettingsSubcommand:
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
        CheckSettings.check()
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
        for key in settings.keys():
            print(" - " + key)


def execute_settings(opt: Namespace):
    """Executes command `settings`.

    Args:
        opt (Namespace): namespace returned by parser.
    """

    try:
        # Try to execute settings command without the key
        return NonKeyBasedSettingsSubcommand.execute(opt)
    except AttributeError:
        pass

    # Setting command needs the key

    if opt.settings_subcommand == "set":
        setattr(settings, opt.key, opt.value)
    if opt.settings_subcommand == "show":
        print("%s: %r" % (opt.key, getattr(settings, opt.key)))


@safe_exit
def main():
    """Main function."""

    logger = logging.getLogger(__name__)
    opt = Parser.parse_args()

    # Keyword arguments that make program exit
    if opt.version:
        return show_version()

    if opt.check_updates:
        return check_updates()

    # Commands
    command = get_command(opt.command)
    Modules.set_current(command.name)

    if command == Command.download and opt.quiet:
        Printer.silence()

    if command != Command.settings:
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

"""Main module, controls the execution."""

import logging

import click

from . import __version__ as version
from .core.modules import Modules
from .core.utils import (
    Printer,
    check_updates,
    open_http_status_server,
    safe_exit,
    setup_vcm,
)
from .downloader import download
from .notifier import notify
from .settings import (
    CheckSettings,
    exclude,
    include,
    section_index,
    settings,
    settings_to_string,
    un_section_index,
)

logger = logging.getLogger(__name__)
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=version, prog_name="vcm")
@click.option("-nss", "--no-status-server", is_flag=True, help="Disable status server")
@click.pass_context
def main(ctx, no_status_server):
    """Virtual Campus Manager"""
    command = ctx.invoked_subcommand

    try:
        Modules.set_current(command)
    except ValueError:
        pass

    if command != "settings":
        # Command executed is not 'settings', so check settings
        setup_vcm()
        logger.info("vcm version: %s", version)


@main.command("check-updates", help="Check for updates")
def check_updates_command():
    """Check for new releases"""
    check_updates()


@main.command("download")
@click.option("--nthreads", default=20, type=int)
@click.option("--no-killer", is_flag=True)
@click.option("-d", "--debug", is_flag=True)
@click.option("-q", "--quiet", is_flag=True)
@click.pass_context
def download_command(ctx, nthreads, no_killer, debug, quiet):
    """Download all files found in the virtual campus"""
    no_status_server = ctx.parent.params["no_status_server"]
    if debug:
        open_http_status_server()

    if quiet:
        Printer.silence()

    return download(
        nthreads=nthreads, killer=not no_killer, status_server=not no_status_server,
    )


@main.command("notify",)
@click.option("--nthreads", default=20, type=int)
@click.option("--no-icons", is_flag=True)
@click.pass_context
def notify_command(ctx, nthreads, no_icons):
    """Sends an email with all the new files of the virtual campus"""
    no_status_server = ctx.parent.params["no_status_server"]

    return notify(
        send_to=settings.email,
        use_icons=not no_icons,
        nthreads=nthreads,
        status_server=not no_status_server,
    )


@main.command("discover")
def discover():
    """Only parse the subject names"""
    Printer.silence()
    return download(nthreads=1, killer=False, status_server=False, discover_only=True)


@main.group("settings")
def settings_command():
    """Manage settings"""


@settings_command.command("list")
def list_settings():
    """List settings keys and values"""
    click.echo(settings_to_string())


@settings_command.command("set")
@click.argument("key")
@click.argument("value")
def set_settings(key, value):
    """Set a new value for a specific setting"""
    settings[key] = value


@settings_command.command("show")
@click.argument("key")
def show_settings(key):
    """Show the value of a specific setting"""
    click.echo("%s: %r" % (key, settings[key]))


@settings_command.command("exclude")
@click.argument("subject_id", type=int)
def exclude_subject(subject_id):
    """Exclude a subject from parsing given its id"""
    exclude(subject_id)


@settings_command.command("include")
@click.argument("subject_id", type=int)
def include_subject(subject_id):
    """Includes a subject in the parsing given its id"""
    include(subject_id)


@settings_command.command("index")
@click.argument("subject_id", type=int)
def index_subject(subject_id):
    """Start using the subject's session to name files"""
    section_index(subject_id)
    click.echo(
        "Done. Remember removing alias entries for subject with id=%d." % subject_id
    )


@settings_command.command("unindex")
@click.argument("subject_id", type=int)
def unindex_subject(subject_id):
    """Stop using the subject's session to name files"""
    un_section_index(subject_id)
    click.echo(
        "Done. Remember removing alias entries for subject with id=%d." % subject_id
    )


@settings_command.command("keys")
def show_settings_keys():
    """Displays the settings keys, but not the values"""
    for key in settings.keys():
        click.echo(" - " + key)


@settings_command.command("check")
def check_settings():
    """Checks the validity of the settings"""
    CheckSettings.check()
    click.secho("Checked", fg="green", bold=True)


def cli():
    return main(prog_name="vcm")

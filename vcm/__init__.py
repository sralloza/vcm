"""File downloader for the Virtual Campus of the Valladolid Unversity."""
from pathlib import Path

from .core.settings import GeneralSettings

__all__ = []


def get_version():
    """Returns the current version.

    Returns:
        str: current version.
    """

    version_path = Path(__file__).with_name("VERSION")
    return version_path.read_text().strip()


__version__ = get_version()

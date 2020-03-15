"""File downloader for the Virtual Campus of the Valladolid Unversity."""


__all__ = []


def get_version():
    from pathlib import Path

    version_path = Path(__file__).with_name("VERSION")
    return version_path.read_text()


version = get_version()

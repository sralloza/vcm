"""File scanner to control file version."""
import os
from pathlib import Path

from vcm.core.exceptions import FileCacheError
from vcm.core.settings import GeneralSettings


class FileCache:
    """File scanner to control file version."""

    path = GeneralSettings.root_folder

    def __init__(self):
        self.cache = {}

    def __contains__(self, item):
        if not isinstance(item, Path):
            raise TypeError(
                "FileCache.__contains__ must be used with Path, not %r"
                % type(item).__name__
            )
        return item in self.cache.keys()

    def __getitem__(self, item):
        if not isinstance(item, Path):
            raise TypeError(
                "FileCache.__getitem__ must be used with Path, not %r"
                % type(item).__name__
            )
        return self.cache[item]

    def __setitem__(self, key, value):
        if not isinstance(key, Path):
            raise TypeError(
                "FileCache.__setitem__'s key must be Path, not %r"
                % type(key).__name__
            )

        if not isinstance(value, int):
            raise TypeError(
                "FileCache.__setitem__'s value must be int, not %r"
                % type(value).__name__
            )

        self.cache[key] = value

    def __len__(self):
        return len(self.cache)

    def load(self, _auto=False):
        """Starts the scanner."""

        if not _auto:
            raise FileCacheError("Use REAL_FILE_CACHE instead")

        filenames = []
        for elem in os.walk(self.path.as_posix()):
            folder = elem[0]
            files = elem[2]

            for file in files:
                filenames.append(Path(folder) / file)

        for file in filenames:
            self._get_file_length(file)

    def _get_file_length(self, file):
        """Gets the file content length."""
        with file.open("rb") as file_handler:
            length = len(file_handler.read())

        self[file] = length


REAL_FILE_CACHE = FileCache()
REAL_FILE_CACHE.load(_auto=True)

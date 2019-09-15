"""File scanner to control file version."""
import os

from vcm.core.exceptions import FileCacheError
from vcm.core.options import Options


class FileCache:
    """File scanner to control file version."""
    path = Options.ROOT_FOLDER

    def __init__(self):
        self.cache = {}

    def __contains__(self, item):
        return item in self.cache.keys()

    def __getitem__(self, item):
        return self.cache[item]

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __len__(self):
        return len(self.cache)

    def load(self, _auto=False):
        """Starts the scanner."""

        if not _auto:
            raise FileCacheError('Use REAL_FILE_CACHE instead')

        filenames = []
        for elem in os.walk(self.path.as_posix()):
            folder = elem[0]
            files = elem[2]

            for file in files:
                filenames.append(os.path.normpath(os.path.join(folder, file)))

        for file in filenames:
            self._get_file_length(file)

    def _get_file_length(self, file):
        """Gets the file content length."""
        with open(file, 'rb') as file_handler:
            length = len(file_handler.read())

        self.cache[file] = length


REAL_FILE_CACHE = FileCache()
REAL_FILE_CACHE.load(_auto=True)

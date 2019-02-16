"""File scanner to control file version."""
import os

from vcd.globals import ROOT_FOLDER


class FileCache:
    """File scanner to control file version."""
    def __init__(self):
        self.path = ROOT_FOLDER
        self.cache = {}

    def __contains__(self, item):
        return item in self.cache.keys()

    def __getitem__(self, item):
        return self.cache[item]

    def __setitem__(self, key, value):
        self.cache[key] = value

    def load(self):
        """Starts the scanner."""
        filenames = []
        for elem in os.walk(self.path):
            folder = elem[0]
            files = elem[2]

            for file in files:
                filenames.append(os.path.join(folder, file).replace('\\', '/'))

        for file in filenames:
            self._get_file_length(file)

    def _get_file_length(self, file):
        """Gets the file content length."""
        with open(file, 'rb') as file_handler:
            length = len(file_handler.read())

        self.cache[file] = length


REAL_FILE_CACHE = FileCache()
REAL_FILE_CACHE.load()

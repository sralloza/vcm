import os
import re


class Options:
    PRODUCTION = False
    FILENAME_PATTERN = re.compile('filename=\"?([\w. ]*)\"?')
    ROOT_FOLDER = 'D:/sistema/desktop/virtual_ittade3'
    TIMEOUT = 30

    @staticmethod
    def create_root_folder():
        if os.path.isdir(Options.ROOT_FOLDER) is False:
            os.mkdir(Options.ROOT_FOLDER)

    @staticmethod
    def set_root_folder(root_folder):
        Options.ROOT_FOLDER = root_folder
        Options.create_root_folder()

    @staticmethod
    def set_timeout(timeout:int):
        if not isinstance(timeout, int):
            raise TypeError(f'Timeout must be int, not {type(timeout).__name__}')

        Options.TIMEOUT = timeout


Options.create_root_folder()

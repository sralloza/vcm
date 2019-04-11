import os
import re


class Options:
    PRODUCTION = False
    FILENAME_PATTERN = re.compile('filename="(.*)"')
    ROOT_FOLDER = 'D:/sistema/desktop/virtual_ittade3'

    @staticmethod
    def set_root_folder(root_folder):
        Options.ROOT_FOLDER = root_folder
        if os.path.isdir(Options.ROOT_FOLDER) is False:
            os.mkdir(Options.ROOT_FOLDER)

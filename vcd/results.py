"""Print real-time alerts."""
import os
from threading import Lock

from colorama import Fore

from .options import Options


class Results:
    """Class to manage information."""
    print_lock = Lock()

    file_lock = Lock()
    result_path = os.path.join(Options.ROOT_FOLDER, 'new-files.txt').replace('\\', '/')

    @staticmethod
    def print_updated(message):
        """Prints an updated message (yellow) thread-safely.

        Args:
            message (str): message to print

        """
        with Results.print_lock:
            print(Fore.LIGHTYELLOW_EX + message)

        Results.add_to_result_file(message)

    @staticmethod
    def print_new(message):
        """Prints an new message (green) thread-safely.

        Args:
            message (str): message to print

        """
        with Results.print_lock:
            print(repr(Fore.LIGHTGREEN_EX + message))

        Results.add_to_result_file(message)

    @staticmethod
    def add_to_result_file(message):
        """Writes a message in the new-files file.

        Args:
            message (str): message to write in the new-files file.

        """
        with Results.file_lock:
            with open(Results.result_path, 'at') as f:
                f.write(message + '\n')

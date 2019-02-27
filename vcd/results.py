"""Print real-time alerts."""
import os
from threading import Lock

from colorama import Fore

from .options import Options


class Results:
    """Class to manage information."""
    list_lock = Lock()

    print_lock = Lock()
    print_list = []

    file_lock = Lock()
    result_path = os.path.join(Options.ROOT_FOLDER, 'new-files.txt').replace('\\', '/')

    @staticmethod
    def add(value):
        """Adds anything to the print list."""
        with Results.list_lock:
            Results.print_list.append(value)

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
            print(Fore.LIGHTGREEN_EX + message)

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

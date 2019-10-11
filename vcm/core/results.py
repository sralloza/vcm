"""Print real-time alerts."""
from threading import Lock

from colorama import Fore

from .options import Options


class Results:
    """Class to manage information."""
    print_lock = Lock()

    file_lock = Lock()
    result_path = Options.ROOT_FOLDER / 'new-files.txt'

    @staticmethod
    def print_updated(message):
        """Prints an updated message (yellow) thread-safely.

        Args:
            message (str): message to print

        """
        with Results.print_lock:
            print(Fore.LIGHTYELLOW_EX + message + Fore.RESET)

        Results.add_to_result_file(message)

    @staticmethod
    def print_new(message):
        """Prints an new message (green) thread-safely.

        Args:
            message (str): message to print

        """
        with Results.print_lock:
            print(Fore.LIGHTGREEN_EX + message + Fore.RESET)

        Results.add_to_result_file(message)

    @staticmethod
    def add_to_result_file(message):
        """Writes a message in the new-files file.

        Args:
            message (str): message to write in the new-files file.

        """
        with Results.file_lock:
            with Results.result_path.open("at", encoding="utf-8") as f:
                f.write(message + "\n")

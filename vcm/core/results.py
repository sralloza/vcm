"""Print real-time alerts."""
from threading import Lock

from colorama import Fore

from .settings import GeneralSettings


class Counters:
    updated = 0
    new = 0

    @classmethod
    def count_updated(cls):
        cls.updated += 1

    @classmethod
    def count_new(cls):
        cls.new += 1


class Results:
    """Class to manage information."""

    print_lock = Lock()

    file_lock = Lock()
    result_path = GeneralSettings.root_folder / "new-files.txt"

    @staticmethod
    def print_updated(filepath):
        """Prints an updated message (yellow) thread-safely."""
        Counters.count_updated()
        message = "File updated no. %3d: %s" % (Counters.updated, filepath)
        with Results.print_lock:
            print(Fore.LIGHTYELLOW_EX + message + Fore.RESET)

        Results.add_to_result_file(message)

    @staticmethod
    def print_new(filepath):
        """Prints an new message (green) thread-safely."""
        Counters.count_new()
        message = "New file no. %3d: %s" % (Counters.new, filepath)
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

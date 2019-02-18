"""Print real-time alerts."""

from threading import Lock

from colorama import Fore


class Results:
    """Class to manage information."""
    list_lock = Lock()
    print_lock = Lock()
    print_list = []

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

    @staticmethod
    def print_new(message):
        """Prints an new message (green) thread-safely.

        Args:
            message (str): message to print

        """
        with Results.print_lock:
            print(Fore.LIGHTGREEN_EX + message)

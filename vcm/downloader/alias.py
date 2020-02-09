"""Alias manager for signatures."""
import json
from dataclasses import dataclass
from hashlib import sha1
from threading import Semaphore

from vcm.core.exceptions import AliasFatalError, AliasNotFoundError, IdError
from vcm.core.settings import GeneralSettings
from vcm.core.utils import Singleton


def calculate_hash(byte_data):
    if isinstance(byte_data, str):
        byte_data = byte_data.encode()
    return sha1(byte_data).hexdigest()


class Events:
    """Contains events to control the multithreading version of Alias."""

    access = Semaphore()

    @classmethod
    def acquire(cls):
        cls.access.acquire()

    @classmethod
    def release(cls):
        cls.access.release()


@dataclass
class AliasEntry:
    id: str
    original: str
    alias: str

    def to_json(self):
        return {"id": self.id, "original": self.original, "alias": self.alias}


class Alias(metaclass=Singleton):
    """Class designed to declare aliases"""

    def __init__(self):
        self.alias_path = GeneralSettings.root_folder / "alias.json"
        self.json = []
        self.load()

    def __len__(self):
        return len(self.json)

    def load(self):
        """Loads the alias configuration."""

        if not self.alias_path.exists():
            self.json = []
            return
        try:
            Events.acquire()
            with self.alias_path.open(encoding="utf-8") as file_handler:
                self.json = json.load(file_handler) or []
        except json.JSONDecodeError as ex:
            raise AliasFatalError("Raised JSONDecodeError") from ex
        except UnicodeDecodeError as ex:
            raise AliasFatalError("Raised UnicodeDecodeError") from ex

        if not isinstance(self.json, list):
            raise TypeError(f"alias file invalid ({type(self.json).__name__})")

        for alias in self.json:
            if "id" not in alias or "alias" not in alias or "original" not in alias:
                raise TypeError(f"alias file invalid: {alias!r}")

        self.json = [AliasEntry(**x) for x in self.json]

        Events.release()

    @classmethod
    def destroy(cls):
        """Destroys the alias database."""

        self = cls()
        Events.acquire()

        self.json = []
        with self.alias_path.open("wt", encoding="utf-8") as file_handler:
            json.dump([], file_handler, indent=4, sort_keys=True, ensure_ascii=False)

        Events.release()
        return

    def save(self):
        """Saves alias configuration to the file."""
        try:
            with self.alias_path.open(encoding="utf-8") as file_handler:
                temp = json.load(file_handler) or []
        except (FileNotFoundError, json.JSONDecodeError):
            temp = []

        to_write = [x.json() for x in self.json]
        to_write += temp

        res_list = []
        for i, _ in enumerate(to_write):
            if to_write[i] not in to_write[i + 1 :]:
                res_list.append(to_write[i])

        with self.alias_path.open("wt", encoding="utf-8") as file_handler:
            json.dump(
                res_list, file_handler, indent=4, sort_keys=True, ensure_ascii=False
            )

    def _increment(self, something):
        """Changes the filename if it already exists in the database.

        Examples:
            Alias._increment("file") -> "file.1"
            Alias._increment("file.txt") -> "file.1.txt"
            Alias._increment("some.file.txt") -> "some.file.1.txt"

        """
        index = 0
        while True:
            index += 1
            temp = self._create_name(something, index)

            done = True
            for file in self.json:
                if temp == file.alias:
                    done = False
                    break

            if done:
                return temp

    @classmethod
    def _create_name(cls, template: str, index: int):
        """Given a filename and an index, creates the filename.

        Examples
            Alias._createname("file", 5) -> "file.5"
            Alias._createname("file.txt", 5) -> "file.5.txt"
            Alias._createname("some.file.txt", 5) -> "some.file.5.txt"
        """

        splitted = template.split(".")
        if len(splitted) == 1:
            return f"{splitted[0]}.{index}"
        elif len(splitted) == 2:
            return f"{splitted[0]}.{index}.{splitted[1]}"
        else:
            return f'{".".join(splitted[:-1])}.{index}.{splitted[-1]}'

    @classmethod
    def original_to_alias(cls, id_, original, folder_id=None):
        """Returns the alias given the original name.

        Args:
            id_ (str | int): id.
            original (str): original name.

        Returns:
            str: the alias if the original name is found in the alias database. If it
                is not found, the original name will be returned.

        """

        is_folder = id_ == "744efab6c9423088e7f5c0bc83f9e7b92c604309"

        if is_folder:
            id_ = calculate_hash(original + str(folder_id))

        self = Alias.__new__(Alias)
        self.__init__()
        Events.acquire()

        for file in self.json:
            if file.id == id_:
                Events.release()

                if file.original == original:
                    return file.alias

                raise IdError(
                    f"Same id, different names ({file.id}, {file.alias}, {original})"
                )

        alias = original

        for file in self.json:
            if file.original == original:
                alias = self._increment(alias)
                break

        self.json.append(AliasEntry(id_, original, alias))
        self.save()

        Events.release()
        return alias

    @classmethod
    def alias_to_original(cls, alias):
        """Returns the original name given the alias.

        Args:
            alias (str): alias.

        Returns:
            str: the original name if the alias is found in the alias database.

        Raises
            AliasNotFoundError: if the alias is not in the database.

        """
        self = Alias.__new__(Alias)
        self.__init__()

        for file in self.json:
            if file.alias == alias:
                return file.original

        raise AliasNotFoundError(f"Alias not found: {alias!r}")

    @classmethod
    def get_original_from_id(cls, id_):
        """Returns the original name given the id.

        Args:
            id_ (str | int): id.

        Returns:
            str: the original name if the id is found in the alias database.

        Raises
            IdError: if the id is not in the database.

        """
        self = Alias.__new__(Alias)
        self.__init__()

        for file in self.json:
            if file.id == id_:
                return file.original

        raise IdError(f"Id not found: {id_}")

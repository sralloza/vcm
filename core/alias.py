"""Alias manager for signatures."""
import json
import os
from threading import Semaphore

from .options import Options




class Events:
    """Contains events to control the multithreading version of Alias."""
    access = Semaphore()

    @staticmethod
    def acquire():
        Events.access.acquire()

    @staticmethod
    def release():
        Events.access.release()


class Alias:
    """Class designed to declare aliases"""

    def __init__(self):
        self.alias_path = os.path.join(Options.ROOT_FOLDER, 'alias.json')
        self.json = []
        self.load()

    def __len__(self):
        return len(self.json)

    def load(self):
        """Loads the alias configuration."""

        if os.path.isfile(self.alias_path) is False:
            self.json = []
            return
        try:
            Events.acquire()
            with open(self.alias_path, encoding='utf-8') as file_handler:
                self.json = json.load(file_handler) or []
        except json.JSONDecodeError as ex:
            raise AliasFatalError('Raised JSONDecodeError') from ex
        except UnicodeDecodeError as ex:
            raise AliasFatalError('Raised UnicodeDecodeError') from ex

        if not isinstance(self.json, list):
            raise TypeError(f'alias file invalid ({type(self.json).__name__})')

        for alias in self.json:
            if 'id' not in alias or 'new' not in alias or 'old' not in alias or 'type' not in alias:
                raise TypeError(f'alias file invalid: {alias!r}')

        Events.release()

    @staticmethod
    def destroy():
        """Destroys the alias database."""

        self = Alias.__new__(Alias)
        self.__init__()
        Events.acquire()

        self.json = []
        with open(self.alias_path, 'wt', encoding='utf-8') as file_handler:
            json.dump([], file_handler, indent=4, sort_keys=True, ensure_ascii=False)

        Events.release()
        return

    def save(self):
        """Saves alias configuration to the file."""
        try:
            with open(self.alias_path, encoding='utf-8') as file_handler:
                temp = json.load(file_handler) or []
        except (FileNotFoundError, json.JSONDecodeError):
            temp = []

        to_write = (self.json + temp)

        res_list = []
        for i in range(len(to_write)):
            if to_write[i] not in to_write[i + 1:]:
                res_list.append(to_write[i])

        with open(self.alias_path, 'wt', encoding='utf-8') as file_handler:
            json.dump(res_list, file_handler, indent=4, sort_keys=True, ensure_ascii=False)

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
                if temp == file['new']:
                    done = False
                    break

            if done:
                return temp

    @staticmethod
    def _create_name(template: str, index: int):
        """Given a filename and an index, creates the filename.

        Examples
            Alias._createname("file", 5) -> "file.5"
            Alias._createname("file.txt", 5) -> "file.5.txt"
            Alias._createname("some.file.txt", 5) -> "some.file.5.txt"
        """

        splitted = template.split('.')
        if len(splitted) == 1:
            return f'{splitted[0]}.{index}'
        elif len(splitted) == 2:
            return f'{splitted[0]}.{index}.{splitted[1]}'
        else:
            return f'{".".join(splitted[:-1])}.{index}.{splitted[-1]}'

    @staticmethod
    def real_to_alias(id_, real):
        """Returns the alias given the real name.

        Args:
            id_ (str | int): id.
            real (str): real name.

        Returns:
            str: the alias if the real name is found in the alias database. If it is not found, the
                real name will be returned.

        """

        self = Alias.__new__(Alias)
        self.__init__()
        Events.acquire()

        for file in self.json:
            if file['id'] == id_:
                Events.release()

                if file['old'] == real:
                    return file['new']

                raise IdError(f'Same id, different names ({file["id"]}, {file["new"]}, {real})')

        if os.path.isfile(real):
            type_ = 'f'
        elif os.path.isdir(real):
            type_ = 'd'
        else:
            type_ = '?'

        new = real

        for file in self.json:
            if file['old'] == real:
                new = self._increment(new)
                break

        self.json.append({'id': id_, 'old': real, 'new': new, 'type': type_})
        self.save()

        Events.release()
        return new

    @staticmethod
    def alias_to_real(alias):
        """Returns the real name given the alias.

        Args:
            alias (str): alias.

        Returns:
            str: the real name if the alias is found in the alias database.

        Raises
            AliasNotFoundError: if the alias is not in the database.

        """
        self = Alias.__new__(Alias)
        self.__init__()

        for file in self.json:
            if file['new'] == alias:
                return file['old']

        raise AliasNotFoundError(f'Alias not found: {alias!r}')

    @staticmethod
    def get_real_from_id(id_):
        """Returns the real name given the id.

        Args:
            id_ (str | int): id.

        Returns:
            str: the real name if the id is found in the alias database.

        Raises
            IdError: if the id is not in the database.

        """
        self = Alias.__new__(Alias)
        self.__init__()

        for file in self.json:
            if file['id'] == id_:
                return file['old']

        raise IdError(f'Id not found: {id_}')

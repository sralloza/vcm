"""Alias manager for signatures."""
import json
import os
from threading import Event

from .options import Options


class IdError(Exception):
    """Error with ids."""


class AliasNotFoundError(Exception):
    """Alias not found error."""


class Events:
    free = Event()
    free.set()


class Alias:
    """Class designed to declare aliases"""

    def __init__(self):
        Events.free.wait()
        self.alias_path = os.path.join(Options.ROOT_FOLDER, 'alias.json')
        self.json = []
        self.load()

    def load(self):
        """Loads the alias configuration."""
        if os.path.isfile(self.alias_path) is False:
            self.json = []
            return
        try:
            with open(self.alias_path, encoding='utf-8') as file_handler:
                self.json = json.load(file_handler) or []
        except json.JSONDecodeError:
            self.json = []

        if not isinstance(self.json, list):
            raise TypeError(f'alias file invalid ({type(self.json).__name__})')

        for alias in self.json:
            if 'id' not in alias or 'new' not in alias or 'old' not in alias or 'type' not in alias:
                raise TypeError(f'alias file invalid: {alias!r}')

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
        Events.free.wait()

        Events.free.clear()

        for file in self.json:
            if file['id'] == id_:
                Events.free.set()

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

        Events.free.set()
        return new

    @staticmethod
    def alias_to_real(alias):

        self = Alias.__new__(Alias)
        self.__init__()

        for file in self.json:
            if file['new'] == alias:
                return file['old']

        raise AliasNotFoundError(f'Alias not found: {alias!r}')

    @staticmethod
    def get_real_from_id(id_):
        self = Alias.__new__(Alias)
        self.__init__()

        for file in self.json:
            if file['id'] == id_:
                return file['old']

        raise IdError(f'Id not found: {id_}')

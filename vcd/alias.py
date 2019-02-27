"""Alias manager for signatures."""
import json
import os

from .options import Options


class Alias:
    """Class designed to declare aliases"""

    def __init__(self, autosave=True):
        """

        Args:
            autosave (bool): Save aliases after every operation.
        """
        self.alias_path = os.path.join(Options.ROOT_FOLDER, 'alias.json')
        self.json = {}
        self.autosave = autosave
        self.load()

        if self.autosave:
            self.save()

    def load(self):
        """Loads the alias configuration."""
        if os.path.isfile(self.alias_path) is False:
            self.json = {}
            return
        try:
            with open(self.alias_path, encoding='utf-8') as file_handler:
                self.json = json.load(file_handler) or {}
        except json.JSONDecodeError:
            self.json = {}

    def save(self):
        """Saves alias configuration to the file."""
        with open(self.alias_path, 'wt', encoding='utf-8') as file_handler:
            json.dump(self.json, file_handler, indent=4, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def real_to_alias(real, autosave=True):
        """Returns the alias given the real name.

        Args:
            real (str): real name.
            autosave (bool): either to save the alias configuration or not.

        Returns:
            str: the alias if the real name is found in the alias database. If it is not found, the
                real name will be returned.

        """
        self = Alias.__new__(Alias)
        self.__init__(autosave=autosave)

        if real in self.json.keys():
            return self.json[real]
        return real

    @staticmethod
    def alias_to_real(alias, autosave=True):
        """Returns the real name given the alias.

        Args:
            alias (str): alias.
            autosave (bool): either to save the alias configuration or not.

        Returns:
            str: if the alias is found in the alias database the real name will be return. If not,
                the alias will be returned.

        """
        self = Alias.__new__(Alias)
        self.__init__(autosave=autosave)

        for key, value in self.json.items():
            if value == alias:
                return key

        return alias

import json
import os
from json import JSONDecodeError

from vcd.globals import ROOT_FOLDER


class Alias:
    def __init__(self, autosave=True):
        self.alias_path = os.path.join(ROOT_FOLDER, 'alias.json')
        self.json = {}
        self.autosave = autosave
        self.load()

        if self.autosave:
            self.save()

    def load(self):
        if os.path.isfile(self.alias_path) is False:
            self.json = {}
            return
        try:
            with open(self.alias_path, encoding='utf-8') as fh:
                self.json = json.load(fh) or {}
        except JSONDecodeError:
            self.json = {}

    def save(self):
        with open(self.alias_path, 'wt', encoding='utf-8') as f:
            json.dump(self.json, f, indent=4, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def real_to_alias(real, autosave=True):
        self = Alias.__new__(Alias)
        self.__init__(autosave=autosave)

        if real in self.json.keys():
            return self.json[real]
        return real

    @staticmethod
    def alias_to_real(alias, autosave=True):
        self = Alias.__new__(Alias)
        self.__init__(autosave=autosave)

        for key, value in self.json.items():
            if value == alias:
                return key

        return alias

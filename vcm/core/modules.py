from enum import Enum


class Modules(Enum):
    undefined = "undefined"
    download = "download"
    notify = "notify"
    settings = "settings"

    @classmethod
    def current(cls):
        return _Static.module

    @classmethod
    def set_current(cls, value):
        _Static.module = cls(value)


class _Static:
    module = Modules.undefined

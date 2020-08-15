from enum import Enum


class Modules(Enum):
    undefined = "undefined"
    download = "download"
    notify = "notify"
    discover = "discover"
    settings = "settings"


    @classmethod
    def current(cls):
        return _Static.module

    @classmethod
    def set_current(cls, value):
        _Static.module = cls(value)

    @classmethod
    def should_print(cls):
        return cls.current() != cls.notify


class _Static:
    module = Modules.undefined

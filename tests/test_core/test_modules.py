from unittest import mock

import pytest

from vcm.core.modules import Modules, _Static


class TestModules:
    def test_attributes(self):
        assert len(Modules) == 4

        assert hasattr(Modules, "undefined")
        assert hasattr(Modules, "download")
        assert hasattr(Modules, "notify")
        assert hasattr(Modules, "settings")

        assert isinstance(Modules.undefined.value, str)
        assert isinstance(Modules.download.value, str)
        assert isinstance(Modules.notify.value, str)
        assert isinstance(Modules.settings.value, str)

    @mock.patch("vcm.core.modules._Static")
    def test_current(self, static_m):
        assert Modules.current() == static_m.module

    @mock.patch("vcm.core.modules._Static")
    def test_set_current_ok(self, static_m):
        Modules.set_current("undefined")
        assert static_m.module == Modules.undefined
        Modules.set_current("download")
        assert static_m.module == Modules.download
        Modules.set_current("notify")
        assert static_m.module == Modules.notify
        Modules.set_current("settings")
        assert static_m.module == Modules.settings

    @mock.patch("vcm.core.modules._Static")
    def test_set_current_error(self, _):
        with pytest.raises(ValueError, match=r"'\w+' is not a valid Modules"):
            Modules.set_current("something")


class TestHiddenStatic:
    def test_attributes(self):
        assert hasattr(_Static, "module")
        assert isinstance(_Static.module, Modules)
        assert isinstance(_Static.module.value, str)

    def test_default_value(self):
        assert _Static.module == Modules.undefined

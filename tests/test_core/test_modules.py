import pytest

from vcm.core.modules import Modules, _Static


class TestModules:
    def test_attributes(self):
        assert hasattr(Modules, "undefined")
        assert hasattr(Modules, "download")
        assert hasattr(Modules, "notify")
        assert hasattr(Modules, "settings")

        assert isinstance(Modules.undefined.value, str)
        assert isinstance(Modules.download.value, str)
        assert isinstance(Modules.notify.value, str)
        assert isinstance(Modules.settings.value, str)

    @pytest.mark.xfail
    def test_current(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_set_current(self):
        assert 0, "Not implemented"


class TestHiddenStatic:
    def test_attributes(self):
        assert hasattr(_Static, "module")
        assert isinstance(_Static.module, Modules)
        assert isinstance(_Static.module.value, str)

from enum import Enum

import pytest

from vcm.main import Command


class TestCommand:
    def test_inherintance(self):
        assert issubclass(Command, Enum)

    def test_attributes(self):
        assert hasattr(Command, "notify")
        assert hasattr(Command, "download")
        assert hasattr(Command, "settings")
        assert hasattr(Command, "discover")

    def test_types(self):
        assert isinstance(Command.notify.value, int)
        assert isinstance(Command.download.value, int)
        assert isinstance(Command.settings.value, int)
        assert isinstance(Command.discover.value, int)


@pytest.mark.xfail
def test_parse_args():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_main():
    assert 0, "Not implemented"

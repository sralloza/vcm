import pytest


class TestCommand:
    @pytest.mark.xfail
    def test_attributes(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
def test_parse_args():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_main():
    assert 0, "Not implemented"

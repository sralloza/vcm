import pytest


def test_alphabet():
    from vcm.core.time_operations import ALPHABET

    assert isinstance(ALPHABET, dict)

    for key in ALPHABET:
        assert isinstance(ALPHABET[key], dict)
        for subkey in ALPHABET[key]:
            assert isinstance(ALPHABET[key][subkey], list)

    assert "abbr" in ALPHABET
    assert "default" in ALPHABET


@pytest.mark.xfail
class TestSecondsToString:
    def test_seconds_to_string(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
class TestSplitSeconds:
    def test_split_seconds(self):
        assert 0, "Not implemented"

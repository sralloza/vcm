import pytest


@pytest.mark.xfail
def calculate_hash():
    assert 0, "Not implemented"


class TestEvents:
    @pytest.mark.xfail
    def test_attributes(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def acquire(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def release(self):
        assert 0, "Not implemented"


class TestAliasEntry:
    @pytest.mark.xfail
    def test_init(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def to_json(self):
        assert 0, "Not implemented"


class TestAlias:
    @pytest.mark.xfail
    def test_init(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_len(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def load(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def destroy(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def save(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def _increment(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def _create_name(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def id_to_alias(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def alias_to_id(self):
        assert 0, "Not implemented"

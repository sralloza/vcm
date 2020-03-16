import pytest


@pytest.mark.xfail
def test_calculate_hash():
    assert 0, "Not implemented"


class TestEvents:
    @pytest.mark.xfail
    def test_attributes(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_acquire(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_release(self):
        assert 0, "Not implemented"


class TestAliasEntry:
    @pytest.mark.xfail
    def test_init(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_to_json(self):
        assert 0, "Not implemented"


class TestAlias:
    @pytest.mark.xfail
    def test_init(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_len(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_load(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_destroy(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_save(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test__increment(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test__create_name(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_id_to_alias(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_alias_to_id(self):
        assert 0, "Not implemented"

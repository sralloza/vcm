import pytest


class TestDatabaseInterface:
    @pytest.mark.xfail
    def test_init(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_context_manager(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_ensure_table(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_commit(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_close(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_save_link(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_delete_link(self):
        assert 0, "Not implemented"


class TestDatabaseLinkInterface:
    @pytest.mark.xfail
    def test_save(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_delete(self):
        assert 0, "Not implemented"

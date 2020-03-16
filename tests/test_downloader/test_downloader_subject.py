import pytest


class TestSubject:
    @pytest.mark.xfail
    def test_init(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_repr(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_str(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_make_request(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_create_folder(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_add_link(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_find_section_by_child(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_url_to_query_args(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_find_and_download_links(self):
        assert 0, "Not implemented"


class Section:
    @pytest.mark.xfail
    def test_init(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_str(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_filter_name(self):
        assert 0, "Not implemented"

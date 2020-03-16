import pytest

# FIXME: maybe TestRunServer
class TestServer:
    @pytest.mark.xfail
    def test_error_handler(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_index(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_feed(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_queue_endpoint(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
def test_get_thread_state_info():
    assert 0, "Not implemented"

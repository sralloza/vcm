from threading import Event

import pytest


class TestEmpty:
    def test_assert_attributes(self):
        from vcm.core._threading import Empty

        for method in dir(Empty):
            assert method.startswith("__")
            assert method.endswith("__")


def test_running():
    from vcm.core._threading import running

    assert isinstance(running, Event)
    assert running.is_set()


class TestThreadStates:
    def test_attributes(self):
        from vcm.core._threading import ThreadStates

        assert hasattr(ThreadStates, "idle")
        assert hasattr(ThreadStates, "working_0")
        assert hasattr(ThreadStates, "working_1")
        assert hasattr(ThreadStates, "working_2")
        assert hasattr(ThreadStates, "working_3")
        assert hasattr(ThreadStates, "killed")
        assert hasattr(ThreadStates, "online")

        assert isinstance(ThreadStates.idle.value, int)
        assert isinstance(ThreadStates.working_0.value, int)
        assert isinstance(ThreadStates.working_1.value, int)
        assert isinstance(ThreadStates.working_2.value, int)
        assert isinstance(ThreadStates.working_3.value, int)
        assert isinstance(ThreadStates.killed.value, int)
        assert isinstance(ThreadStates.online.value, int)

    @pytest.mark.xfail
    def test_alias(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
def test_state_to_alias():
    assert 0, "Not implemented"


class TestColors:
    def test_attributes(self):
        from vcm.core._threading import Colors

        assert hasattr(Colors, "blue")
        assert hasattr(Colors, "green")
        assert hasattr(Colors, "orange")
        assert hasattr(Colors, "red")
        assert hasattr(Colors, "magenta")
        assert hasattr(Colors, "black")
        assert hasattr(Colors, "light_blue")

        assert isinstance(Colors.blue.value, str)
        assert isinstance(Colors.green.value, str)
        assert isinstance(Colors.orange.value, str)
        assert isinstance(Colors.red.value, str)
        assert isinstance(Colors.magenta.value, str)
        assert isinstance(Colors.black.value, str)
        assert isinstance(Colors.light_blue.value, str)


@pytest.mark.xfail
def test_state_to_color():
    assert 0, "Not implemented"


class TestWorker:
    @pytest.mark.xfail
    def test_init_attributes(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_state(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_update_state(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_hidden_update_state(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_active(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_to_log(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_kill(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_run(self):
        assert 0, "Not implemented"


class TestKiller:
    @pytest.mark.xfail
    def test_init_attributes(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_to_log(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_run(self):
        assert 0, "Not implemented"


@pytest.mark.xfail
def test_start_workers():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_print_fatal_error():
    assert 0, "Not implemented"

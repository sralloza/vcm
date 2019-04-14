import threading
import time
from queue import Queue

import pytest
import requests

from vcd import runserver
from vcd._threading import Worker


class TestStatusServer:
    def setup_class(self):
        self.queue = Queue()
        self.threads = [Worker(self.queue, name=f'Test-{x:03d}') for x in range(1, 101)]

        for t in self.threads:
            t.start()

        runserver(self.queue, self.threads)

    def test_index(self):
        r = requests.get('http://localhost')

        assert r.status_code == 200
        assert '<p id="content">' in r.text
        assert '</p>' in r.text
        assert '<script>' in r.text
        assert '</script>' in r.text
        assert 'var interval = setInterval' in r.text

    def test_queue_view(self):
        r = requests.get('http://localhost/queue')
        assert r.status_code == 200
        assert '<title>Queue content</title>' in r.text
        assert '<h1>Queue</h1>' in r.text

    def test_feed(self):
        r = requests.get('http://localhost/feed')
        assert r.status_code == 200
        assert '<title>VCD STATUS</title>'
        assert 'Execution time:' in r.text
        assert 'Unfinished' in r.text
        assert 'tasks' in r.text
        assert 'Items left:' in r.text

        assert 'Threads working: ' in r.text
        assert 'Threads idle' in r.text

        for i in range(1, 101):
            assert f'Test-{i:03d}' in r.text


@pytest.fixture(autouse=True, scope='module')
def auto_close_threads():
    yield

    for thread in threading.enumerate():
        if not isinstance(thread, Worker):
            continue

        thread.queue.put(None)

    time.sleep(.2)

    assert len(threading.enumerate()) < 20

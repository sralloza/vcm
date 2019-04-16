# todo - test start_workers
# todo - test Worker()
import threading
import time
from queue import Queue
from typing import List

import pytest

from vcd import Subject, Downloader
from vcd._threading import Worker, start_workers


class TestWorker:
    @pytest.fixture(autouse=True)
    def create_threads(self, close_threads):
        self.q = Queue()
        self.t1 = Worker(self.q, name='test-1')
        self.t2 = Worker(self.q, name='test-2')
        self.t3 = Worker(self.q, name='test-3')

        yield

        close_threads(threading.enumerate()[1:])

    def test_run(self, close_threads):
        self.t1.start()
        self.t2.start()
        self.t3.start()

        close_threads((self.t1, self.t2, self.t3))

    def test_to_log(self):
        self.t1.start()
        assert self.t1.to_log() == '<font color="black">test-1: idle - None</font>'

        subject = Subject('dummy', 'http://httpbin.org/get', Downloader(), self.t1.queue)
        self.t1.queue.put(subject)
        time.sleep(.2)

        assert self.t1.to_log() == '<font color="green">test-1: working - dummy</font>'


def test_start_workers(close_threads):
    q = Queue()
    workers = start_workers(q, nthreads=30)

    assert len(threading.enumerate()) == 31

    close_threads(workers)


@pytest.fixture
def close_threads():
    def real_close_threads(thread_list: List[Worker]):
        for thread in thread_list:
            assert isinstance(thread, Worker)

        for thread in thread_list:
            thread.queue.put(None)

        time.sleep(.2)

        assert len(threading.enumerate()) == 1

    return real_close_threads

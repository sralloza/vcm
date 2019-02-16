"""Multithreading workers for the vcd."""

from queue import Queue
from threading import Thread

from vcd._requests import DownloaderError
from vcd.globals import get_logger
from vcd.links import BaseLink
from vcd.subject import Subject


class Worker(Thread):
    """Special worker for vcd multithreading."""
    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = get_logger(__name__)
        self.queue: Queue = queue

    def run(self):
        """Runs the thread"""
        while True:
            anything = self.queue.get()
            self.logger.debug('%d items remaining in queue', self.queue.qsize())

            if isinstance(anything, BaseLink):
                self.logger.debug('Found Link %r, processing', anything.name)
                try:
                    anything.download()
                except FileNotFoundError as ex:
                    self.logger.exception('FileNotFoundError in url %s (%r)', anything.url, ex)
                except DownloaderError as ex:
                    self.logger.exception('DownloaderError in url %s (%r)', anything.url, ex)
                self.queue.task_done()

            elif isinstance(anything, Subject):
                self.logger.debug('Found Subject %r, processing', anything.name)
                try:
                    anything.find_links()
                except DownloaderError as ex:
                    self.logger.exception('DownloaderError in subject %s (%r)', anything.name, ex)
                self.queue.task_done()


def start_workers(queue, nthreads=20):
    """Starts the wokers.

    Args:
        queue (Queue): queue to manage the workers's tasks.
        nthreads (int): number of trheads to start.

    Returns:

    """
    thread_list = []
    for i in range(nthreads):
        thread = Worker(queue, name=f'W-{i + 1}', daemon=True)
        thread.logger.debug('Started worker named %r', thread.name)
        thread.start()
        thread_list.append(thread)

    return thread_list

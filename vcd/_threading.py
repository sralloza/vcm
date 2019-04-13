"""Multithreading workers for the vcd."""

import logging
from queue import Queue
from threading import Thread

from vcd._requests import DownloaderError
from vcd.links import BaseLink
from vcd.subject import Subject


class Worker(Thread):
    """Special worker for vcd multithreading."""

    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger(__name__)
        self.queue: Queue = queue
        self.status = 'idle'

    # noinspection PyUnresolvedReferences
    def run(self):
        """Runs the thread"""
        while True:
            self.status = 'idle'
            self.logger.info('Worker %r ready to continue working', self.name)
            anything = self.queue.get()
            self.logger.debug('%d items left in queue (%d unfinished tasks)', self.queue.qsize(),
                              self.queue.unfinished_tasks)

            self.status = 'working'
            if isinstance(anything, BaseLink):
                self.logger.debug('Found Link %r, processing', anything.name)
                try:
                    anything.download()
                except FileNotFoundError as ex:
                    self.logger.exception('FileNotFoundError in url %s (%r)', anything.url, ex)
                except DownloaderError as ex:
                    self.logger.exception('DownloaderError in url %s (%r)', anything.url, ex)

                self.logger.info('Worker %r completed work of Link %r', self.name, anything.name)
                self.queue.task_done()

            elif isinstance(anything, Subject):
                self.logger.debug('Found Subject %r, processing', anything.name)
                try:
                    anything.find_links()
                except DownloaderError as ex:
                    self.logger.exception('DownloaderError in subject %s (%r)', anything.name, ex)

                self.logger.info('Worker %r completed work of Subject %r', self.name, anything.name)
                self.queue.task_done()

            self.logger.info('%d unfinished tasks', self.queue.unfinished_tasks)


def start_workers(queue, nthreads=20):
    """Starts the wokers.

    Args:
        queue (Queue): queue to manage the workers's tasks.
        nthreads (int): number of trheads to start.

    Returns:

    """
    thread_list = []
    for i in range(nthreads):
        thread = Worker(queue, name=f'W-{i + 1:02d}', daemon=True)
        thread.logger.debug('Started worker named %r', thread.name)
        thread.start()
        thread_list.append(thread)

    return thread_list

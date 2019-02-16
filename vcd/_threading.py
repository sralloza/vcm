from queue import Queue
from threading import Thread

from vcd.links import BaseLink
from vcd.downloader import DownloaderError
from vcd.globals import get_logger
from vcd.subject import Subject


# noinspection PyProtectedMember
class Worker(Thread):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = get_logger(__name__)
        self.queue: Queue = queue

    def run(self):
        """Runs the thread"""
        while True:
            anything = self.queue.get()
            self.logger.debug('%d items remaining in queue', self.queue._qsize())

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


def start_workers(queue, n=20):
    thread_list = []
    for i in range(n):
        t = Worker(queue, name=f'W-{i + 1}', daemon=True)
        t.logger.debug('Started worker named %r', t.name)
        t.start()
        thread_list.append(t)

    return thread_list

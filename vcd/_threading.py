"""Multithreading workers for the vcd."""

import logging
import time
import threading

from queue import Queue


from ._getch import getch
from ._requests import DownloaderError
from .links import BaseLink
from .subject import Subject
from .time_operations import seconds_to_str


class Worker(threading.Thread):
    """Special worker for vcd multithreading."""

    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger(__name__)
        self.queue: Queue = queue
        self.status = 'idle'
        self.timestamp = None
        self.current_object = None
        self.active = True

    def to_log(self, integer=False):
        color = 'black'
        exec_time = 0

        if self.timestamp is not None:
            exec_time = time.time() - self.timestamp

            if exec_time < 30:
                color = 'green'
            elif 30 < exec_time < 60:
                color = "orange"
            else:
                color = "red"

        status = f'<font color="{color}">{self.name}: {self.status} - '

        if exec_time > 90:
            status += f'[{seconds_to_str(exec_time, integer=integer)}] '

        if isinstance(self.current_object, BaseLink):
            status += f'{self.current_object.subject.name} → {self.current_object.name}'
        elif isinstance(self.current_object, Subject):
            status += f'{self.current_object.name}'
        else:
            status += 'None'

        status += '</font>'

        return status

    # noinspection PyUnresolvedReferences
    def run(self):
        """Runs the thread"""
        while self.active:
            self.status = 'idle'
            self.logger.info('Worker %r ready to continue working', self.name)
            anything = self.queue.get()
            self.timestamp = time.time()
            self.logger.debug('%d items left in queue (%d unfinished tasks)', self.queue.qsize(),
                              self.queue.unfinished_tasks)

            self.status = 'working'
            self.current_object = anything

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
            elif anything is None:
                self.logger.info('Closing thread, received None')
                self.logger.info('%d unfinished tasks', self.queue.unfinished_tasks)
                self.current_object = None
                self.timestamp = None
                return

            self.logger.info('%d unfinished tasks', self.queue.unfinished_tasks)
            self.current_object = None
            self.timestamp = None


class Killer(threading.Thread):
    def __init__(self, queue):
        super().__init__(name='Killer', daemon=True)
        self.queue = queue

    def to_log(self, *args, **kwargs):
        return f'<font color="blue">{self.name}: working'

    def run(self):
        print('ready')
        while True:
            try:
                char = getch()
                real = char.decode().lower()
            except UnicodeError:
                continue

            if real == 'q':
                print('KILLING')

                self.queue.mutex.acquire()
                self.queue.queue.clear()
                # self.queue.all_tasks_done.notify_all()
                self.queue.unfinished_tasks = 0
                self.queue.mutex.release()

                for thread in threading.enumerate():
                    if isinstance(thread, Worker):
                        thread.active = False
                        thread.status = 'killed'

                exit(1)


def start_workers(queue, nthreads=20):
    """Starts the wokers.

    Args:
        queue (Queue): queue to manage the workers's tasks.
        nthreads (int): number of trheads to start.

    Returns:

    """

    thread_list = []

    killer = Killer(queue)
    killer.start()
    thread_list.append(killer)

    for i in range(nthreads):
        thread = Worker(queue, name=f'W-{i + 1:02d}', daemon=True)
        thread.logger.debug('Started worker named %r', thread.name)
        thread.start()
        thread_list.append(thread)

    return thread_list

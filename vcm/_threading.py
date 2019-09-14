"""Multithreading workers for the vcd."""

import logging
import threading
import time
import webbrowser

from queue import Queue

from ._requests import DownloaderError
from .links import BaseLink
from .subject import Subject
from .time_operations import seconds_to_str
from .utils import getch


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
        status_code = 0

        if self.timestamp is not None:
            exec_time = time.time() - self.timestamp

            if exec_time < 30:
                color = 'green'
                status_code = 1
            elif 30 <= exec_time < 60:
                color = "orange"
                status_code = 2
            elif 60 <= exec_time < 90:
                color = "red"
                status_code = 3
            else:
                color = "magenta"
                status_code = 4

        status = f'<font color="{color}">{self.name}: {self.status} - '

        if status_code == 4:
            status += f'[{seconds_to_str(exec_time, integer=integer)}] '

        if isinstance(self.current_object, BaseLink):
            status += f'{self.current_object.subject.name} → {self.current_object.name}'
        elif isinstance(self.current_object, Subject):
            status += f'{self.current_object.name}'
        elif isinstance(self.current_object, str):
            status += self.current_object
        else:
            status += 'None'

        status += '</font>'

        return status, status_code

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
            elif anything == 'killed':
                self.status = 'killed'
                break

            self.logger.info('%d unfinished tasks', self.queue.unfinished_tasks)
            self.current_object = None
            self.timestamp = None

        # if self.status == 'killed':
        self.timestamp = None
        self.current_object = 'Dead thread'

        for thread in threading.enumerate():
            if isinstance(thread, Worker):
                self.queue.put('killed')
                thread.status = 'killed'
                thread.active = 0

        while True:
            foo = self.queue.get()
            if not foo:
                break
            self.queue.task_done()

        exit()


class Killer(threading.Thread):
    def __init__(self, queue):
        super().__init__(name='Killer', daemon=True)
        self.queue = queue
        self.status = 'online'

    def to_log(self, *args, **kwargs):
        output = f'<font color="blue">{self.name}: {self.status}'
        return output, 0

    def run(self):
        print('Killer ready')
        while True:
            try:
                char = getch()
                real = char.decode().lower()
            except UnicodeError:
                continue

            if real in ('q', 'k'):
                print('Exiting')

                for thread in threading.enumerate():
                    if isinstance(thread, Worker):
                        thread.active = False
                        thread.status = 'killed'

                self.status = 'commited suicide'
                exit(1)

            if real in ('w', 'o'):
                print('Opening status server')
                chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
                webbrowser.get(chrome_path).open_new('localhost')


def start_workers(queue, nthreads=20, no_killer=False):
    """Starts the wokers.

    Args:
        queue (Queue): queue to manage the workers's tasks.
        nthreads (int): number of trheads to start.
        no_killer (bool): if true, killer thread will not be started.

    Returns:

    """

    thread_list = []

    if no_killer is False:
        killer = Killer(queue)
        killer.start()
        thread_list.append(killer)
    else:
        print('Killer not started')

    for i in range(nthreads):
        thread = Worker(queue, name=f'W-{i + 1:02d}', daemon=True)
        thread.logger.debug('Started worker named %r', thread.name)
        thread.start()
        thread_list.append(thread)

    return thread_list

"""Multithreading workers for the VCM."""

import logging
import threading
import time
import webbrowser
from enum import Enum, auto
from queue import Queue
from typing import Any

from vcm.core.modules import Modules
from vcm.downloader.link import BaseLink
from vcm.downloader.subject import Subject

from .exceptions import InvalidStateError
from .networking import DownloaderError
from .time_operations import seconds_to_str
from .utils import Printer, getch

logger = logging.getLogger(__name__)


class Empty:
    pass


class ThreadStates(Enum):
    idle = auto()
    working = auto()
    killed = auto()
    online = auto()

    @staticmethod
    def get(value):
        try:
            return ThreadStates(value)
        except ValueError:
            pass

        try:
            return ThreadStates[value]
        except KeyError:
            pass

        raise ValueError("%r is not a valid %s" % (value, ThreadStates.__name__))


class WorkerCodes(Enum):
    black = 0
    green = 1
    orange = 2
    red = 3
    magenta = 4


class Worker(threading.Thread):
    """Special worker for VCM multithreading."""

    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.called_from = Modules.current()
        self.queue: Queue = queue
        self._state = ThreadStates.idle
        self.timestamp = None
        self.current_object = None

    @property
    def state(self):
        return self._state

    @property
    def active(self):
        return self.state != ThreadStates.killed

    def to_log(self, integer=False):
        code = WorkerCodes.black
        exec_time = 0

        if self.state == ThreadStates.idle:
            code = WorkerCodes.green

        if self.timestamp is not None:
            exec_time = time.time() - self.timestamp

            if exec_time < 30 and self.state != ThreadStates.killed:
                code = WorkerCodes.green
            elif 30 <= exec_time < 60:
                code = WorkerCodes.orange
            elif 60 <= exec_time < 90:
                code = WorkerCodes.red
            else:
                code = WorkerCodes.magenta

        status = f'<font color="{code.name}">{self.name}: {self.state.name} - '

        if code == WorkerCodes.magenta:
            status += f"[{seconds_to_str(exec_time, integer=integer)}] "

        if isinstance(self.current_object, BaseLink):
            status += f"{self.current_object.subject.name} → {self.current_object.name}"
        elif isinstance(self.current_object, Subject):
            status += f"{self.current_object.name}"
        elif isinstance(self.current_object, str):
            status += self.current_object
        else:
            status += "None"

        status += "</font>"

        return status, code.value

    def kill(self):
        self.set_state(ThreadStates.killed, None)

    def set_state(self, state, queue_object: Any = Empty):
        self._state = ThreadStates.get(state)

        if queue_object != Empty:
            self.current_object = queue_object
            return

        if self.state in [ThreadStates.idle, ThreadStates.killed, ThreadStates.online]:
            self.current_object = None
            self.timestamp = None

    # noinspection PyUnresolvedReferences
    def run(self):
        """Runs the thread"""
        while self.active:
            self.set_state(ThreadStates.idle)
            logger.info("Worker %r ready to continue working", self.name)
            queue_object = self.queue.get()
            self.timestamp = time.time()
            logger.debug(
                "%d items left in queue (%d unfinished tasks)",
                self.queue.qsize(),
                self.queue.unfinished_tasks,
            )

            self.set_state(ThreadStates.working, queue_object)

            if isinstance(queue_object, BaseLink):
                logger.debug("Found Link %r, processing", queue_object.name)
                try:
                    queue_object.download()
                except FileNotFoundError as ex:
                    logger.exception(
                        "FileNotFoundError in url %s (%r)", queue_object.url, ex
                    )
                except DownloaderError as ex:
                    logger.exception(
                        "DownloaderError in url %s (%r)", queue_object.url, ex
                    )

                logger.info(
                    "Worker %r completed work of Link %r", self.name, queue_object.name
                )
                self.queue.task_done()

            elif isinstance(queue_object, Subject):
                logger.debug("Found Subject %r, processing", queue_object.name)
                try:
                    queue_object.find_and_download_links()
                except DownloaderError as ex:
                    logger.exception(
                        "DownloaderError in subject %s (%r)", queue_object.name, ex
                    )

                logger.info(
                    "Worker %r completed work of Subject %r",
                    self.name,
                    queue_object.name,
                )
                self.queue.task_done()
            elif queue_object is None:
                logger.info("Closing thread, received None")
                return self.kill()
            elif queue_object == ThreadStates.killed:
                return self.kill()
            else:
                raise InvalidStateError("Unkown object in queue: %r" % queue_object)

            logger.info("%d unfinished tasks", self.queue.unfinished_tasks)
            self.set_state(ThreadStates.idle)
            self.timestamp = None

        return self.kill()


class Killer(Worker):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(queue, name="Killer", *args, **kwargs)
        self.queue = queue
        self.status = ThreadStates.online

    def to_log(self, *args, **kwargs):
        output = f'<font color="blue">{self.name}: {self.status.name}'
        return output, 0

    def run(self):
        Printer.print("Killer ready")
        while True:
            try:
                char = getch()
                real = char.decode().lower()
            except UnicodeError:
                continue

            if real in ("q", "k"):
                Printer.print("Exiting")

                for thread in threading.enumerate():
                    if isinstance(thread, Worker):
                        thread.kill()

                self.kill()
                exit(1)

            if real in ("w", "o"):
                Printer.print("Opening state server")
                chrome_path = (
                    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
                )
                webbrowser.get(chrome_path).open_new("localhost")


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
        killer = Killer(queue, daemon=True)
        killer.start()
        thread_list.append(killer)
    else:
        if Modules.current() == Modules.download:
            Printer.print("Killer not started")

    for i in range(nthreads):
        thread = Worker(queue, name=f"W-{i + 1:02d}", daemon=True)
        logger.debug("Started worker named %r", thread.name)
        thread.start()
        thread_list.append(thread)

    return thread_list

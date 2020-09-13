"""Multithreading workers for the VCM."""
from enum import Enum, auto
from logging import getLogger
from queue import Empty as EmptyQueue
from queue import Queue
import sys
from threading import Event, Thread
from threading import enumerate as enumerate_threads
from time import time
from typing import List

import click

from .time_operations import seconds_to_str
from .utils import ErrorCounter, Printer, open_http_status_server

logger = getLogger(__name__)


running = Event()
running.set()


class ThreadStates(Enum):
    idle = auto()
    working_0 = auto()
    working_1 = auto()
    working_2 = auto()
    working_3 = auto()
    killed = auto()
    online = auto()  # Only valid for the Killer Thread

    @property
    def alias(self):
        return self.name.split("_")[0]


class Colors(Enum):
    blue = "blue"
    green = "green"
    orange = "orange"
    red = "red"
    magenta = "magenta"
    black = "black"
    light_blue = "light_blue"


state_to_color = {
    ThreadStates.idle: Colors.blue,
    ThreadStates.working_0: Colors.green,
    ThreadStates.working_1: Colors.orange,
    ThreadStates.working_2: Colors.red,
    ThreadStates.working_3: Colors.magenta,
    ThreadStates.killed: Colors.black,
    ThreadStates.online: Colors.light_blue,
}


class Worker(Thread):
    """Special worker for VCM multithreading."""

    def __init__(self, queue, state=None, name=None):
        super().__init__(name=name, daemon=True)

        self.queue: Queue = queue
        self.timestamp = None
        self.current_object = None

        if state:
            self.set_state(state)
        else:
            self.set_state(ThreadStates.idle)

        self.last_state_update = 0
        self.update_state()

        from vcm.downloader.subject import Subject
        from vcm.downloader.link import BaseLink

        self.Subject = Subject
        self.BaseLink = BaseLink

    @property
    def state(self) -> ThreadStates:
        # self.update_state()
        return self._state

    def set_state(self, state):
        self._state = state

    def update_state(self):
        # Update state at less than one Herz
        if time() - self.last_state_update > 1:
            self._update_state()
            self.last_state_update = time()

    def _update_state(self):
        if self.timestamp is None:
            return

        exec_time = time() - self.timestamp

        if exec_time < 30:
            self.set_state(ThreadStates.working_0)
        elif 30 <= exec_time < 60:
            self.set_state(ThreadStates.working_1)
        elif 60 <= exec_time < 90:
            self.set_state(ThreadStates.working_2)
        else:
            self.set_state(ThreadStates.working_3)

    @property
    def active(self):
        return running.is_set()

    def to_log(self, integer=False):
        self._update_state()
        state = self.state
        color = state_to_color[state]
        status = f'<font color="{color.name}"><b>{self.name}: {state.alias}</b> - '

        if state == ThreadStates.working_3:
            timestamp = -float("inf") if not self.timestamp else self.timestamp
            status += f"[{seconds_to_str(time() - timestamp, integer=integer)}] "

        if isinstance(self.current_object, self.BaseLink):
            status += f"{self.current_object.subject.name} → <i>{self.current_object.name}</i>"
        elif isinstance(self.current_object, self.Subject):
            status += f'</font><font color="#aa00ff">{self.current_object.name}</font>'
        elif isinstance(self.current_object, str):
            status += f'</font><font color="##ff00ff">{self.current_object}</font>'
        else:
            status += "None"

        status += "</font>"

        return status

    def kill(self):
        while True:
            try:
                self.queue.get(False)
                self.queue.task_done()
            except EmptyQueue:
                break

        self.timestamp = None
        self.set_state(ThreadStates.killed)
        logger.info("Thread killed")
        running.clear()
        sys.exit()

    def run(self):
        """Runs the thread"""
        while self.active:
            logger.info("Worker %r ready to continue working", self.name)
            self.current_object = self.queue.get()
            self.timestamp = time()
            self.update_state()
            logger.debug(
                "%d items left in queue (%d unfinished tasks)",
                self.queue.qsize(),
                self.queue.unfinished_tasks,
            )

            if isinstance(self.current_object, self.BaseLink):
                logger.debug("Found Link %r, processing", self.current_object.name)
                try:
                    self.current_object.download()
                except Exception as exc:
                    print_fatal_error(exc, self.current_object)
                except BaseException as exc:
                    if not isinstance(exc, SystemExit):
                        raise
                    logger.warning(
                        "Catched SystemExit exception (%s), ignoring it", exc
                    )
                    print_fatal_error(exc, self.current_object, log_exception=False)

                logger.info(
                    "Worker %r completed work of Link %r",
                    self.name,
                    self.current_object.name,
                )
                self.queue.task_done()

            elif isinstance(self.current_object, self.Subject):
                logger.debug("Found Subject %r, processing", self.current_object.name)
                try:
                    self.current_object.find_and_download_links()
                except Exception as exc:
                    print_fatal_error(exc, self.current_object)
                except BaseException as exc:
                    if not isinstance(exc, SystemExit):
                        raise
                    logger.warning(
                        "Catched SystemExit exception (%s), ignoring it", exc
                    )
                    print_fatal_error(exc, self.current_object, log_exception=False)

                logger.info(
                    "Worker %r completed work of Subject %r",
                    self.name,
                    self.current_object.name,
                )
                self.queue.task_done()
            else:
                raise ValueError("Unknown object in queue: %r" % self.current_object)

            logger.info(
                "%d unfinished tasks (continue=%s)",
                self.queue.unfinished_tasks,
                self.active,
            )
            self.current_object = None
            self.timestamp = None
            self.set_state(ThreadStates.idle)

        return self.kill()


class Killer(Worker):
    def __init__(self, queue):
        super().__init__(queue, name="Killer", state=ThreadStates.online)
        self.queue = queue
        # self.set_state(ThreadStates.online)

    def to_log(self, integer=False):
        output = f'<font color="blue"><b>{self.name}: {self.state.name}</b>'
        return output

    def run(self):
        Printer.print("Killer ready")
        while True:
            try:
                char = click.getchar()
                real = str(char).lower()
            except UnicodeError:
                continue

            if real in ("q", "k"):
                Printer.print("Exiting")
                logger.info("Killer thread starts his massacre")

                for thread in enumerate_threads():
                    if isinstance(thread, Worker):
                        thread.kill()

                logger.info("Killer thread ended his massacre")
                return self.kill()

            if real in ("w", "o"):
                open_http_status_server()


def start_workers(queue, nthreads=20, killer=True) -> List[Worker]:
    """Starts the wokers.

    Args:
        queue (Queue): queue to manage the workers's tasks.
        nthreads (int): number of trheads to start.
        killer (bool): if True, killer thread will be started.

    Returns:
        List[Worker]: list of started threads.
    """

    thread_list = []

    if killer is True:
        killer = Killer(queue)
        killer.start()
        thread_list.append(killer)
    else:
        Printer.print("Killer not started")

    for i in range(nthreads):
        thread = Worker(queue, name=f"W-{i + 1:02d}")
        logger.debug("Started worker named %r", thread.name)
        thread.start()
        thread_list.append(thread)

    return thread_list


def print_fatal_error(exception, current_object, log_exception=True):
    ErrorCounter.record_error(exception)
    if log_exception:
        logger.exception(
            "%s in %r(url=%r) (%r)",
            type(exception).__name__,
            type(current_object).__name__,
            current_object.url,
            exception,
        )

    Printer.print(
        "ERROR: %s in url %s (%r)"
        % (type(exception).__name__, current_object.url, exception),
        color="bright_red",
    )

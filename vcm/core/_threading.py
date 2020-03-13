"""Multithreading workers for the VCM."""

from enum import Enum, auto
from logging import getLogger
from queue import Empty as EmptyQueue
from queue import Queue
from threading import Event, Thread
from threading import enumerate as enumerate_threads
from time import time
from webbrowser import get as getwebbrowser

from colorama import Fore

from vcm.core.modules import Modules
from vcm.downloader.link import BaseLink
from vcm.downloader.subject import Subject

from .time_operations import seconds_to_str
from .utils import Printer, getch

logger = getLogger(__name__)


class Empty:
    pass


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
        return _state_to_alias[self]


_state_to_alias = {
    ThreadStates.idle: "idle",
    ThreadStates.working_0: "working",
    ThreadStates.working_1: "working",
    ThreadStates.working_2: "working",
    ThreadStates.working_3: "working",
    ThreadStates.killed: "killed",
    ThreadStates.online: "online",
}


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

    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.called_from = Modules.current()
        self.queue: Queue = queue
        self.timestamp = None
        self.current_object = None

        self._state = ThreadStates.idle
        self._last_state_update = time()
        self._update_state()

    @property
    def state(self):
        self.update_state()
        return self._state

    def update_state(self):
        if time() - self._last_state_update > 1:
            self._update_state()
            self._last_state_update = time()

    def _update_state(self):
        if self.timestamp is None:
            if not self.active:
                self._state = ThreadStates.killed
                return

            if isinstance(self, Killer):
                self._state = ThreadStates.online
                return

            if self.current_object is None:
                self._state = ThreadStates.idle
                return

        exec_time = time() - self.timestamp

        if exec_time < 30:
            state = ThreadStates.working_0
        elif 30 <= exec_time < 60:
            state = ThreadStates.working_1
        elif 60 <= exec_time < 90:
            state = ThreadStates.working_2
        else:
            state = ThreadStates.working_3

        self._state = state
        return

    @property
    def active(self):
        return running.is_set()

    def to_log(self, integer=False):
        state = self.state
        color = state_to_color[state]
        status = f'<font color="{color.name}">{self.name}: {state.alias} - '

        if state == ThreadStates.working_3:
            timestamp = -float("inf") if not self.timestamp else self.timestamp
            status += f"[{seconds_to_str(time() - timestamp, integer=integer)}] "

        if isinstance(self.current_object, BaseLink):
            status += f"{self.current_object.subject.name} → {self.current_object.name}"
        elif isinstance(self.current_object, Subject):
            status += f"{self.current_object.name}"
        elif isinstance(self.current_object, str):
            status += self.current_object
        else:
            status += "None"

        status += "</font>"

        return status

    def kill(self):
        logger.info("Thread killed")

        while True:
            try:
                self.queue.get(False)
                self.queue.task_done()
            except EmptyQueue:
                break

        self.timestamp = None
        running.clear()

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

            if isinstance(self.current_object, BaseLink):
                logger.debug("Found Link %r, processing", self.current_object.name)
                try:
                    self.current_object.download()
                except Exception as exc:
                    print_fatal_error(exc, self.current_object)

                logger.info(
                    "Worker %r completed work of Link %r",
                    self.name,
                    self.current_object.name,
                )
                self.queue.task_done()

            elif isinstance(self.current_object, Subject):
                logger.debug("Found Subject %r, processing", self.current_object.name)
                try:
                    self.current_object.find_and_download_links()
                except Exception as exc:
                    print_fatal_error(exc, self.current_object)

                logger.info(
                    "Worker %r completed work of Subject %r",
                    self.name,
                    self.current_object.name,
                )
                self.queue.task_done()
            else:
                raise ValueError("Unkown object in queue: %r" % self.current_object)

            logger.info("%d unfinished tasks", self.queue.unfinished_tasks)
            self.current_object = None
            self.timestamp = None

        return self.kill()


class Killer(Worker):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(queue, name="Killer", *args, **kwargs)
        self.queue = queue
        self.status = ThreadStates.online

    def to_log(self, integer=False):
        output = f'<font color="blue">{self.name}: {self.status.name}'
        return output

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
                logger.info("Killer thread starts his massacre")

                for thread in enumerate_threads():
                    if isinstance(thread, Worker):
                        thread.kill()

                logger.info("Killer thread ended his massacre")
                self.kill()
                exit(1)

            if real in ("w", "o"):
                Printer.print("Opening state server")
                chrome_path = (
                    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
                )
                getwebbrowser(chrome_path).open_new("localhost")


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


def print_fatal_error(exception, current_object):
    logger.exception(
        "%s in %r(url=%r) (%r)",
        type(exception).__name__,
        type(current_object),
        current_object.url,
        exception,
    )

    Printer.print(
        "%sERROR: %s in url %s (%r)%s"
        % (
            Fore.LIGHTRED_EX,
            type(exception).__name__,
            current_object.url,
            exception,
            Fore.RESET,
        )
    )

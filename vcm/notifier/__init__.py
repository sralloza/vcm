"""Notifier module. Manages email report."""
import logging
from queue import Queue
from typing import List, Union

from vcm.core.networking import Connection
from vcm.core.status_server import runserver
from vcm.core.utils import Printer, timing
from vcm.core.workers import start_workers
from vcm.downloader import find_subjects

from .report import send_report

_A = Union[List[str], str]


@timing(name="VCM notifier")
def notify(send_to: _A, use_icons=True, nthreads=20, status_server=False):
    """Launches notify scanner.

    Args:
        send_to (_A): address or list of address to send the report to
            (email address).
        use_icons (bool, optional): if true, icons will be included in
            email. Defaults to True.
        nthreads (int, optional): number of threads to use. Defaults to 20.
        status_server (bool, optional): if true, a http server will be opened
            in port 80 to show the status of each thread. Defaults to False.
    """

    logger = logging.getLogger(__name__)
    logger.info(
        "Launching notify(send_to=%r, use_icons=%s, nthreads=%s, status_server=%s)",
        send_to,
        use_icons,
        nthreads,
        status_server,
    )

    Printer.silence()

    queue = Queue()
    threads = start_workers(queue, nthreads, killer=False)

    if status_server:
        runserver(queue, threads)

    with Connection():
        subjects = find_subjects(queue)
        queue.join()
        send_report(subjects, use_icons, send_to)

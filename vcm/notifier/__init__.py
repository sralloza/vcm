import logging
import time
from queue import Queue
from typing import List, Union

from vcm import Options
from vcm.core._requests import Connection
from vcm.core._threading import start_workers
from vcm.core.modules import Modules
from vcm.core.status_server import runserver
from vcm.core.time_operations import seconds_to_str
from vcm.downloader import get_subjects
from vcm.downloader.subject import Subject
from vcm.notifier.report import send_report

S = List[Subject]
A = Union[List[str], str]

logger = logging.getLogger(__name__)


def notify(send_to: A, use_icons=True, nthreads=20):
    initial_time = time.time()

    Options.set_module(Modules.notify)
    queue = Queue()
    threads = start_workers(queue, nthreads, no_killer=True)
    runserver(queue, threads)

    with Connection() as connection:
        subjects = get_subjects(connection, queue)

        for i, _ in enumerate(subjects):
            queue.put(subjects[i])

        queue.join()

        send_report(subjects, use_icons, send_to)

    final_time = time.time() - initial_time
    logger.info('VCM notifier executed in %s', seconds_to_str(final_time))

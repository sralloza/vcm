import logging
from queue import Queue
from typing import List, Union

from vcm.core._threading import start_workers
from vcm.core.modules import Modules
from vcm.core.networking import Connection
from vcm.core.options import Options
from vcm.core.status_server import runserver
from vcm.core.utils import timing
from vcm.downloader import get_subjects
from vcm.downloader.subject import Subject
from vcm.notifier.report import send_report

S = List[Subject]
A = Union[List[str], str]

logger = logging.getLogger(__name__)


@timing(name='VCM notifier')
def notify(send_to: A, use_icons=True, nthreads=20):
    Modules.set_current(Modules.notify)
    queue = Queue()
    threads = start_workers(queue, nthreads, no_killer=True)
    runserver(queue, threads)

    with Connection() as connection:
        subjects = get_subjects(connection, queue)

        for i, _ in enumerate(subjects):
            queue.put(subjects[i])

        queue.join()

        send_report(subjects, use_icons, send_to)

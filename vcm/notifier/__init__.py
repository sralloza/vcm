from queue import Queue
from typing import List, Union

from vcm.core._requests import Connection
from vcm.core._threading import start_workers
from vcm.core.status_server import runserver
from vcm.downloader import get_subjects
from vcm.downloader.subject import Subject
from vcm.notifier.report import send_report

S = List[Subject]
A = Union[List[str], str]


def notify(send_to: A, use_icons=True, nthreads=20):
    queue = Queue()
    threads = start_workers(queue, nthreads)
    runserver(queue, threads)

    with Connection() as connection:
        subjects = get_subjects(connection, queue)

        for i, _ in enumerate(subjects):
            queue.put(subjects[i])

        queue.join()

        return send_report(subjects, use_icons, send_to)

"""File downloader for the Virtual Campus of the Valladolid Unversity."""
import logging
import re
import time
from queue import Queue

from bs4 import BeautifulSoup
from colorama import init as init_colorama, Fore

from vcm import Options
from vcm.core._requests import Connection
from vcm.core._threading import start_workers
from vcm.core.exceptions import LoginError
from vcm.core.modules import Modules
from vcm.core.status_server import runserver
from vcm.core.time_operations import seconds_to_str
from .subject import Subject

logger = logging.getLogger(__name__)


def get_subjects(connection, queue):
    request = connection.get(connection.user_url)
    soup = BeautifulSoup(request.text, 'html.parser')
    primary_li = soup.find_all('li', class_='contentnode')[3]

    lis = primary_li.find_all('li')
    logger.debug('Found %d potential subjects', len(lis))
    subjects = []

    for li in lis:
        course_id = re.search(r'course=(\d+)', li.a['href']).group(1)
        subject_url = 'https://campusvirtual.uva.es/course/view.php?id=%s' % course_id
        name = re.search(r'^([\w\s]+?)\s?\(', li.text).group(1)

        if 'grado' in name.lower():
            continue

        logger.debug('Assembling subject %r', name)
        subject = Subject(name, subject_url, connection, queue)
        subjects.append(subject)

    subjects.sort(key=lambda x: x.name)
    return subjects


def find_subjects(connection, queue, nthreads=20, no_killer=False):
    """Starts finding subjects.

    Args:
        connection (Connection): custom session with retry control.
        queue (Queue): queue to organize threads.
        nthreads (int): number of threads to start.
        no_killer (bool): desactivate Killer thread.

    """
    logger.debug('Finding subjects')

    threads = start_workers(queue, nthreads, no_killer=no_killer)
    runserver(queue, threads)

    subjects = get_subjects(connection, queue)

    for i, _ in enumerate(subjects):
        queue.put(subjects[i])

    return subjects


def download(nthreads=None, no_killer=False):
    """Starts the app.

    Args:
        nthreads (int): number of threads to start.
        no_killer (bool): desactivate Killer thread.
    """

    Options.set_module(Modules.download)
    init_colorama()

    if not nthreads:
        nthreads = 50

    initial_time = time.time()
    logger.info('STARTING APP')
    logger.debug('Starting queue')
    queue = Queue()

    logger.debug('Launching subjects finder')

    try:
        with Connection() as connection:
            find_subjects(connection, queue, nthreads, no_killer)

            logger.debug('Waiting for queue to empty')
            queue.join()
    except LoginError:
        exit(Fore.RED + 'Login not correct' + Fore.RESET)

    final_time = time.time() - initial_time
    logger.info('VCM downloader executed in %s', seconds_to_str(final_time))

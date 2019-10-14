"""File downloader for the Virtual Campus of the Valladolid Unversity."""
import logging
import re
from queue import Queue

from bs4 import BeautifulSoup
from colorama import Fore
from colorama import init as init_colorama

from vcm.core._threading import start_workers
from vcm.core.exceptions import LoginError
from vcm.core.modules import Modules
from vcm.core.networking import Connection
from vcm.core.results import Results
from vcm.core.settings import GeneralSettings
from vcm.core.status_server import runserver
from vcm.core.utils import timing, Printer

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
        _subject = Subject(name, subject_url, connection, queue)
        subjects.append(_subject)

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


@timing(name='VCM downloader')
def download(nthreads=None, no_killer=False):
    """Starts the app.

    Args:
        nthreads (int): number of threads to start.
        no_killer (bool): desactivate Killer thread.
    """

    Modules.set_current(Modules.download)
    init_colorama()
    if quiet:
        Printer.silence()

    if not nthreads:
        nthreads = 50

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

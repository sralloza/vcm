"""File downloader for the Virtual Campus of the Valladolid Unversity."""
import logging
import os
import re
import time
from logging.handlers import RotatingFileHandler
from queue import Queue
from threading import current_thread

from bs4 import BeautifulSoup
from colorama import init as init_colorama, Fore

from .exceptions import LoginError
from ._requests import Downloader, Connection
from ._threading import start_workers
from .credentials import Credentials
from .options import Options
from .status_server import runserver
from .subject import Subject
from .time_operations import seconds_to_str

if os.environ.get('TESTING') is None:
    should_roll_over = os.path.isfile(Options.LOG_PATH)

    fmt = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
    handler = RotatingFileHandler(filename=Options.LOG_PATH, maxBytes=2_500_000,
                                  encoding='utf-8', backupCount=5)

    current_thread().setName('MT')

    if should_roll_over:
        handler.doRollover()

    logging.basicConfig(handlers=[handler, ], level=Options.LOGGING_LEVEL, format=fmt)

logging.getLogger('urllib3').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


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

    for i, _ in enumerate(subjects):
        queue.put(subjects[i])

    return subjects


def start(nthreads=None, no_killer=False):
    """Starts the app.

    Args:
        nthreads (int): number of threads to start.
        no_killer (bool): desactivate Killer thread.
    """

    init_colorama()

    if not nthreads:
        nthreads = 50

    initial_time = time.time()
    main_logger = logging.getLogger(__name__)
    main_logger.info('STARTING APP')
    main_logger.debug('Starting queue')
    queue = Queue()

    main_logger.debug('Launching subjects finder')

    try:
        with Connection() as connection:
            find_subjects(connection, queue, nthreads, no_killer)

            main_logger.debug('Waiting for queue to empty')
            queue.join()
    except LoginError:
        exit(Fore.RED + 'Login not correct' + Fore.RESET)

    final_time = time.time() - initial_time
    main_logger.info('VCD executed in %s', seconds_to_str(final_time))

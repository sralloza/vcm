"""File downloader for the Virtual Campus of the Valladolid Unversity."""
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from queue import Queue
from threading import current_thread

from bs4 import BeautifulSoup
from colorama import init

from ._requests import Downloader
from ._threading import start_workers
from .credentials import Credentials
from .options import Options
from .status_server import runserver
from .subject import Subject
from .time_operations import seconds_to_str

if os.path.isdir('logs') is False:
    os.mkdir('logs')

if os.environ.get('TESTING') is None:
    should_roll_over = os.path.isfile('logs/vcd.log')

    old_reliable = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
    handler = RotatingFileHandler(filename='logs/vcd.log', maxBytes=2_500_000,
                                  encoding='utf-8', backupCount=5)

    current_thread().setName('MT')

    if should_roll_over:
        handler.doRollover()

    logging.basicConfig(handlers=[handler, ], level=logging.DEBUG, format=old_reliable)

logging.getLogger('urllib3').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


# noinspection PyShadowingNames
def find_subjects(downloader, queue, nthreads=20):
    """Starts finding subjects.

    Args:
        downloader (Downloader): custom session with retry control.
        queue (Queue): queue to organize threads.
        nthreads (int): number of threads to start.

    Returns:

    """
    logger = logging.getLogger(__name__)
    logger.debug('Finding subjects')

    threads = start_workers(queue, nthreads)
    runserver(queue, threads)

    user = Credentials.get('sralloza')

    downloader.post(
        'https://campusvirtual.uva.es/login/index.php',
        data={'anchor': '', 'username': user.username, 'password': user.password})

    response = downloader.get('https://campusvirtual.uva.es/my/')

    logger.debug('Returned primary response with code %d', response.status_code)

    logger.debug('Login correct: %s', 'Vista general de cursos' in response.text)

    if 'Vista general de cursos' not in response.text:
        exit('ERROR: Login not correct')

    soup = BeautifulSoup(response.content, 'html.parser')
    search = soup.findAll('div', {'class': 'course_title'})

    logger.debug('Found %d potential subjects', len(search))
    subjects = []

    for find in search:
        name = find.h2.a['title'].split(' (')[0]
        subject_url = find.h2.a['href']

        if 'grado' in name.lower():
            continue

        logger.debug('Assembling subject %r', name)
        subjects.append(Subject(name, subject_url, downloader, queue))

    subjects.sort(key=lambda x: x.name)

    for i, _ in enumerate(subjects):
        queue.put(subjects[i])

    return subjects


def start(root_folder=None, nthreads=50, timeout=None):
    """Starts the app."""
    init()

    if root_folder:
        Options.set_root_folder(root_folder)

    if timeout:
        Options.set_timeout(timeout)

    initial_time = time.time()
    main_logger = logging.getLogger(__name__)
    main_logger.info('STARTING APP')
    main_logger.debug('Starting downloader')
    downloader = Downloader()
    main_logger.debug('Starting queue')
    queue = Queue()

    main_logger.debug('Launching subjects finder')
    find_subjects(downloader, queue, nthreads)

    main_logger.debug('Waiting for queue to empty')
    queue.join()

    final_time = time.time() - initial_time
    main_logger.info('VCD executed in %s', seconds_to_str(final_time))

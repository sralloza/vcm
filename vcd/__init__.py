"""File downloader for the Virtual Campus of the Valladolid Unversity."""

import time
from queue import Queue

from bs4 import BeautifulSoup

from vcd._threading import start_workers
from vcd.credentials import Credentials
from vcd.globals import get_logger
from vcd.requests import Downloader
from vcd.subject import Subject


# noinspection PyShadowingNames
def find_subjects(downloader, queue, condition=None, nthreads=20):
    """Starts finding subjects.

    Args:
        downloader (Downloader): custom session with retry control.
        queue (Queue): queue to organize threads.
        condition (str|None): optional filter of subjects name.
        condition (str): optional filter of subjects name.
        nthreads (int): number of threads to start.

    Returns:

    """
    logger = get_logger(__name__)
    logger.debug('Finding subjects')

    user = Credentials.get('sralloza')

    downloader.post(
        'https://campusvirtual.uva.es/login/index.php',
        data={'anchor': '', 'username': user.username, 'password': user.password})

    response = downloader.get('https://campusvirtual.uva.es/my/')

    logger.debug('Returned primary response with code %d', response.status_code)

    logger.debug('Login correct: %s', 'Vista general de cursos' in response.text)

    if 'Vista general de cursos' in response.text is False:
        raise RuntimeError('Login not correct')

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

    start_workers(queue, nthreads)
    for i, _ in enumerate(subjects):
        if condition is None:
            queue.put(subjects[i])
        else:
            if condition in subjects[i].name.lower():
                queue.put(subjects[i])

    return subjects


def start():
    """Starts the app."""
    initial_time = time.time()
    main_logger = get_logger(__name__)
    main_logger.info('STARTING APP')
    main_logger.debug('Starting downloader')
    downloader = Downloader()
    main_logger.debug('Starting queue')
    queue = Queue()
    condition = None
    nthreads = 30

    main_logger.debug('Launching subjects finder')
    find_subjects(downloader, queue, condition, nthreads)

    main_logger.debug('Waiting for queue to empty')
    queue.join()

    final_time = time.time() - initial_time
    main_logger.info('DONE (%.2f seconds)', final_time)


if __name__ == '__main__':
    start()

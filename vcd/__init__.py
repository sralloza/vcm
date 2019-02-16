import time
from queue import Queue

from bs4 import BeautifulSoup

from vcd._threading import start_workers
from vcd.credentials import Credentials
from vcd.downloader import Downloader
from vcd.globals import get_logger
from vcd.subject import Subject


# noinspection PyShadowingNames
def find_subjects(downloader, queue, condition=None, n=20):
    logger = get_logger(__name__)
    logger.debug('Finding subjects')

    user = Credentials.get('sralloza')

    downloader.post(
        'https://campusvirtual.uva.es/login/index.php',
        data={'anchor': '', 'username': user['username'], 'password': user['password']})

    r1 = downloader.get('https://campusvirtual.uva.es/my/')

    logger.debug('Returned primary response with code %d', r1.status_code)

    login_correct = 'Vista general de cursos' in r1.text
    logger.debug('Login correct: %s', login_correct)

    if login_correct is False:
        raise RuntimeError('Login not correct')

    soup = BeautifulSoup(r1.content, 'html.parser')
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

    start_workers(queue, n)
    for i, _ in enumerate(subjects):
        if condition is None:
            queue.put(subjects[i])
        else:
            if condition in subjects[i].name.lower():
                queue.put(subjects[i])

    return subjects


if __name__ == '__main__':
    t0 = time.time()
    main_logger = get_logger(__name__)
    main_logger.info('STARTING APP')
    main_logger.debug('Starting downloader')
    downloader = Downloader()
    main_logger.debug('Starting queue')
    queue = Queue()
    condition = None
    n = 30

    main_logger.debug('Launching subjects finder')
    find_subjects(downloader, queue, condition, n)

    main_logger.debug('Waiting for queue to empty')
    queue.join()

    tf = time.time() - t0
    main_logger.info('DONE (%.2f seconds)', tf)

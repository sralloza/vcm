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
from vcm.core.utils import Printer, timing

from .subject import Subject

logger = logging.getLogger(__name__)


def get_subjects(queue):
    connection = Connection()
    request = connection.get(connection.user_url)
    soup = BeautifulSoup(request.text, "html.parser")
    primary_li = soup.find_all("li", class_="contentnode")[3]

    lis = primary_li.find_all("li")
    logger.debug("Found %d potential subjects", len(lis))
    subjects = []

    for li in lis:
        course_id = int(re.search(r"course=(\d+)", li.a["href"]).group(1))
        subject_url = "https://campusvirtual.uva.es/course/view.php?id=%d" % course_id
        name = re.search(r"^([\w\s]+?)\s?\(", li.text).group(1)

        if course_id in GeneralSettings.exclude_subjects_ids:
            logger.info("Excluding subject %s (%d)", name, course_id)
            continue

        # Don't consider subject if 'grado' is in the name (it is the degree itself)
        if "grado" in name.lower():
            continue

        logger.debug("Assembling subject %r", name)
        _subject = Subject(name, subject_url, queue)
        subjects.append(_subject)

    subjects.sort(key=lambda x: x.name)
    return subjects


def find_subjects(queue):
    """Starts finding subjects.

    Args:
        queue (Queue): queue to organize threads.

    """
    logger.debug("Finding subjects")

    subjects = get_subjects(queue)

    for i, _ in enumerate(subjects):
        queue.put(subjects[i])

    return subjects


@timing(name="VCM downloader")
def download(nthreads=20, no_killer=False, status_server=True):
    """Starts the app.

    Args:
        nthreads (int): number of threads to start.
        no_killer (bool): desactivate Killer thread.
    """

    Modules.set_current(Modules.download)
    init_colorama()

    logger.info("STARTING APP")
    logger.debug("Starting queue")
    queue = Queue()

    logger.debug("Launching subjects finder")

    threads = start_workers(queue, nthreads, no_killer=no_killer)

    if status_server:
        runserver(queue, threads)

    with Connection():
        find_subjects(queue)
        logger.debug("Waiting for queue to empty")
        queue.join()

"""File downloader for the Virtual Campus of the Valladolid Unversity."""
import logging
from queue import Queue
import re

from bs4 import BeautifulSoup
from colorama import init as init_colorama

from vcm.core.modules import Modules
from vcm.core.networking import Connection
from vcm.core.settings import GeneralSettings
from vcm.core.status_server import runserver
from vcm.core.tasks import start_workers
from vcm.core.utils import timing

from .subject import Subject


def get_subjects(queue):
    logger = logging.getLogger(__name__)

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


def find_subjects(queue, discover_only=False):
    """Starts finding subjects.

    Args:
        queue (Queue): queue to organize threads.

    """
    logger = logging.getLogger(__name__)
    logger.debug("Finding subjects")

    subjects = get_subjects(queue)

    if discover_only:
        logger.info("Discovery done")
        return subjects

    for i, _ in enumerate(subjects):
        queue.put(subjects[i])

    return subjects


@timing(name="VCM downloader")
def download(nthreads=20, no_killer=False, status_server=True, discover_only=False):
    """

    Args:
        nthreads (int, optional): number of threads to use. Defaults to 20.
        no_killer (bool, optional): if True, an extra thread will be launched
            to detect key pressings, shuch as K for kill the app. Defaults to False.
        status_server (bool, optional): if true, a http server will be opened
            in port 80 to show the status of each thread. Defaults to True.
        discover_only (bool, optional): if true, it will only discover the subjects,
            without downloading anything. Defaults to False.
    """

    logger = logging.getLogger(__name__)
    logger.info(
        "Launching notify(nthreads=%r, no_killer=%s, status_server=%s, discover_only=%s)",
        nthreads,
        no_killer,
        status_server,
        discover_only,
    )

    Modules.set_current(Modules.download)
    init_colorama()

    queue = Queue()
    threads = start_workers(queue, nthreads, no_killer=no_killer)

    if status_server:
        runserver(queue, threads)

    with Connection():
        find_subjects(queue, discover_only=discover_only)
        logger.debug("Waiting for queue to empty")
        queue.join()

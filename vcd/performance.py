import csv
import logging
import time
from queue import Queue


from vcd import get_logger, find_subjects, Downloader

logger = get_logger(__name__, level=logging.DEBUG, filename='performance.log')


# noinspection PyShadowingNames
def check_if_exists(n):
    with open('performance.csv', 'rt', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        ns = [x['n'] for x in reader]

    return str(n) in ns


# noinspection PyShadowingNames
def save_value(n: int, tf: float):
    with open('performance.csv', 'at', newline='') as csvfile:
        fieldnames = ['n', 'tf']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'n': n, 'tf': tf})


# noinspection PyShadowingNames
def performance_test(n):
    if check_if_exists(n):
        logger.debug('Skipping n=%d because it is already registered', n)
        return

    t0 = time.time()
    downloader = Downloader()
    queue = Queue()
    condition = None

    logger.debug('Launching subjects finder with n=%d', n)
    find_subjects(downloader, queue, condition, n)

    queue.join()

    tf = time.time() - t0
    logger.info('DONE FOR n=%d (%.2f seconds)', n, tf)
    save_value(n, tf)


if __name__ == '__main__':
    logger.debug('Starting tests')

    for n in range(1, 400):
        performance_test(n)

    logger.debug('Finished tests')

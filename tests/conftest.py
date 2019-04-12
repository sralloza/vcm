import logging
import os
import shutil
from threading import current_thread

import pytest


def pytest_configure():
    os.environ['TESTING'] = '1'

    from vcd import Options
    Options.set_root_folder('temp_tests')

    old_reliable = "[%(asctime)s] %(levelname)s - %(threadName)s.%(module)s:%(lineno)s - %(message)s"
    handler = logging.FileHandler(filename='testing.log', encoding='utf-8')

    current_thread().setName('MT')

    logging.basicConfig(handlers=[handler, ], level=logging.DEBUG, format=old_reliable)
    logging.getLogger('urllib3').setLevel(logging.ERROR)


@pytest.fixture(scope='session', autouse=True)
def teardown_everything():
    yield
    shutil.rmtree('temp_tests')

    logging.shutdown()
    os.remove('testing.log')

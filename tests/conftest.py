import logging
import shutil

import pytest

from vcd import Options

def pytest_configure():
    Options.set_root_folder('temp-tests')


# @pytest.fixture(scope='session', autouse=True)
# def teardown_everything():
#     yield
#     shutil.rmtree('temp-tests')
#
#     logging.shutdown()
#     shutil.rmtree('logs')
from pathlib import Path
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import versioneer

version = versioneer.get_version()
cmdclass = versioneer.get_cmdclass()
requirements = Path(__file__).with_name("requirements.txt").read_text().splitlines()


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


cmdclass["test"] = PyTest

setup(
    name="vcm",
    url="https://github.com/sralloza/vcm.git",
    description="File scanner and downloader of campusvirtual.uva.es",
    version=version,
    author="Diego Alloza",
    entry_points={"console_scripts": ["vcm=vcm.main:main"]},
    include_package_data=True,
    author_email="admin@sralloza.es",
    packages=["vcm", "vcm.core", "vcm.notifier", "vcm.downloader"],
    install_requires=requirements,
    package_data={"vcm": ["VERSION"]},
    tests_require=["pytest", "coverage"],
    cmdclass=cmdclass,
    zip_safe=False,
)

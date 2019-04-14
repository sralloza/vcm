import os

import pytest
from colorama import Fore

from vcd.results import Results


def setup_module():
    Results.result_path = 'new-files-test.txt'


def test_print_updated(capsys):
    Results.print_updated('Updated: something-1')

    out, err = capsys.readouterr()
    assert err == ''
    assert out == Fore.LIGHTYELLOW_EX + 'Updated: something-1\n'


def test_print_new(capsys):
    Results.print_new('New: something-2')

    out, err = capsys.readouterr()
    assert err == ''
    assert out == Fore.LIGHTGREEN_EX + 'New: something-2\n'


def test_add_to_result_file():
    with open(Results.result_path, encoding='utf-8') as f:
        c = f.read()

    assert 'Updated: something-1' in c
    assert 'New: something-2' in c

    os.remove(Results.result_path)
    assert not os.path.isfile(Results.result_path)


@pytest.fixture(scope='module', autouse=True)
def reset_color():
    print(Fore.RESET, end='')
    yield
    print(Fore.RESET, end='')

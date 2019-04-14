import pytest
from colorama import Fore

from vcd.results import Results


def test_print_updated(capsys):
    Results.print_updated('Updated: something-1')

    out, err = capsys.readouterr()
    assert err == ''
    assert out == '\x1b[93mUpdated: something-1\n'


def test_print_new(capsys):
    Results.print_updated('New: something-1')

    out, err = capsys.readouterr()
    assert err == ''
    assert out == '\x1b[93mNew: something-1\n'


@pytest.fixture(scope='module', autouse=True)
def reset_color():
    print(Fore.RESET, end='')
    yield
    print(Fore.RESET, end='')
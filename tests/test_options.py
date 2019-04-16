import os

import pytest

from vcd import Options


def test_filename_pattern():
    pat = Options.FILENAME_PATTERN
    assert pat.search('filename="federico.txt"').group(1) == 'federico.txt'
    assert pat.search('filename="a la meca.rar"').group(1) == 'a la meca.rar'
    assert pat.search('filename="dummy.txt').group(1) == 'dummy.txt'
    assert pat.search('filename=dummy.txt"').group(1) == 'dummy.txt'


def test_set_root_folder():
    root_folder = Options.ROOT_FOLDER
    temp_folder = 'temp-root-folder-to-delete'

    assert not os.path.isdir(temp_folder)
    Options.set_root_folder(temp_folder)
    assert os.path.isdir(temp_folder)

    Options.set_root_folder(root_folder)
    assert os.path.isdir(root_folder)

    os.rmdir(temp_folder)
    assert not os.path.isdir(temp_folder)


# noinspection PyTypeChecker
def test_set_timeout():
    Options.set_timeout(1)
    assert Options.TIMEOUT == 1

    Options.set_timeout(2)
    assert Options.TIMEOUT == 2

    with pytest.raises(TypeError, 'Timeout must be int, not'):
        Options.set_timeout('3')
    with pytest.raises(TypeError, 'Timeout must be int, not'):
        Options.set_timeout(False)
    with pytest.raises(TypeError, 'Timeout must be int, not'):
        Options.set_timeout(None)
    with pytest.raises(TypeError, 'Timeout must be int, not'):
        Options.set_timeout(1 + 2j)
    with pytest.raises(TypeError, 'Timeout must be int, not'):
        Options.set_timeout(7.22)
    with pytest.raises(TypeError, 'Timeout must be int, not'):
        Options.set_timeout([3, 2])
    with pytest.raises(TypeError, 'Timeout must be int, not'):
        Options.set_timeout((2, 3))

    Options.set_timeout(30)

# todo test Options.load_config

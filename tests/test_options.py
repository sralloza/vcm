import os

from vcd import Options


def test_filename_pattern():
    pat = Options.FILENAME_PATTERN
    assert pat.search('filename="federico.txt"').group(1) == 'federico.txt'
    assert pat.search('filename="a la meca.rar"').group(1) == 'a la meca.rar'
    assert pat.search('filename="dummy.txt').group(1) == 'dummy.txt'
    assert pat.search('filename=dummy.txt"').group(1) == 'dummpy.txt'


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

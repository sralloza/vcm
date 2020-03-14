from unittest import mock

import pytest

import vcm
from vcm.core.utils import Patterns, check_updates


class TestPatterns:
    filename_data = (
        ('filename="a.txt"', "a.txt"),
        ('filename="cool.html"', "cool.html"),
        ('filename="hello-there-93.jpg"', "hello-there-93.jpg"),
        ('filename="consider spacing true.txt"', "consider spacing true.txt"),
        ('filename="IS_BI_2_20.xlsx"', "IS_BI_2_20.xlsx"),
        ('filename="important (2020_2021).pdf"', "important (2020_2021).pdf"),
        ('filename="accents [áéíóúñÁÉÍÓÚÑ]()"', "accents [áéíóúñÁÉÍÓÚÑ]()"),
        ('filename="-.,_;~+`^´¨{[]\'¡¿!@#·$%&/€"', "-.,_;~+`^´¨{[]\'¡¿!@#·$%&/€"),
        ('filename="-.,_:;~+`*^´¨{[]\'¡¿?!|@#·$%&/"', None)

    )
    @pytest.mark.parametrize("input_str, expected", filename_data)
    def test_filename_pattern(self, input_str, expected):
        match = Patterns.FILENAME_PATTERN.search(input_str)

        if expected:
            assert match.group(1) == expected
        else:
            assert match is None



class TestCheckUpdates:
    version_data = (
        ("3.0.1", "3.0.2", True),
        ("3.0.0", "3.0.1", True),
        ("2.1.1", "3.0.0", True),
        ("2.1.0", "2.1.1", True),
        ("2.0.1", "2.1.0", True),
    )

    version_data = version_data + tuple([[x[1], x[0], False] for x in version_data])

    @pytest.fixture
    def mocks(self):
        con_mock = mock.patch("vcm.core.networking.connection").start()
        print_mock = mock.patch("vcm.core.utils.Printer.print").start()

        yield con_mock, print_mock

        mock.patch.stopall()

    @pytest.mark.parametrize("version1, version2, new_update", version_data)
    def test_check_updates(self, mocks, version1, version2, new_update):
        con_mock, print_mock = mocks

        response_mock = mock.MagicMock()
        response_mock.text = version2
        con_mock.get.return_value = response_mock

        vcm.version = version1

        result = check_updates()

        assert result == new_update
        print_mock.assert_called_once()


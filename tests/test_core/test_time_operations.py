from unittest import mock

import pytest

from tests.test_core.time_operations_ci_test_data import SECONDS_TO_STR_TEST_DATA
from vcm.core.exceptions import InvalidLanguageError
from vcm.core.time_operations import (
    ALPHABET,
    LANGUAGES,
    Language,
    gen_part,
    join_parts,
    seconds_to_str,
    split_seconds,
)


def test_alphabet():
    assert isinstance(ALPHABET, dict)

    for key in ALPHABET:
        assert isinstance(ALPHABET[key], dict)
        for subkey in ALPHABET[key]:
            assert isinstance(ALPHABET[key][subkey], list)

    assert "abbr" in ALPHABET
    assert "default" in ALPHABET


def test_language_interface():
    lang = Language(*list("abcdef"))
    assert hasattr(lang, "day")
    assert hasattr(lang, "hour")
    assert hasattr(lang, "minute")
    assert hasattr(lang, "second")
    assert hasattr(lang, "s")
    assert hasattr(lang, "join")


def test_languages():
    langs_keys = list(ALPHABET[list(ALPHABET.keys())[0]].keys())
    assert isinstance(LANGUAGES, dict)

    for value in LANGUAGES.values():
        assert isinstance(value, dict)
        for lang_key in langs_keys:
            assert lang_key in value
            assert isinstance(value[lang_key], Language)


class TestSecondsToStr:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.ss_m = mock.patch("vcm.core.time_operations.split_seconds").start()
        self.gp_m = mock.patch("vcm.core.time_operations.gen_part").start()
        self.jp_m = mock.patch("vcm.core.time_operations.join_parts").start()

        yield

        mock.patch.stopall()

    def test_type_error(self):
        with pytest.raises(
            TypeError, match="seconds must be float or int, not complex"
        ):
            seconds_to_str(2 + 5j)

        self.jp_m.assert_not_called()
        self.gp_m.assert_not_called()
        self.ss_m.assert_not_called()

    def test_invalid_language_error(self):
        expected_match = "'<invalid-language>' is not a valid language"
        with pytest.raises(InvalidLanguageError, match=expected_match):
            seconds_to_str(2, language="<invalid-language>")

        self.jp_m.assert_not_called()
        self.gp_m.assert_not_called()
        self.ss_m.assert_not_called()

    @pytest.mark.parametrize("inf", [float("inf"), float("-inf")])
    @pytest.mark.parametrize("lang", ALPHABET["default"].keys())
    def test_infinite_seconds(self, inf, lang):
        result = seconds_to_str(inf, language=lang)
        assert result == "infinite " + ALPHABET["default"][lang][0] + "s"

    @pytest.mark.parametrize("is_empty", [True, False])
    @mock.patch("vcm.core.time_operations.LANGUAGES")
    def test_ok(self, langs_m, is_empty):
        self.ss_m.return_value = (10, 20, 30, 40)
        lang = mock.MagicMock()
        langs_m.__getitem__.return_value.__getitem__.return_value = lang
        lang.t = "h"

        if is_empty:
            self.jp_m.return_value = None

        parts = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        self.gp_m.side_effect = parts

        seconds_to_str(2)
        langs_m.__getitem__.assert_called_once()
        langs_m.__getitem__.return_value.__getitem__.assert_called_once()

        self.ss_m.assert_called_once()
        self.gp_m.assert_any_call(10, lang.day, lang.s, False)
        self.gp_m.assert_any_call(20, lang.hour, lang.s, False)
        self.gp_m.assert_any_call(30, lang.minute, lang.s, False)
        self.gp_m.assert_any_call(40, lang.second, lang.s, False)
        self.jp_m.assert_called_once_with(lang.join, *parts[:-1])

        if is_empty:
            self.gp_m.assert_any_call(0, lang.second, lang.s, False, force_output=True)
            assert self.gp_m.call_count == 5
        else:
            assert self.gp_m.call_count == 4


class TestGenPart:
    test_data_force = (
        (4, "second", False, "4 seconds"),
        (5, "s", True, "5s"),
        (0, "second", False, "0 seconds"),
        (0, "s", True, "0s"),
        (1, "second", False, "1 second"),
        (1, "s", True, "1s"),
        (2, "second", False, "2 seconds"),
        (2, "s", True, "2s"),
        (0, "s", True, "0s"),
    )

    test_data_no_force = [
        x if x[0] != 0 else (0, x[1], x[2], None) for x in test_data_force
    ]

    @pytest.mark.parametrize("int_part, str_part, space, expected", test_data_no_force)
    def test_not_force_output(self, int_part, str_part, space, expected):
        result = gen_part(int_part, str_part, "s", space, force_output=False)
        assert result == expected

    @pytest.mark.parametrize("int_part, str_part, space, expected", test_data_force)
    def test_force_output(self, int_part, str_part, space, expected):
        result = gen_part(int_part, str_part, "s", space, force_output=True)
        assert result == expected


@pytest.mark.parametrize(
    "output, parts",
    [
        ("1", list("1")),
        ("1 y 2", list("12")),
        ("1, 2 y 3", list("123")),
        ("1, 2, 3 y 4", list("1234")),
        ("1 y 2", ["1", None, None, "2"]),
        (None, [None] * 9),
        (None, []),
    ],
)
def test_join_parts(output, parts):
    result = join_parts("y", *parts)
    assert result == output


class TestSplitSeconds:
    test_normal_data = [
        (0, (0, 0, 0)),
        (1, (0, 0, 1)),
        (2, (0, 0, 2)),
        (31, (0, 0, 31)),
        (60, (0, 1, 0)),
        (61, (0, 1, 1)),
        (62, (0, 1, 2)),
        (129, (0, 2, 9)),
        (4321, (1, 12, 1)),
        (654321, (181, 45, 21)),
    ]

    @pytest.mark.parametrize("seconds, output", test_normal_data)
    def test_normal_int_no_days(self, seconds, output):
        result = split_seconds(seconds)
        assert result == output

    test_normal_data_days = [
        (65, (0, 0, 1, 5)),
        (129, (0, 0, 2, 9)),
        (4321, (0, 12, 1)),
        (86400, (1, 0, 0, 0)),
        (654321, (7, 13, 45, 21)),
    ]

    @pytest.mark.parametrize("seconds, output", test_normal_data)
    def test_normal_int_with_days(self, seconds, output):
        result = split_seconds(seconds)
        assert result == output

    test_integer_argument_data = [
        (13.54, None, (0, 0, 13.54)),
        (13.54, False, (0, 0, 13.54)),
        (13.54, True, (0, 0, 14)),
        (13.33, None, (0, 0, 13.33)),
        (13.33, False, (0, 0, 13.33)),
        (13.33, True, (0, 0, 13)),
        (0.33, None, (0, 0, 0.33)),
        (0.33, False, (0, 0, 0.33)),
        (0.33, True, (0, 0, 0)),
        (0.0, None, (0, 0, 0.0)),
        (0.0, False, (0, 0, 0)),  # This is the special behavior of integer=False
        (0.0, True, (0, 0, 0)),
    ]

    @pytest.mark.parametrize("seconds, integer, output", test_integer_argument_data)
    def test_integer_argument(self, seconds, integer, output):
        result = split_seconds(seconds, integer=integer)
        assert result == output


class TestSecondsToStringIntegration:
    @pytest.fixture(params=[True, False])
    def use_abbr(self, request):
        return request.param

    @pytest.fixture(params=["es", "en"])
    def language(self, request):
        return request.param

    @pytest.mark.parametrize(
        "lang, is_ok", [(x, True) for x in ALPHABET["default"]] + [("inv", False)]
    )
    def test_languages(self, lang, is_ok):
        if is_ok:
            seconds_to_str(0, language=lang)
        else:
            with pytest.raises(InvalidLanguageError, match=r"'\w+' is not a valid"):
                seconds_to_str(0, language=lang)

    @mock.patch("vcm.core.time_operations.split_seconds")
    @pytest.mark.parametrize("time_tuple", SECONDS_TO_STR_TEST_DATA.keys())
    def test_integration(self, ss_m, use_abbr, language, time_tuple):
        ss_m.return_value = time_tuple
        expected = SECONDS_TO_STR_TEST_DATA[time_tuple][(use_abbr, language)]
        real = seconds_to_str(0, abbreviated=use_abbr, language=language)
        assert real == expected

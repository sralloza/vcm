from unittest import mock

import pytest

from tests.test_core.time_operations_test_data import (
    SECONDS_TO_STR_TEST_DATA,
    SPLIT_SECONDS_TEST_DATA,
)
from vcm.core.exceptions import InvalidLanguageError
from vcm.core.time_operations import ALPHABET, seconds_to_str


def test_alphabet():
    assert isinstance(ALPHABET, dict)

    for key in ALPHABET:
        assert isinstance(ALPHABET[key], dict)
        for subkey in ALPHABET[key]:
            assert isinstance(ALPHABET[key][subkey], list)

    assert "abbr" in ALPHABET
    assert "default" in ALPHABET


@mock.patch("vcm.core.time_operations._split_seconds")
@mock.patch("vcm.core.time_operations.gen_part")
@mock.patch("vcm.core.time_operations.join_parts")
class TestSecondsToStr:
    def test_type_error(self, jp_m, gp_m, ss_m):
        with pytest.raises(
            TypeError, match="seconds must be float or int, not complex"
        ):
            seconds_to_str(2 + 5j)

        jp_m.assert_not_called()
        gp_m.assert_not_called()
        ss_m.assert_not_called()

    def test_invalid_language_error(self, jp_m, gp_m, ss_m):
        expected_match = "'<invalid-language>' is not a valid language"
        with pytest.raises(InvalidLanguageError, match=expected_match):
            seconds_to_str(2, language="<invalid-language>")

        jp_m.assert_not_called()
        gp_m.assert_not_called()
        ss_m.assert_not_called()

    @pytest.mark.parametrize("inf", [float("inf"), float("-inf")])
    @pytest.mark.parametrize("lang", ALPHABET["default"].keys())
    def test_infinite_seconds(self, jp_m, gp_m, ss_m, inf, lang):
        result = seconds_to_str(inf, language=lang)
        assert result == "infinite " + ALPHABET["default"][lang][0] + "s"

    @pytest.mark.parametrize("is_empty", [True, False])
    @mock.patch("vcm.core.time_operations.LANGUAGES")
    def test_ok(self, langs_m, jp_m, gp_m, ss_m, is_empty):
        ss_m.return_value = (10, 20, 30, 40)
        lang = mock.MagicMock()
        langs_m.__getitem__.return_value.__getitem__.return_value = lang
        lang.t = "h"

        if is_empty:
            jp_m.return_value = None

        parts = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        gp_m.side_effect = parts

        seconds_to_str(2)
        langs_m.__getitem__.assert_called_once()
        langs_m.__getitem__.return_value.__getitem__.assert_called_once()

        ss_m.assert_called_once()
        gp_m.assert_any_call(10, lang.day, lang.s, False)
        gp_m.assert_any_call(20, lang.hour, lang.s, False)
        gp_m.assert_any_call(30, lang.minute, lang.s, False)
        gp_m.assert_any_call(40, lang.second, lang.s, False)
        jp_m.assert_called_once_with(lang.join, *parts[:-1])

        if is_empty:
            gp_m.assert_any_call(0, lang.second, lang.s, False, force_output=True)
            assert gp_m.call_count == 5
        else:
            assert gp_m.call_count == 4


@pytest.mark.xfail
def test_gen_part():
    # def gen_part(int_part, str_part, possible_s, include_space, force_output=False):
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_join_parts():
    # def join_parts(join_str, *string_parts):
    assert 0, "Not implemented"


@pytest.mark.xfail
class TestSplitSeconds:
    def test_split_seconds(self):
        assert 0, "Not implemented"


class TestSecondsToStringIntegration:
    @pytest.fixture(params=[True, False])
    def use_abbr(self, request):
        return request.param

    @pytest.fixture(params=["es", "en"])
    def language(self, request):
        return request.param

    @pytest.mark.parametrize(
        "lang, ok", [(x, True) for x in ALPHABET["default"]] + [("inv", False)]
    )
    def test_languages(self, lang, ok):
        if ok:
            seconds_to_str(0, language=lang)
        else:
            with pytest.raises(InvalidLanguageError, match=r"'\w+' is not a valid"):
                seconds_to_str(0, language=lang)

    @mock.patch("vcm.core.time_operations._split_seconds")
    @pytest.mark.parametrize("time_tuple", SECONDS_TO_STR_TEST_DATA.keys())
    def test_integration(self, ss_m, use_abbr, language, time_tuple):
        ss_m.return_value = time_tuple
        expected = SECONDS_TO_STR_TEST_DATA[time_tuple][(use_abbr, language)]
        real = seconds_to_str(0, abbreviated=use_abbr, language=language)
        assert real == expected

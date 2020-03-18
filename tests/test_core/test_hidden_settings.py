import pytest

from vcm.core._settings import (
    Checkers,
    Setters,
    exclude_subjects_ids_setter,
    section_indexing_setter,
)
from vcm.core.exceptions import SettingsError


class TestExcludeSubjectIdsSetter:
    @classmethod
    def setup_class(cls):
        cls.default_error_message = (
            "general.exclude-subjects-ids can't be set using the CLI"
        )

    def test_force_ok(self):
        settings = [6518, 215, 23165, 2165, 12356]
        result = exclude_subjects_ids_setter(settings, force=True)
        assert result == settings

    def test_force_false(self):
        settings = [12, 2323]
        with pytest.raises(SettingsError, match=self.default_error_message):
            exclude_subjects_ids_setter(settings, force=False)

    def test_force_error_1(self):
        settings = ["id-1", "id-2", "id-3"]
        err_expected = (
            r"Element 0 \('id-1'\) of exclude-subjects-ids must be int, not str"
        )
        with pytest.raises(TypeError, match=err_expected):
            exclude_subjects_ids_setter(settings, force=True)

    def test_force_error_2(self):
        settings = [654, 64598, 31298, 12384, 312984, "id-1"]
        err_expected = (
            r"Element 5 \('id-1'\) of exclude-subjects-ids must be int, not str"
        )
        with pytest.raises(TypeError, match=err_expected):
            exclude_subjects_ids_setter(settings, force=True)

    def test_no_force(self):
        settings = [245254, 5245]
        with pytest.raises(SettingsError, match=self.default_error_message):
            exclude_subjects_ids_setter(settings)

    def test_weird_args(self):
        settings = []
        exclude_subjects_ids_setter(settings, "fed", 1 + 2j, force=True, hi="there")
        exclude_subjects_ids_setter(settings, 456, 2.135, force=True, nasa=-9)
        exclude_subjects_ids_setter(settings, None, bool, type, force=True, nasa=self)


class TestSectionIndexingSetter:
    @classmethod
    def setup_class(cls):
        cls.default_error_message = (
            "download.section-indexing can't be set using the CLI"
        )

    def test_force_ok(self):
        settings = [6518, 215, 23165, 2165, 12356]
        result = section_indexing_setter(settings, force=True)
        assert result == settings

    def test_force_false(self):
        settings = [12, 2323]
        with pytest.raises(SettingsError, match=self.default_error_message):
            section_indexing_setter(settings, force=False)

    def test_force_error_1(self):
        settings = ["id-1", "id-2", "id-3"]
        err_expected = r"Element 0 \('id-1'\) of section-indexing must be int, not str"
        with pytest.raises(TypeError, match=err_expected):
            section_indexing_setter(settings, force=True)

    def test_force_error_2(self):
        settings = [654, 64598, 31298, 12384, 312984, "id-1"]
        err_expected = r"Element 5 \('id-1'\) of section-indexing must be int, not str"
        with pytest.raises(TypeError, match=err_expected):
            section_indexing_setter(settings, force=True)

    def test_no_force(self):
        settings = [245254, 5245]
        with pytest.raises(SettingsError, match=self.default_error_message):
            section_indexing_setter(settings)

    def test_weird_args(self):
        settings = []
        section_indexing_setter(settings, "fed", 1 + 2j, force=True, hi="there")
        section_indexing_setter(settings, 456, 2.135, force=True, nasa=-9)
        section_indexing_setter(settings, None, bool, type, force=True, nasa=self)


class TestTypes:
    class Log(type):
        pass

    class GoodLog(Log):
        pass

    class BadLog(Log):
        pass

    class Bool(type):
        pass


class TestCheckers:
    checkers_test_data = [
        ("debug", TestTypes.GoodLog),
        ("DEBUG", TestTypes.GoodLog),
        (10, TestTypes.GoodLog),
        (-5, TestTypes.BadLog),
        (5.26, TestTypes.BadLog),
        ("string", str),
        (list(), list),
        (set(), set),
        (dict(), dict),
        (tuple(), tuple),
        (456, int),
        (1 + 2j, complex),
        (True, TestTypes.Bool),
        (None, type(None)),
        (0.256, float),
    ]

    @pytest.mark.parametrize("data, data_type", checkers_test_data)
    def test_logging(self, data, data_type):
        result = Checkers.logging(data)

        if issubclass(data_type, TestTypes.GoodLog):
            assert result is True
        else:
            assert result is False

    @pytest.mark.parametrize("data, data_type", checkers_test_data)
    def test_bool(self, data, data_type):
        result = Checkers.bool(data)

        if issubclass(data_type, TestTypes.Bool):
            assert result is True
        else:
            assert result is False

    @pytest.mark.parametrize("data, data_type", checkers_test_data)
    def test_int(self, data, data_type):
        result = Checkers.int(data)

        if issubclass(data_type, int):
            assert result is True
        else:
            if issubclass(data_type, TestTypes.Log):
                return
            assert result is False

    @pytest.mark.parametrize("data, data_type", checkers_test_data)
    def test_str(self, data, data_type):
        result = Checkers.str(data)

        if issubclass(data_type, str):
            assert result is True
        else:
            if issubclass(data_type, TestTypes.Log):
                return
            assert result is False

    @pytest.mark.parametrize("data, data_type", checkers_test_data)
    def test_list(self, data, data_type):
        result = Checkers.list(data)

        if issubclass(data_type, list):
            assert result is True
        else:
            assert result is False

    @pytest.mark.parametrize("data, data_type", checkers_test_data)
    def test_float(self, data, data_type):
        result = Checkers.float(data)

        if issubclass(data_type, float):
            assert result is True
        else:
            if issubclass(data_type, TestTypes.Log):
                return
            assert result is False


class TestSetters:
    def test_int_no_args(self):
        result = Setters.int("2")
        assert result == 2

    def test_int_force(self):
        result = Setters.int("2", force=True)
        assert result == 2

    def test_list_no_args(self):
        result = Setters.list([])
        assert result == []

    def test_list_force(self):
        result = Setters.list([], force=True)
        assert result == []

    def test_str_no_args(self):
        result = Setters.str("2")
        assert result == "2"

    def test_str_force(self):
        result = Setters.str("2", force=True)
        assert result == "2"


def test_defaults():
    from vcm.core._settings import defaults

    for value in defaults.values():
        assert isinstance(value, dict)
        for value2 in value.values():
            assert not callable(value2)


def test_checkers():
    from vcm.core._settings import checkers

    for value in checkers.values():
        assert isinstance(value, dict)
        for value2 in value.values():
            assert callable(value2)


def test_constructors():
    from vcm.core._settings import constructors

    assert isinstance(constructors, dict)


def test_setters():
    from vcm.core._settings import setters

    assert isinstance(setters, dict)


class TestSettingsDictKeys:
    def get_keys_from_dicts(self, *dicts):
        keys = []
        for dict in dicts:
            keys += list(dict.keys())
        return tuple(set(keys))

    def test_settings_dict_keys(self):
        from vcm.core._settings import defaults, checkers, constructors, setters

        keys = self.get_keys_from_dicts(defaults, checkers, constructors, setters)
        keys = tuple(set(keys))
        for key in keys:
            assert key in defaults
            assert key in checkers
            assert key in constructors
            assert key in setters

            subkeys = self.get_keys_from_dicts(
                defaults[key], checkers[key], constructors[key], setters[key]
            )

            for subkey in subkeys:
                assert subkey in defaults[key]
                assert subkey in checkers[key]
                assert subkey in constructors[key]
                assert subkey in setters[key]

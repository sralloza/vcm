import pytest

from vcm.core._settings import exclude_subjects_ids_setter
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

@pytest.mark.xfail
def test_section_indexing_setter():
    assert 0, "Not implemented"


@pytest.mark.xfail
class TestCheckers:
    def test_logging(self):
        assert 0, "Not implemented"

    def test_bool(self):
        assert 0, "Not implemented"

    def test_int(self):
        assert 0, "Not implemented"

    def test_str(self):
        assert 0, "Not implemented"

    def test_list(self):
        assert 0, "Not implemented"

    def test_float(self):
        assert 0, "Not implemented"


class TestSetters:
    @pytest.mark.xfail
    def test_int(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_list(self):
        assert 0, "Not implemented"

    @pytest.mark.xfail
    def test_str(self):
        assert 0, "Not implemented"


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


@pytest.mark.xfail
def test_constructors():
    assert 0, "Not implemented"


@pytest.mark.xfail
def test_setters():
    assert 0, "Not implemented"


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

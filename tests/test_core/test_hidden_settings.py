def test_exclude_subjects_ids_setter():
    assert 0, "Not implemented"


def test_section_indexing_setter():
    assert 0, "Not implemented"


def test_defaults():
    from vcm.core._settings import defaults

    for value in defaults.values():
        assert isinstance(value, dict)
        for value2 in value.values():
            assert not callable(value2)


def test_types():
    from vcm.core._settings import types

    for value in types.values():
        assert isinstance(value, dict)
        for value2 in value.values():
            assert callable(value2)


def test_constructors():
    assert 0, "Not implemented"


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

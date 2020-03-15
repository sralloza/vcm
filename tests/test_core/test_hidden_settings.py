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

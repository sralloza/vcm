from unittest import mock


@mock.patch("pathlib.Path")
def test_get_version(path_m):
    import vcm

    path_m.return_value.with_name.return_value.read_text.return_value = "testing"

    version = vcm.get_version()
    assert version == "testing"

    path_m.assert_called_with(vcm.__file__)
    path_m.return_value.with_name.assert_called_once_with("VERSION")
    path_m.return_value.with_name.return_value.read_text.assert_called_once()

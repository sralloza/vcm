import sys
from unittest import mock


@mock.patch("vcm._version.get_versions")
def test_get_version(get_versions_m):
    get_versions_m.return_value = {
        "version": "5.1.2",
        "full-revisionid": "<commit-id>",
        "dirty": False,
        "error": None,
        "date": "<date>",
    }

    del sys.modules["vcm"]
    import vcm

    version = vcm.__version__
    assert version == "5.1.2"

    get_versions_m.assert_called_once_with()

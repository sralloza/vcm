import sys
from unittest import mock
import pytest


@pytest.fixture
def reset_vcm_import():
    vcm_import = sys.modules["vcm"]
    del sys.modules["vcm"]
    yield
    sys.modules["vcm"] = vcm_import


@mock.patch("vcm._version.get_versions")
def test_get_version(get_versions_m, reset_vcm_import):
    get_versions_m.return_value = {
        "version": "5.1.2",
        "full-revisionid": "<commit-id>",
        "dirty": False,
        "error": None,
        "date": "<date>",
    }

    import vcm

    version = vcm.__version__
    assert version == "5.1.2"

    get_versions_m.assert_called_once_with()

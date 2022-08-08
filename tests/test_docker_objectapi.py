import pytest

import cmk

import logging


logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.docker, pytest.mark.xdist_group("docker")]


@pytest.fixture
def api():

    with cmk.ObjectAPI("http://localhost:8080/cmk/", "cmkadmin", "cmkadmin") as api:
        yield api


def test_objectapi_notfound(api):
    host = api.HostConfig("not_found")
    assert not host


def test_objectapi(api):
    folder = api.FolderConfig("~test_folder")
    if folder:
        folder.delete()

    folder = api.FolderConfig.create("test_folder")

    assert folder.identifier == "~test_folder"

    subfolder = folder.FolderConfig.create("sub")

    assert subfolder.identifier == "~test_folder~sub"

    subfolder.delete()

    folder.delete()

import pytest

import cmk

import logging


logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.docker, pytest.mark.xdist_group("docker")]


def test_objectapi_notfound():
    api = cmk.ObjectAPI("http://localhost:8080/cmk/", "cmkadmin", "cmkadmin")
    host = api.Host("not_found")
    assert not host


def test_objectapi():
    api = cmk.ObjectAPI("http://localhost:8080/cmk/", "cmkadmin", "cmkadmin")
    folder = api.Folder("~test_folder")
    if folder:
        folder.delete()

    folder = api.Folder.create("test_folder")

    assert folder.identifier == "~test_folder"

    folder.delete()

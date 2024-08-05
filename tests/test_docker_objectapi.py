import pytest

import cmk

import logging


__logger__ = logging.getLogger(__name__)
pytestmark = [pytest.mark.docker, pytest.mark.xdist_group("docker")]


@pytest.fixture
def api():
    with cmk.ObjectAPI("http://localhost:8080/cmk/", "cmkadmin", "cmkadmin") as api:
        yield api


def test_objectapi_notfound(api):
    host = api.HostConfig("not_found")
    assert not host


def test_objectapi_folder(api):
    folder = api.FolderConfig("~test_folder")
    if folder:
        folder.delete()

    folder = api.FolderConfig.create("test_folder")

    assert folder.identifier == "~test_folder"

    subfolder = folder.FolderConfig.create("sub")

    assert subfolder.identifier == "~test_folder~sub"

    test_folder = api.FolderConfig("test_folder").FolderConfig("sub")

    assert test_folder.identifier == "~test_folder~sub"

    assert test_folder

    subfolder.delete()

    folder.delete()


@pytest.mark.parametrize(
    ("class_name"),
    [
        ("ContactGroupConfig"),
        ("HostGroupConfig"),
        ("ServiceGroupConfig"),
    ],
)
def test_objectapi_group_config(api, class_name):
    gc_class = getattr(api, class_name)
    identifier = class_name.lower() + "_name"
    alias = class_name.lower() + "_alias"
    gc = gc_class(identifier)
    if gc:
        gc.delete()

    gc = gc_class.create(identifier, alias)

    assert gc.identifier == identifier
    assert gc.alias == alias

    gc = gc_class(identifier)

    assert gc
    assert gc.identifier == identifier
    assert gc.alias == alias

    for i in gc_class.iter():
        if i.identifier == identifier:
            assert i.alias == alias

    gc.delete()

    gc = gc_class(identifier)
    assert not gc

import pytest

import cmk

import logging


logger = logging.getLogger(__name__)
pytestmark = [pytest.mark.docker, pytest.mark.xdist_group("docker")]


def test_restapi():
    api = cmk.RESTAPI("http://localhost:8080/cmk/", "cmkadmin", "cmkadmin")
    api.create_object(
        "folder_config", name="test_folder", title="Test Folder Title", parent="~"
    )
    host, _ = api.show_object("folder_config", "~test_folder")
    logger.debug(host)
    assert host["title"] == "Test Folder Title"
    api.delete_object("folder_config", "~test_folder")

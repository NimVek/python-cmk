import pytest

import cmk


pytestmark = [pytest.mark.docker, pytest.mark.xdist_group("docker")]


def test_httpapi():
    api = cmk.HTTPAPI("https://localhost:8080/cmk/", "cmkadmin", "cmkadmin")
    api

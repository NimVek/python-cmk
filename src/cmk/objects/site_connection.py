"""SiteConnection-Object for Object-API."""

from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class SiteConnection(base.ReadWriteObject):
    domain_type = "site_connection"

    class Service(base.ReadWriteService):
        pass

    def login(self, username: str, password: str):
        return self._action("POST", "login", username=username, password=password)

    def logout(self):
        return self._action("POST", "logout")

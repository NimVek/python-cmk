"""User-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class UserConfig(base.ReadWriteObject):
    domain_type = "user_config"

    class Service(base.ReadWriteService):
        def create(self, username, fullname=None, **parameter):
            return super().create(
                username=username,
                fullname=fullname or username,
                **(self.api.version.customer_required(parameter)),
            )

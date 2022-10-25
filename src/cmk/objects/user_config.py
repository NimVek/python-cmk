"""User-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class UserConfig(base.ConfigObject):
    domain_type = "user_config"

    class Service(base.ConfigService):
        def create(self, username, fullname=None, **parameter):
            return super().create(
                username=username,
                fullname=fullname or username,
                **parameter,
            )

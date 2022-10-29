"""UserRole-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class UserRole(base.ReadWriteObject):
    domain_type = "user_role"

    class Service(base.ReadWriteService):
        def create(self, role_id, new_role_id, new_alias=None):
            return super().create(
                role_id=role_id,
                new_role_id=new_role_id,
                new_alias=new_alias or new_role_id,
            )

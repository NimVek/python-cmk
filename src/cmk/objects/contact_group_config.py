"""Contact Group-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class ContactGroupConfig(base.ReadWriteObject):
    domain_type = "contact_group_config"

    class Service(base.ReadWriteService):
        def create(self, name, alias=None, **parameter):
            return super().create(
                name=name,
                alias=alias or name,
                **(self.api.version.customer_required(parameter)),
            )

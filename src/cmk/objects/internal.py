"""Internal-Object for Object-API."""

from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Internal(base.ReadOnlyObject):
    domain_type = "internal"

    class Service(base.ReadOnlyService):
        def discover_receiver(self):
            result = self._action("GET", "discover-receiver")
            return int(result)

"""ServiceDiscoveryRun for Object-API."""
from __future__ import annotations

from . import base, dictionary

import logging


__log__ = logging.getLogger(__name__)


class ServiceDiscoveryRun(base.ReadOnlyObject):
    domain_type = "service_discovery_run"

    class Service(base.ReadOnlyService):
        def start(self, **parameter):
            result = self._action("POST", "start", **parameter)
            __log__.debug(result)
            return result

"""Service-Status for Object-API."""
from __future__ import annotations

from . import base, dictionary

import logging


__log__ = logging.getLogger(__name__)


class ServiceDiscovery(base.ReadOnlyObject):
    domain_type = "service_discovery"

    class Service(base.ReadOnlyService):
        def from_identifier(self, identifier):
            # INCONSISTENCY: id of return object
            # is: service_discovery-{hostname}
            # should be: {hostname}
            if identifier.startswith("service_discovery-"):
                identifier = identifier[18:]
            return super().from_identifier(identifier)

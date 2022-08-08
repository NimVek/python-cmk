"""User-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class ActivationRun(base.Object):
    domain_type = "activation_run"

    class Service(base.Service):
        def start(self, **parameter):
            result = self.api.rest.activate_changes(**parameter)
            __log__.debug(result)
            if not parameter.get("redirect"):
                return self(result[0].get("id"))

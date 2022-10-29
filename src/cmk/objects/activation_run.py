"""User-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class ActivationRun(base.ReadOnlyObject):
    domain_type = "activation_run"

    class Service(base.ReadOnlyService):
        def activate_changes(self, **parameter):
            result = self._action("POST", "activate-changes", **parameter)
            __log__.debug(result)
            return self.from_object(*result) if result[0] else None

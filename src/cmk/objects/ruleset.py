"""Ruleset-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Ruleset(base.ReadOnlyObject):
    domain_type = "ruleset"

    class Service(base.ReadOnlyService):
        pass

    @property
    def rules(self):
        return self.api.Rule.list(ruleset_name=self.identifier)

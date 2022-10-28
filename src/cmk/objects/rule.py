"""Rule-Object for Object-API."""
from __future__ import annotations

import json

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Rule(base.ReadWriteObject):
    domain_type = "rule"

    class Service(base.ReadWriteService):
        def create(
            self,
            ruleset,
            value,
            folder="~",
            properties={"disabled": False},
            conditions={},
        ):
            if not isinstance(value, str):
                value = json.dumps(value)
            return super().create(
                ruleset=ruleset,
                folder=folder,
                properties=properties,
                value_raw=value,
                conditions=conditions,
            )

        def list(self, ruleset_name):
            return super().list(ruleset_name=ruleset_name)

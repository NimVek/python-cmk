"""Rule-Object for Object-API."""

from __future__ import annotations

import ast

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
            properties=None,
            conditions=None,
        ):
            if properties is None:
                properties = {"disabled": False}
            if conditions is None:
                conditions = {}
            value_raw = repr(base.serialize(value))
            return super().create(
                ruleset=ruleset,
                folder=folder,
                properties=properties,
                value_raw=value_raw,
                conditions=conditions,
            )

    @property
    def ruleset(self):
        return self.api.Ruleset(self.extension("ruleset"))

    @property
    def value(self):
        return ast.literal_eval(self.extension("value_raw"))

    @property
    def folder(self):
        return self.api.FolderConfig(self.extension("folder"))

    @property
    def conditions(self):
        return {k: v for k, v in self.extension("conditions").items() if v}

    def move(self, position, **parameter):
        result = self._action(
            "POST", "move", etag=self._etag, position=position, **parameter
        )
        __log__.debug(result)
        return result

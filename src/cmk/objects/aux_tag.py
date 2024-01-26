"""Aux Tag-Object for Object-API."""

from __future__ import annotations

from . import base, interface

import logging


__log__ = logging.getLogger(__name__)


class AuxTag(base.ReadWriteObject, interface.Title):
    domain_type = "aux_tag"

    class Service(base.ReadWriteService):
        def create(self, aux_tag_id, title=None, **parameter):
            return super().create(
                aux_tag_id=aux_tag_id, title=title or aux_tag_id, **parameter
            )

    def invalidate(self):
        for cls in AuxTag.__bases__:
            cls.invalidate(self)

    def _changed(self):
        result = {}
        for cls in AuxTag.__bases__:
            result.update(cls._changed(self))
        return result

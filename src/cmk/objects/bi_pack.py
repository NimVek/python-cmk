"""BI Pack-Object for Object-API."""

from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class BiPack(base.ReadWriteObject):
    domain_type = "bi_pack"

    class Service(base.ReadWriteService):
        pass

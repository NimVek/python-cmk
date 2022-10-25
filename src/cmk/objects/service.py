"""Service-Status for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Service(base.Object):
    domain_type = "service"

    class Service(base.Service):
        pass

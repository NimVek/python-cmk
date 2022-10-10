"""Ruleset-Object for Object-API."""
from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Ruleset(base.Object):
    domain_type = "ruleset"

    class Service(base.Service):
        create = None

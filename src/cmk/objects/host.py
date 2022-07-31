"""Hst-Object for Object-API."""
from __future__ import annotations

from . import attributes, base

import logging


__log__ = logging.getLogger(__name__)


class Host(attributes.EffectiveAttributes):
    domain_type = "host_config"

    Service = base.Service

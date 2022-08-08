"""Hst-Object for Object-API."""
from __future__ import annotations

from . import attributes, base

import logging


__log__ = logging.getLogger(__name__)


class HostConfig(attributes.EffectiveAttributes):
    domain_type = "host_config"

    class Service(base.Service):
        def create(self, host_name, folder=None, **parameter):
            return super().create(
                host_name=host_name,
                folder=folder,
                **parameter,
            )

    def rename(self, new_name):
        pass
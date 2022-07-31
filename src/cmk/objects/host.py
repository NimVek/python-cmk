"""Hst-Object for Object-API."""
from __future__ import annotations

from . import attributes, base

import logging


__log__ = logging.getLogger(__name__)


class Host(attributes.EffectiveAttributes):
    domain_type = "host_config"

    class Service(base.Service):
        def __init__(self, api, cls, folder):
            self.folder = folder
            super().__init__(api, cls)

        def create(self, host_name, folder=None, **parameter):
            return super().create(
                host_name=host_name,
                folder=folder or self.folder,
                **parameter,
            )

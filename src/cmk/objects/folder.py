"""Folder Object for Object-API."""
from __future__ import annotations

from . import attributes, base
from .host import Host

import logging


__log__ = logging.getLogger(__name__)


class Folder(attributes.Attributes):
    domain_type = "folder_config"

    class Service(base.Service):
        def __init__(self, api, cls, parent):
            self.parent = parent
            super().__init__(api, cls)

        def create(self, name, title=None, parent=None, **parameter):
            return super().create(
                name=name,
                title=title or name,
                parent=parent or self.parent,
                **parameter,
            )

    def __init__(self, api, identifier):
        super().__init__(api, identifier)
        self.Folder = Folder.Service(api, Folder, self)
        self.Host = Host.Service(api, Host, self)

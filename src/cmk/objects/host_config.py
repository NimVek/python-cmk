"""Hst-Object for Object-API."""
from __future__ import annotations

from . import attributes, base

import logging


__log__ = logging.getLogger(__name__)


class HostConfig(attributes.EffectiveAttributes):
    domain_type = "host_config"

    class Service(base.ReadWriteService):
        def create(self, host_name, folder=None, **parameter):
            return super().create(
                host_name=host_name,
                folder=folder,
                **parameter,
            )

    def rename(self, new_name):
        result = self._action("PUT", "rename", etag=self._etag, new_name=new_name)
        __log__.debug(result)
        return result

    def move(self, target_folder):
        result = self._action(
            "POST", "move", etag=self._etag, target_folder=target_folder
        )
        __log__.debug(result)
        return result

    @property
    def folder(self):
        return self.api.FolderConfig(self.extension("folder"))

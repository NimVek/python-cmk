"""Folder Object for Object-API."""
from __future__ import annotations

from . import attributes, base
from .host_config import HostConfig

import logging


__log__ = logging.getLogger(__name__)


class FolderConfig(attributes.Attributes):
    domain_type = "folder_config"

    class Service(base.ReadWriteService):
        def create(self, name, title=None, parent="~", **parameter):
            return super().create(
                name=name,
                title=title or name,
                parent=parent,
                **parameter,
            )

        def __call__(self, identifier):
            identifier = identifier.replace("/", "~").replace("\\", "~")
            if not identifier.startswith("~"):
                identifier = "~" + identifier
            return super().__call__(identifier)

    class ParentService:
        def __init__(self, api, cls, parent):
            self.service = getattr(api, cls.__name__)
            self.parent = parent

        def __call__(self, identifier):
            return self.service(identifier)

        def __getattr__(self, name):
            return getattr(self.service, name)

    class FolderParentService(ParentService):
        def create(self, name, title=None, parent=None, **parameter):
            return self.service.create(
                name=name,
                title=title or name,
                parent=parent or self.parent,
                **parameter,
            )

        def __call__(self, identifier):
            if identifier.startswith("~"):
                path = identifier
            else:
                path = self.parent.identifier
                if not path.endswith("~"):
                    path += "~"
                path += identifier
            return self.service(path)

    class HostParentService(ParentService):
        def create(self, host_name, folder=None, **parameter):
            return self.service.create(
                host_name=host_name,
                folder=folder or self.parent,
                **parameter,
            )

    def __init__(self, api, identifier):
        super().__init__(api, identifier)
        self.FolderConfig = FolderConfig.FolderParentService(api, FolderConfig, self)
        self.HostConfig = FolderConfig.HostParentService(api, HostConfig, self)

    @property
    def title(self):
        return self.__title or self._value["title"]

    @title.setter
    def title(self, value):
        self.__title = value or self.identifier

    def invalidate(self):
        super().invalidate()
        self.__title = None

    def _changed(self):
        changed = super()._changed()
        if self.__title != self._value["title"]:
            changed["title"] = self.__title
        return changed

    @property
    def folders(self):
        return self.api.FolderConfig.list(
            parent=self, recursive=False, show_hosts=False
        )

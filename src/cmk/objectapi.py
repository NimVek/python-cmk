"""Object-API for python-cmk."""
from __future__ import annotations

from . import objects
from .httpapi import HTTPAPI
from .restapi import RESTAPI

import logging


__log__ = logging.getLogger(__name__)


def all_subclasses(cls):
    for i in cls.__subclasses__():
        yield i
        yield from all_subclasses(i)


class ObjectAPI:
    def __init__(self, url, user, password):
        self._restapi = RESTAPI(url, user, password)
        self._httpapi = HTTPAPI(url, user, password)

        self.domain_types = {}
        self.root = objects.Folder(self, "~")
        self.add_domain_type(objects.Host)
        self.add_domain_type(objects.Folder, parent=self.root)

    @property
    def rest(self):
        return self._restapi

    @property
    def http(self):
        return self._httpapi

    def add_domain_type(self, cls, **parameter):
        self.domain_types[cls.__name__] = cls.Service(self, cls, **parameter)

    def __getattr__(self, name):
        try:
            return self.domain_types[name]
        except KeyError:
            raise AttributeError

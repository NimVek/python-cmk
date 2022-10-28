"""Object-API for python-cmk."""
from __future__ import annotations

from . import common, objects
from .httpapi import HTTPAPI
from .restapi import RESTAPI

import logging


__log__ = logging.getLogger(__name__)


def all_subclasses(cls):
    for i in cls.__subclasses__():
        yield i
        yield from all_subclasses(i)


class ObjectAPI:
    def __init__(self, url, user=None, password=None):
        self._restapi = RESTAPI(url, user, password)
        self._httpapi = HTTPAPI(url, user, password)

        self.domain_types = {}
        self.add_domain_type(objects.FolderConfig)
        self.add_domain_type(objects.HostConfig)
        self.add_domain_type(objects.UserConfig)
        self.add_domain_type(objects.ActivationRun)
        self.add_domain_type(objects.Ruleset)
        self.add_domain_type(objects.Rule)
        self.add_domain_type(objects.ContactGroupConfig)

        self.add_domain_type(objects.Service)
        self.add_domain_type(objects.Host)
        self.add_domain_type(objects.ServiceDiscovery)
        self.root = objects.FolderConfig(self, "~")

    @property
    def rest(self):
        return self._restapi

    @property
    def http(self):
        return self._httpapi

    def get_service(self, domain_type):
        return self.domain_types[domain_type]

    def add_domain_type(self, cls, **parameter):
        self.domain_types[cls.domain_type] = cls.Service(self, cls, **parameter)
        setattr(self, cls.__name__, self.domain_types[cls.domain_type])

    def from_value(self, value, etag=None):
        service = self.get_service(value["domainType"])
        return service.from_value(value, etag)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        if typ is None:
            try:
                self.ActivationRun.activate_changes()  # type: ignore[attr-defined]
            except common.MKRESTError as e:
                if e.status != 422:
                    raise e

"""Object-API for python-cmk."""
from __future__ import annotations

import enum

from functools import cached_property

from . import common, objects
from .httpapi import HTTPAPI
from .restapi import RESTAPI

import logging


__log__ = logging.getLogger(__name__)


def all_subclasses(cls):
    for i in cls.__subclasses__():
        yield i
        yield from all_subclasses(i)


class Edition(enum.Enum):
    FREE = "cfe"
    RAW = "cre"
    ENTERPRISE = "cee"
    MANAGED = "cme"
    PLUS = "cpe"
    CFE = FREE
    CRE = RAW
    CEE = ENTERPRISE
    CME = MANAGED
    CPE = PLUS


class Version:
    def __init__(self, api):
        self._version, _ = api.rest._request("GET", "version")

    @cached_property
    def edition(self):
        return Edition(self._version["edition"])

    def customer_required(self, parameter):
        if self.edition == Edition.MANAGED:
            if "customer" not in parameter:
                parameter["customer"] = "global"
        else:
            parameter.pop("customer")
        return parameter


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

    @cached_property
    def version(self):
        return Version(self)

    def get_service(self, domain_type):
        return self.domain_types[domain_type]

    def add_domain_type(self, cls, **parameter):
        self.domain_types[cls.domain_type] = cls.Service(self, cls, **parameter)
        setattr(self, cls.__name__, self.domain_types[cls.domain_type])

    def from_object(self, obj, etag=None):
        service = self.get_service(obj["domainType"])
        return service.from_object(obj, etag)

    def from_collection(self, collection, etag=None):
        service = self.get_service(collection["domainType"])
        return (service.from_object(obj) for obj in collection["value"])

    def from_envelope(self, envelope, etag=None):
        if "value" in envelope:
            return self.from_collection(envelope, etag)
        else:
            return self.from_object(envelope, etag)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        if typ is None:
            try:
                self.ActivationRun.activate_changes()  # type: ignore[attr-defined]
            except common.MKRESTError as e:
                if e.status != 422:
                    raise e

"""Object-API for python-cmk."""
from __future__ import annotations

import enum

from functools import cached_property, partialmethod

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
        self._version = api._request("GET", "version")

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

        self.domain_types = {"dict": None, "link": objects.LinkService(self)}

        for obj in all_subclasses(objects.ReadOnlyObject):
            if hasattr(obj, "Service"):
                self.add_domain_type(obj)

        self.domain_types["contact_group"] = self.domain_types["contact_group_config"]

    @property
    def rest(self):
        return self._restapi

    @property
    def http(self):
        return self._httpapi

    def __wrapper(self, _method, *args, **kwargs):
        data, etag = getattr(self.rest, _method)(*args, **kwargs)
        if isinstance(data, dict) and "domainType" in data:
            if "value" in data:
                return self.from_collection(data, etag)
            else:
                return self.from_object(data, etag)
        else:
            return data

    _request = partialmethod(__wrapper, "_request")

    _type_action = partialmethod(__wrapper, "_type_action")
    _type_collection = partialmethod(__wrapper, "_type_collection")

    _object = partialmethod(__wrapper, "_object")
    _object_action = partialmethod(__wrapper, "_object_action")
    _object_collection = partialmethod(__wrapper, "_object_collection")

    @cached_property
    def version(self):
        return Version(self)

    @cached_property
    def root(self):
        return self.FolderConfig("~")  # type: ignore[attr-defined]

    def get_service(self, domain_type):
        return self.domain_types[domain_type]

    def add_domain_type(self, cls, **parameter):
        service = cls.Service(self, cls, **parameter)
        self.domain_types[cls.domain_type] = service
        setattr(self, cls.__name__, service)

    def from_object(self, obj, etag=None):
        service = self.get_service(obj["domainType"])
        return service.from_object(obj, etag)

    def from_collection(self, collection, etag=None):
        collection_service = self.get_service(collection["domainType"])
        for obj in collection["value"]:
            object_service = self.get_service(obj["domainType"])
            yield (object_service or collection_service).from_object(obj)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        if typ is None:
            try:
                self.ActivationRun.activate_changes()  # type: ignore[attr-defined]
            except common.MKRESTError as e:
                if e.status != 422:
                    raise e

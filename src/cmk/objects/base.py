"""Object-API for python-cmk."""
from __future__ import annotations

import abc
import collections.abc
import copy
import enum
import json

from .. import common

import logging


__log__ = logging.getLogger(__name__)


class DomainType:
    def __init__(self, api, domain_type):
        self._api = api
        self._domain_type = domain_type

    @property
    def api(self):
        return self._api

    @property
    def domain_type(self):
        return self._domain_type


class ReadOnlyService(DomainType):
    def __init__(self, api, cls):
        super().__init__(api, cls.domain_type)
        self._cls = cls
        self._cache = {}

    def from_identifier(self, identifier):
        if identifier not in self._cache:
            self._cache[identifier] = self._cls(self.api, identifier)
        return self._cache[identifier]

    def from_object(self, value, etag=None):
        obj = self.from_identifier(value["id"])
        obj._update_internal(value, etag)
        return obj

    def __call__(self, identifier):
        return self.from_identifier(identifier)

    def _action(self, method, action, **parameter):
        return self.api._type_action(
            method, self.domain_type, action, **(serialize(parameter))
        )

    def _collection(self, method, collection_name="all", **parameter):
        return self.api._type_collection(
            method, self.domain_type, collection_name, **(serialize(parameter))
        )

    def list(self, collection_name="all", **parameter):  # noqa: A003
        return self._collection("GET", collection_name, **(serialize(parameter)))


class ReadOnlyObject(abc.ABC):
    def __init__(self, api, identifier):
        self._api = api
        self._identifier = identifier
        self.invalidate()

    @property
    @abc.abstractmethod
    def domain_type(self):
        raise NotImplementedError

    def invalidate(self):
        self.__etag = None
        self.__value = {}

    @property
    def _value(self):
        if not self.__value:
            self.pull()
        return self.__value

    @property
    def _etag(self):
        if not self.__etag:
            self.pull()
        return self.__etag

    @property
    def api(self):
        return self._api

    @property
    def identifier(self):
        return self._identifier

    def _(self, method, **parameter):
        return self.api._object(
            method, self.domain_type, self.identifier, **(serialize(parameter))
        )

    def _action(self, method, action, **parameter):
        return self.api._object_action(
            method, self.domain_type, self.identifier, action, **(serialize(parameter))
        )

    def _collection(self, method, collection_name="all", **parameter):
        return self.api._object_collection(
            method,
            self.domain_type,
            self.identifier,
            collection_name,
            **(serialize(parameter)),
        )

    def pull(self, **parameter):
        return self._("GET", **parameter)

    @property
    def extensions(self):
        return self._value["extensions"]

    def extension(self, name, default=None):
        return self._value["extensions"].get(name, default)

    def __getattr__(self, key):
        if key not in self._value["extensions"]:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'"
            )
        return self._value["extensions"][key]

    def __bool__(self):
        try:
            self.extensions
        except common.MKRESTError as e:
            if e.status != 404:
                raise e
            else:
                return False
        return True

    def __eq__(self, other):
        if isinstance(other, ReadOnlyObject):
            return self.identifier == other.identifier
        elif isinstance(other, str):
            return self.identifier == other
        return NotImplemented

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.identifier)})"

    def list(self, collection_name="all", **parameter):  # noqa: A003
        return self._collection("GET", collection_name, **parameter)

    def _update_internal(self, value, etag):
        self.__value = value
        self.__etag = etag


class ReadWriteService(ReadOnlyService):
    def create(self, **parameter):
        return self._collection("POST", **(serialize(parameter)))


class ReadWriteObject(ReadOnlyObject):
    def invalidate(self):
        super().invalidate()
        self._extensions = {}

    def delete(self):
        self._("DELETE", etag=self._etag)
        self.invalidate()

    def update(self, **parameter):
        self._("PUT", etag=self._etag, **parameter)
        self.invalidate()
        return self

    def _changed(self):
        changed = {}
        for key, value in self._extensions.items():
            old_value = self._serialize_extension(key, super().extension(key))
            new_value = self._serialize_extension(key, value)
            if new_value != old_value:
                changed[key] = new_value
        return changed

    def push(self):
        changed = self._changed()
        if changed:
            self.update(**changed)

    @property
    def extensions(self):
        extensions = super().extensions.copy()
        extensions.update(self._extensions)
        return extensions

    def extension(self, name, default=None):
        return self._extensions.get(name, super().extension(name, default))

    def set_extension(self, name, value):
        self._extensions[name] = value

    def _serialize_extension(self, name, value):
        return serialize(value)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        if typ is None:
            self.push()


class QueryService(ReadOnlyService):
    def query(self, sites=[], query={}, columns=[]):
        return self.list(sites=sites, query=json.dumps(query), columns=columns)


class LinkService(DomainType):
    def __init__(self, api):
        super().__init__(api, "link")

    def from_object(self, obj):
        assert obj["method"] == "GET"
        objects, service, identifier = obj["href"].split("/")[-3:]
        assert objects == "objects"
        service = self.api.get_service(service)
        return service.from_identifier(identifier)


def serialize(item):
    if isinstance(item, ReadOnlyObject):
        return item.identifier
    elif isinstance(item, enum.Enum):
        return item.value
    elif isinstance(item, str):
        return item
    elif isinstance(item, collections.abc.Mapping):
        return {k: serialize(v) for k, v in item.items()}
    elif isinstance(item, collections.abc.MutableSequence):
        return [serialize(v) for v in item]
    elif isinstance(item, collections.abc.Iterable):
        return tuple(serialize(v) for v in item)
    else:
        return item

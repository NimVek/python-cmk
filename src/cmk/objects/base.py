"""Object-API for python-cmk."""
from __future__ import annotations

import abc
import collections.abc
import copy

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

    def from_id(self, identifier):
        return self._cls(self.api, identifier)

    def from_value(self, value, etag=None):
        return self._cls.from_value(self.api, value, etag)

    def __call__(self, identifier):
        return self.from_id(identifier)

    def _action(self, method, action, **parameter):
        return self.api.rest._type_action(
            method, self.domain_type, action, **(serialize(parameter))
        )

    def _collection(self, method, collection_name="all", **parameter):
        return self.api.rest._type_collection(
            method, self.domain_type, collection_name, **(serialize(parameter))
        )

    def list(self, collection_name="all", **parameter):  # noqa: A003
        result, _ = self._collection("GET", collection_name, **(serialize(parameter)))
        service = self.api.get_service(result["domainType"])
        return [service.from_value(item) for item in result["value"]]


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
        self._etag = None
        self._value = {}

    @property
    def api(self):
        return self._api

    @property
    def identifier(self):
        return self._identifier

    def _(self, method, **parameter):
        return self.api.rest._object(
            method, self.domain_type, self.identifier, **(serialize(parameter))
        )

    def _action(self, method, action, **parameter):
        return self.api.rest._object_action(
            method, self.domain_type, self.identifier, action, **(serialize(parameter))
        )

    def _collection(self, method, collection_name="all", **parameter):
        return self.api.rest._object_collection(
            method,
            self.domain_type,
            self.identifier,
            collection_name,
            **(serialize(parameter)),
        )

    def show(self, **parameter):
        return self._("GET", **parameter)

    def pull(self):
        self._value, self._etag = self.show()

    @property
    def extensions(self):
        if not self._value:
            self.pull()
        return self._value["extensions"]

    def extension(self, name, default=None):
        return self.extensions.get(name, default)

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

    def list(self, collection_name="all", **parameter):  # noqa: A003
        result, _ = self._collection("GET", collection_name, **parameter)
        service = self.api.get_service(result["domainType"])
        return [service.from_value(item) for item in result["value"]]

    @classmethod
    def from_value(cls, api, value, etag=None):
        result = cls(api, value["id"])
        result._value = value
        result._etag = etag
        return result


class ReadWriteService(ReadOnlyService):
    def create(self, **parameter):
        result, _ = self._collection("POST", **(serialize(parameter)))
        return self(result["id"])


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

    def pull(self):
        super().pull()
        self._extensions = copy.deepcopy(self._value["extensions"])

    def push(self):
        extensions = {}
        for key, value in self.extensions.items():
            old_value = self._serialize_extension(key, self._extensions.get(key))
            new_value = self._serialize_extension(key, value)
            if new_value != old_value:
                extensions[key] = new_value
        if extensions:
            self.update(**extensions)

    def set_extension(self, name, value):
        self.extensions[name] = value

    def _serialize_extension(self, name, value):
        return serialize(value)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        if typ is None:
            self.push()

    @classmethod
    def from_value(cls, api, value, etag=None):
        return cls(api, value["id"])


def serialize(item):
    if isinstance(item, ReadOnlyObject):
        return item.identifier
    elif isinstance(item, collections.abc.Mapping):
        return {k: serialize(v) for k, v in item.items()}
    elif isinstance(item, str):
        return item
    elif isinstance(item, collections.abc.Iterable):
        return [serialize(v) for v in item]
    else:
        return item

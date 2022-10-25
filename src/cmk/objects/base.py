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


class Service(DomainType):
    def __init__(self, api, cls):
        super().__init__(api, cls.domain_type)
        self._cls = cls

    def __call__(self, identifier):
        return self._cls(self.api, identifier)

    def list(self, collection_name="all", **parameter):  # noqa: A003
        result, _ = self.api.rest.list_objects(
            self._domain_type, collection_name, **(serialize(parameter))
        )
        return [self._cls.from_value(self.api, item) for item in result["value"]]


class Object(abc.ABC):
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

    def show(self, **parameter):
        return self.api.rest.show_object(
            self.domain_type, self._identifier, **parameter
        )

    def action(self, action, **parameter):
        return self.api.rest.object_action(
            self.domain_type, self._identifier, action, **parameter
        )

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
        if isinstance(other, Object):
            return self.identifier == other.identifier
        elif isinstance(other, str):
            return self.identifier == other
        return NotImplemented

    @classmethod
    def from_value(cls, api, value):
        result = cls(api, value["id"])
        result._value = value
        return result


class ConfigService(Service):
    def create(self, **parameter):
        result, _ = self.api.rest.create_object(
            self._domain_type, **(serialize(parameter))
        )
        return self(result["id"])

    def list(self, collection_name="all", **parameter):  # noqa: A003
        result, _ = self.api.rest.list_objects(
            self._domain_type, collection_name, **(serialize(parameter))
        )
        return [self._cls(self.api, item["id"]) for item in result["value"]]


class ConfigObject(Object):
    def invalidate(self):
        super().invalidate()
        self._extensions = {}

    def delete(self):
        self.api.rest.delete_object(self.domain_type, self._identifier, etag=self._etag)
        self.invalidate()

    def update(self, **parameter):
        self.api.rest.update_object(
            self.domain_type, self._identifier, etag=self._etag, **parameter
        )
        self.invalidate()
        return self

    def pull(self):
        super().pull()
        self._extensions = copy.deepcopy(self._value["extensions"])

    def push(self):
        extensions = {}
        for key, value in self._extensions.items():
            old_value = self._serialize_extension(
                key, self._value["extensions"].get(key)
            )
            new_value = self._serialize_extension(key, value)
            if new_value != old_value:
                extensions[key] = new_value
        if extensions:
            self.update(**extensions)

    @property
    def extensions(self):
        if not self._value:
            self.pull()
        return self._extensions

    def set_extension(self, name, value):
        self._extensions[name] = value

    def _serialize_extension(self, name, value):
        return serialize(value)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        if typ is None:
            self.push()


def serialize(item):
    if isinstance(item, Object):
        return item.identifier
    elif isinstance(item, collections.abc.Mapping):
        return {k: serialize(v) for k, v in item.items()}
    elif isinstance(item, str):
        return item
    elif isinstance(item, collections.abc.Iterable):
        return [serialize(v) for v in item]
    else:
        return item

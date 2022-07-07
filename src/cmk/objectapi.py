"""Object-API for python-cmk."""
from __future__ import annotations

import abc

from .httpapi import HTTPAPI
from .restapi import RESTAPI

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
        return self._cls(self, identifier)

    def create(self, **parameter):
        result, _ = self.api.create_object(self._domain_type, **parameter)
        return self(result["id"])


class Object(abc.ABC):
    def __init__(self, service, identifier):
        self._service = service
        self._identifier = identifier
        self.invalidate()

    @property
    @abc.abstractmethod
    def domain_type(self):
        raise NotImplementedError

    def invalidate(self):
        self._etag = None
        self._value = None
        self.__extensions = {}

    @property
    def api(self):
        return self._service.api

    def delete(self):
        self.api.delete_object(self.domain_type, self._identifier, etag=self._etag)
        self.invalidate()

    def update(self, **parameter):
        self.api.update_object(
            self.domain_type, self._identifier, etag=self._etag, **parameter
        )
        self.invalidate()
        return self

    def show(self, **parameter):
        return self.api.show_object(self.domain_type, self._identifier, **parameter)

    def action(self, action, **parameter):
        return self.api.object_action(
            self.domain_type, self._identifier, action, **parameter
        )

    def pull(self):
        self._value, self._etag = self.show()

    def push(self):
        self.update(
            **{
                key: value
                for key, value in self.__extensions.items()
                if self.extensions.get(key) != value
            }
        )

    @property
    def extensions(self):
        if not self._value:
            self.pull()
        return self._value["extensions"]  # type: ignore[index]

    def extension(self, name, default=None):
        return self.__extensions.get(name, self.extensions.get(name, default))

    def set_extension(self, name, value):
        self.__extensions[name] = value

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        if typ is None:
            self.push()


class Host(Object):
    domain_type = "host_config"


def all_subclasses(cls):
    for i in cls.__subclasses__():
        yield i
        yield from all_subclasses(i)


class ObjectAPI:
    def __init__(self, url, user, password):
        self._restapi = RESTAPI(url, user, password)
        self._httpapi = HTTPAPI(url, user, password)

        self.domain_types = {
            cls.__name__: Service(self._restapi, cls)
            for cls in all_subclasses(Object)
            if hasattr(cls, "domain_type")
        }

    def __getattr__(self, name):
        try:
            return self.domain_types[name]
        except KeyError:
            raise AttributeError

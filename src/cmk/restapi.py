"""RESTAPI for python-cmk."""
from __future__ import annotations

import json

from functools import partialmethod

from . import common

import logging


__logger__ = logging.getLogger(__name__)


class RESTAPI(common.API):
    def __init__(self, url, user=None, password=None):
        super().__init__(url, user, password)
        self._session.base /= "api/v0"
        self._session.headers["Authorization"] = f"Bearer {self._user} {self._password}"
        __logger__.debug(self._session.headers)

    def _request(self, method, url, etag=None, data=None):
        headers = {}
        _params = _data = None

        if method == "GET":
            _params = data
        else:
            _data = data
        if etag:
            headers["If-Match"] = etag
        with self._session.request(
            method,
            url,
            params=_params,
            json=_data,
            headers=headers,
        ) as response:
            if not response:
                raise common.MKRESTError(response.json())
            if response.headers.get("Content-Type") == "application/json":
                result = response.json()
            elif response.encoding:
                resutl = response.text
            else:
                result = response.content
            etag = json.loads(response.headers.get("ETag", "null"))
            return result, etag

    def _type_action(self, method, domain_type, action, etag=None, **parameter):
        return self._request(
            method,
            f"domain-types/{domain_type}/actions/{action}/invoke",
            etag=etag,
            data=parameter,
        )

    def _type_collection(
        self, method, domain_type, collection_name="all", etag=None, **parameter
    ):
        return self._request(
            method,
            f"domain-types/{domain_type}/collections/{collection_name}",
            etag=etag,
            data=parameter,
        )

    def _object(self, method, domain_type, identifier, etag=None, **parameter):
        return self._request(
            method,
            f"objects/{domain_type}/{identifier}",
            etag=etag,
            data=parameter,
        )

    def _object_action(
        self, method, domain_type, identifier, action, etag=None, **parameter
    ):
        return self._request(
            method,
            f"objects/{domain_type}/{identifier}/actions/{action}/invoke",
            etag=etag,
            data=parameter,
        )

    def _object_collection(
        self, method, domain_type, identifier, collection_name, etag=None, **parameter
    ):
        return self._request(
            method,
            f"objects/{domain_type}/{identifier}/collections/{collection_name}",
            etag=etag,
            data=parameter,
        )

    create_object = partialmethod(_type_collection, "POST", collection_name="all")

    show_object = partialmethod(_object, "GET")

    def delete_object(self, domain_type, identifier, etag=None):
        if etag is None:
            _, etag = self.show_object(domain_type, identifier)
        return self._object("DELETE", domain_type, identifier, etag=etag)

    def update_object(self, domain_type, identifier, etag=None, **parameter):
        if etag is None:
            _, etag = self.show_object(domain_type, identifier)
        return self._object("PUT", domain_type, identifier, etag=etag, **parameter)

    def list_objects(self, domain_type, collection_name="all", **parameter):
        return self._type_collection(
            "GET", domain_type, collection_name=collection_name, **parameter
        )

    activate_changes = partialmethod(
        _type_action, "POST", "activation_run", "activate-changes"
    )

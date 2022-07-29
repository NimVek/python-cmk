"""RESTAPI for python-cmk."""
from __future__ import annotations

import json

from functools import partialmethod

import requests

from . import common

import logging


__log__ = logging.getLogger(__name__)


class RESTAPI:
    def __init__(self, url, user, password):
        self._url = common.cleanup_url(url) + "api/v0"
        self._session = requests.session()
        if common.path_ca_bundle():
            self._session.verify = common.path_ca_bundle()
        self._session.headers["Authorization"] = f"Bearer {user} {password}"
        self._session.headers["Accept"] = "application/json"

    def __request(self, method, url, **kwargs):
        return self._session.request(method, self._url + url, **kwargs)

    def _request(self, method, url, etag=None, data=None):
        headers = {}
        _params = _data = None

        if method == "GET":
            _params = data
        else:
            _data = data
        if etag:
            headers["If-Match"] = etag
        with self.__request(
            method,
            url,
            params=_params,
            json=_data,
            headers=headers,
        ) as response:
            if not response:
                raise common.MKRESTError(response.json())
            result = response.json() if response.status_code != 204 else None
            etag = json.loads(response.headers.get("ETag", "null"))
            return result, etag

    def _type_action(self, method, domain_type, action, **parameter):
        return self._request(
            method,
            f"/domain-types/{domain_type}/actions/{action}/invoke",
            data=parameter,
        )

    def _type_collection(self, method, domain_type, collection_name="all", **parameter):
        return self._request(
            method,
            f"/domain-types/{domain_type}/collections/{collection_name}",
            data=parameter,
        )

    def _object(self, method, domain_type, identifier, **parameter):
        return self._request(
            method,
            f"/objects/{domain_type}/{identifier}",
            data=parameter,
        )

    def _object_action(self, method, domain_type, identifier, action, **parameter):
        return self._request(
            method,
            f"/objects/{domain_type}/{identifier}/actions/{action}/invoke",
            data=parameter,
        )

    def _object_collection(
        self, method, domain_type, identifier, collection_name, **parameter
    ):
        return self._request(
            method,
            f"/objects/{domain_type}/{identifier}/collections/{collection_name}",
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

    def list_objects(self, domain_type, **parameter):
        return self._type_collection(
            "GET", domain_type, collection_name="all", **parameter
        )

"""Common definitions for python-cmk."""
from __future__ import annotations

import pathlib

import furl
import requests

import logging


__logger__ = logging.getLogger(__name__)


class MKError(Exception):
    pass


class MKRESTError(Exception):
    def __init__(self, response):
        self._response = response

    def __getattr__(self, item):
        return self._response[item]


_CA_BUNDLE_CANDIDATES = [
    "/etc/ssl/certs/ca-certificates.crt",  # Debian/Ubuntu/Gentoo etc.
    "/etc/pki/tls/certs/ca-bundle.crt",  # Fedora/RHEL 6
    "/etc/ssl/ca-bundle.pem",  # OpenSUSE
    "/etc/pki/tls/cacert.pem",  # OpenELEC
    "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",  # CentOS/RHEL 7
    "/etc/ssl/cert.pem",  # Alpine Linux
]


class Session(requests.Session):
    def __init__(self, base):
        super().__init__()
        self.base = base
        for candidate in _CA_BUNDLE_CANDIDATES:
            if pathlib.Path(candidate).is_file():
                self.verify = candidate

    @property
    def base(self):
        return self.__base

    @base.setter
    def base(self, base):
        self.__base = furl.furl(base)
        self.__base.path.normalize()
        self.__base.remove(path="/")

    def request(self, method, url, *args, **kwargs):
        return super().request(method, self.base / url, *args, **kwargs)


class API:
    def __init__(self, url, user=None, password=None):
        uri = furl.furl(url)
        self._user = user or uri.username
        self._password = password or uri.password
        uri.remove(username=True, password=True)
        self._session = Session(uri)
        if not self._session.base.path.segments[-1] == "check_mk":
            self._session.base /= "check_mk"

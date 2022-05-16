"""Common definitions for python-cmk."""
from __future__ import annotations

import pathlib

import logging


__logger__ = logging.getLogger(__name__)


class MKError(Exception):
    pass


_CA_BUNDLE_CANDIDATES = [
    "/etc/ssl/certs/ca-certificates.crt",  # Debian/Ubuntu/Gentoo etc.
    "/etc/pki/tls/certs/ca-bundle.crt",  # Fedora/RHEL 6
    "/etc/ssl/ca-bundle.pem",  # OpenSUSE
    "/etc/pki/tls/cacert.pem",  # OpenELEC
    "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",  # CentOS/RHEL 7
    "/etc/ssl/cert.pem",  # Alpine Linux
]


def path_ca_bundle():
    for candidate in _CA_BUNDLE_CANDIDATES:
        if pathlib.Path(candidate).is_file():
            return candidate
    return None


def cleanup_url(url: str) -> str:
    if not url.endswith("/"):
        url += "/"
    if not url.endswith("check_mk/"):
        url += "check_mk/"
    return url

"""Object-API for python-cmk."""
from __future__ import annotations

import collections.abc

from functools import partialmethod

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Dictionary(base.ReadOnlyObject, collections.abc.Mapping):
    def __getitem__(self, key):
        return self.extension(key)

    def __iter__(self):
        return iter(self.extensions)

    def __len__(self):
        return len(self.extensions)

"""Title Interface for Object-API."""

from __future__ import annotations

import logging


__log__ = logging.getLogger(__name__)


class FixEmptyExtensions:
    def __getattr__(self, key):
        if not self.extensions:
            self.invalidate()
        return super().__getattr__(key)

"""Title Interface for Object-API."""

from __future__ import annotations

import logging


__log__ = logging.getLogger(__name__)


class Title:
    @property
    def title(self):
        return self.__title or self._value["title"]

    @title.setter
    def title(self, value):
        self.__title = value or self.identifier

    def invalidate(self):
        self.__title = None

    def _changed(self):
        if self.__title is not None and self._value["title"] != self.__title:
            return {"title": self.__title}
        return {}

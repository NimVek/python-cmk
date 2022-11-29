"""Object-API for python-cmk."""
from __future__ import annotations

from functools import partialmethod

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Attributes(base.ReadWriteObject):
    @property
    def attributes(self):
        return self.extension("attributes", {})

    def attribute(self, name, default=None):
        return self.attributes.get(name, default)

    def set_attribute(self, name, value):
        attributes = self.attributes.copy()
        if value is None:
            attributes.pop(name, None)
        else:
            attributes[name] = value
        self.set_extension("attributes", attributes)

    @property
    def labels(self):
        return self.attribute("labels", {})

    def label(self, name, default=None):
        return self.labels.get(name, default)

    def set_label(self, name, value):
        labels = self.labels.copy()
        if value is None:
            labels.pop(name, None)
        else:
            labels[name] = value
        self.set_attribute("labels", labels)

    def _serialize_extension(self, name, value):
        if name == "attributes":
            value = value.copy()
            value.pop("meta_data", None)

        return super()._serialize_extension(name, value)


class EffectiveAttributes(Attributes):
    pull = partialmethod(Attributes.pull, effective_attributes=True)

    @property
    def effective_attributes(self):
        result = self.extension("effective_attributes", {})
        if result is None:
            self.pull()
            result = self.extension("effective_attributes", {})
        return result

    def effective_attribute(self, name, default=None):
        return self.effective_attributes.get(name, default)

    def set_effective_attribute(self, name, value):
        if self.effective_attribute(name) != value:
            self.effective_attributes[name] = value
            self.set_attribute(name, value)

    def _serialize_extension(self, name, value):
        if name == "effective_attributes":
            value = None

        return super()._serialize_extension(name, value)

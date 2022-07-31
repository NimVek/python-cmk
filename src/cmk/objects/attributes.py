"""Object-API for python-cmk."""
from __future__ import annotations

from functools import partialmethod

from . import base

import logging


__log__ = logging.getLogger(__name__)


class Attributes(base.Object):
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

    def prepare_extension(self, name, value):
        if name == "attributes":
            value = value.copy()
            value.pop("meta_data", None)

        return super().prepare_extension(name, value)


class EffectiveAttributes(Attributes):
    show = partialmethod(Attributes.show, effective_attributes=True)

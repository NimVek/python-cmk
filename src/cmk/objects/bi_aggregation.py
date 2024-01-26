"""BI Aggregation-Object for Object-API."""

from __future__ import annotations

from . import base

import logging


__log__ = logging.getLogger(__name__)


class BiAggregation(base.ReadWriteObject):
    domain_type = "bi_aggregation"

    class Service(base.ReadWriteService):
        def aggregation_state(self, **parameter):
            result = self._action("POST", "aggregation_state", **parameter)
            __log__.debug(result)
            return result

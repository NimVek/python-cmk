"""Host-Status for Object-API."""
from __future__ import annotations

from . import base, dictionary

import logging


__log__ = logging.getLogger(__name__)


class Host(dictionary.Dictionary):
    domain_type = "host"

    class Service(base.QueryService):
        def query(self, sites=[], query={}, columns=["name"]):
            if len(columns) == 1:
                if "name" in columns:
                    columns.append("alias")
                else:
                    columns.append("name")
            return super().query(sites=sites, query=query, columns=columns)

    def services(self, sites=None, query=None, columns=None):
        return self.list(
            collection_name="services", sites=sites, query=query, columns=columns
        )

    def service(self, service_description):
        return self._action(
            "GET", "show_service", service_description=service_description
        )

    @property
    def config(self):
        return self.api.HostConfig(self.identifier)

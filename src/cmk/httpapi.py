"""HTTPAPI for python-cmk."""
from __future__ import annotations

import ast
import json

from typing import TYPE_CHECKING

from . import common

import logging


__log__ = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing import Literal


class HTTPAPI(common.API):
    def __init__(self, url, user=None, password=None):
        super().__init__(url, user, password)
        self._credentials = {
            "_username": self._user,
            "_secret": self._password,
            "request_format": "json",
            "output_format": "json",
        }

    def _request(self, url, params, data=None, ioformat=None):
        params.update(self._credentials)
        if ioformat:
            params["request_format"] = ioformat.get("input", "json")
            params["output_format"] = ioformat.get("output", "json")
        if data:
            if params["request_format"] == "python":
                data = repr(data)
            else:
                data = json.dumps(data)
            response = self._session.post(
                url,
                params=params,
                data={"request": data},
                allow_redirects=False,
            )
        else:
            response = self._session.get(url, params=params, allow_redirects=False)
        if response:
            if response.text.startswith("ERROR: "):
                raise ValueError(response.text[7:])
            else:
                if params["output_format"] == "python":
                    return ast.literal_eval(response.text)
                else:
                    return response.json()
        response.raise_for_status()

    def view(
        self, view_name: str, limit: Literal["soft", "hard", "none"] = "none", **filters
    ):
        """Fetches data from a View.

        Retrieves rows of the view specified by name.

        Args:
           view_name: Name of the View
           limit: Limit the amount of results
           **filters: Filter parameters
        """
        parameter = {"view_name": view_name, "limit": limit}
        parameter.update(filters)
        result = self._request("view.py", parameter)
        header = result[0]
        return [dict(zip(header, row)) for row in result[1:]]

    def webapi(self, action, data=None, ioformat=None):
        result = self._request("webapi.py", {"action": action}, data, ioformat)
        if result["result_code"]:
            error = result["result"]
            if error.startswith("Checkmk exception: "):
                raise common.MKError(error[19:])
            elif error.startswith("Unhandled exception: "):
                raise Exception(error[21:])
            raise Exception(result["result"])
        return result["result"]

    def get_rulesets_info(self):
        return self.webapi("get_rulesets_info")

    def get_ruleset(self, name):
        return self.webapi(
            "get_ruleset", data={"ruleset_name": name}, ioformat={"output": "python"}
        )

    def set_ruleset(self, name, ruleset, configuration_hash=None):
        data = {"ruleset_name": name, "ruleset": ruleset}
        if configuration_hash:
            data["configuration_hash"] = configuration_hash
        self.webapi("set_ruleset", data=data, ioformat={"input": "python"})

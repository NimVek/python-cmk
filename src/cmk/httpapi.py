"""HTTPAPI for python-cmk."""
from __future__ import annotations

import ast
import json

import requests

from . import common

import logging


__log__ = logging.getLogger(__name__)


class HTTPAPI:
    def __init__(self, url, user, secret):
        self._session = requests.session()
        if common.path_ca_bundle():
            self._session.verify = common.path_ca_bundle()
        self._url = common.cleanup_url(url)
        self._credentials = {
            "_username": user,
            "_secret": secret,
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
                self._url + url,
                params=params,
                data={"request": data},
                allow_redirects=False,
            )
        else:
            response = self._session.get(
                self._url + url, params=params, allow_redirects=False
            )
        if response:
            if response.text.startswith("ERROR: "):
                raise ValueError(response.text[7:])
            else:
                if params["output_format"] == "python":
                    return ast.literal_eval(response.text)
                else:
                    return response.json()
        response.raise_for_status()

    def view(self, view_name, limit="none", **parameter):
        """limit: soft|hard|none"""
        parameter.update({"view_name": view_name, "limit": limit})
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

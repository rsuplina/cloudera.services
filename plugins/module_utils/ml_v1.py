# -*- coding: utf-8 -*-

# Copyright 2026 Cloudera, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A common Ansible Module for shared functions for the CML Workspace API V1 (legacy).
"""

import http.client
import io
import json
import logging
import requests

from re import sub
from functools import wraps
from typing import List, NamedTuple, Optional

from ansible.module_utils.basic import AnsibleModule, env_fallback

__maintainer__ = [
    "wmudge@cloudera.com",
]

API_VERSION = "api/v1"
LOG = []


def kebab(s):
    return "-".join(
        sub(
            r"(\s|_|-)+",
            " ",
            sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda mo: " " + mo.group(0).lower(),
                s,
            ),
        ).split(),
    )


class LogCaptureHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        global LOG
        LOG.append(msg)


def httpclient_log_func(*args):
    LOG.append(args)


class Squelch(NamedTuple):
    status_code: int
    return_value: any


class MLModuleV1(object):
    """A base ML Workspace module class for common parameters, fields, and methods."""

    def __init__(self, module):
        # Set common parameters
        self.module = module
        self.endpoint = self._get_param("endpoint").strip("/")
        self.api_key = self._get_param("api_key")
        self.debug = self._get_param("debug", default=False)
        self.agent_header = self._get_param("agent_header", default="ClouderaFoundry")

        # Logging
        _log_format = (
            "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
        )
        if self.debug:
            # self._setup_logger(logging.DEBUG, _log_format)
            handler = LogCaptureHandler()
            root = logging.getLogger()
            root.addHandler(handler)
            root.setLevel(logging.DEBUG)
            http.client.HTTPConnection.debuglevel = 1
            http.client.print = httpclient_log_func
        else:
            self._setup_logger(logging.ERROR, _log_format)

        # Initialize common return values
        self.log_out = None
        self.log_lines = []
        self.changed = False

        # Requests
        self.requests = requests
        self._api_path = [self.endpoint, API_VERSION]

    def _get_param(self, *params, default=None):
        """Fetches an Ansible input parameter, including nested options, if it exists, else returns optional default or None"""
        p = dict(self.module.params)
        for key in params:
            try:
                p = p[key]
                if p is None:
                    return default
            except KeyError:
                return default
        return p

    def _setup_logger(self, log_level, log_format):
        http.client.HTTPConnection.debuglevel = 1

        # logging.basicConfig()
        self.logger = logging.getLogger("MLSDK")
        self.logger.setLevel(log_level)

        requests_log = logging.getLogger("urllib3")
        requests_log.setLevel(log_level)
        requests_log.propagate = True

        self.__log_capture = io.StringIO()
        handler = logging.StreamHandler(self.__log_capture)
        handler.setLevel(log_level)

        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        requests_log.addHandler(handler)

    def _get_log(self):
        # contents = self.__log_capture.getvalue()
        # self.__log_capture.truncate(0)
        # return contents
        global LOG
        return LOG

    @classmethod
    def process_debug(cls, f):
        @wraps(f)
        def _impl(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            if self.debug:
                self.log_out = self._get_log()
                # self.module.fail_json(msg=self.log_out)
                self.log_lines.append(self.log_out)
            return result

        return _impl

    def _process_request(self, req, success_code, squelch):
        if req.status_code != success_code:
            for s in squelch:
                if req.status_code == s.status_code:
                    return s.return_value
            self.module.fail_json(msg=req.text, status_code=req.status_code)
        else:
            return req.json()

    def _process_pagination(self, endpoint_call, endpoint_args, return_field):
        results = []

        resp = endpoint_call(endpoint_args)
        if resp is None:
            return None

        while "next_page_token" in resp and resp["next_page_token"]:
            results.extend(resp[return_field])
            endpoint_args["page_token"] = resp["next_page_token"]
            resp = endpoint_call(endpoint_args)

        results.extend(resp[return_field])
        return results

    def query(
        self,
        method: str,
        api: List[str],
        field: Optional[str] = None,
        success_code=200,
        squelch: List[Squelch] = [],
        params={},
        body={},
    ):
        """Execute a Workspace API V1 query"""

        def _api_call(query_args={}):
            req = self.requests.request(
                method.upper(),
                "/".join(self._api_path + api),
                headers={
                    "Content-Type": "application/json",
                },
                auth=[self.api_key, ""],
                params=query_args,
                data=json.dumps(body, separators=(",", ":")),
            )
            return self._process_request(req, success_code, squelch)

        if field is None:
            return _api_call(params)
        else:
            return self._process_pagination(_api_call, params, field)

    @staticmethod
    def ansible_module(argument_spec={}, **kwargs):
        """Creates the base Ansible module argument spec and dependencies."""
        return AnsibleModule(
            argument_spec=dict(
                **argument_spec,
                endpoint=dict(
                    required=True,
                    type="str",
                    aliases=["url", "workspace_url"],
                    fallback=(env_fallback, ["CML_ENDPOINT"]),
                ),
                api_key=dict(
                    required=True,
                    type="str",
                    no_log=True,
                    aliases=["token"],
                    fallback=(env_fallback, ["CML_API_V1_KEY"]),
                ),
                debug=dict(
                    required=False,
                    type="bool",
                    default=False,
                    aliases=["debug_endpoint"],
                ),
                agent_header=dict(
                    required=False,
                    type="str",
                    default="ClouderaFoundry",
                ),
            ),
            **kwargs,
        )

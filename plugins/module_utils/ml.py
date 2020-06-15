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
A common Ansible Module for shared functions for the CML Workspace API V2.
See https://docs.cloudera.com/machine-learning/cloud/api/topics/ml-api-v2.html
"""

import http.client
import io
import json
import logging
import re
import requests

from typing import NamedTuple, List
from functools import wraps

from ansible.module_utils.basic import AnsibleModule, env_fallback

__maintainer__ = [
    "wmudge@cloudera.com",
]

API_VERSION = "api/v2"
LOG = []


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


class MLModule(AnsibleModule):
    """A base ML Workspace module class for common parameters, fields, and methods."""

    def __init__(self, module):
        # Set common parameters
        self.module = module
        self.endpoint = self._get_param("endpoint").strip("/")
        self.api_key = self._get_param("api_key")
        self.debug = self._get_param("debug", default=False)
        self.agent_header = self._get_param("agent_header", default="ClouderaFoundry")
        self.endpoint_tls = self._get_param("endpoint_tls", default=True)

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
                self.module.fail_msg(msg=self.log_out)
                self.log_lines.append(self.log_out.splitlines())
            return result

        return _impl

    def find_project(self, name: str):
        query_params = dict(
            include_public_projects=True,
            search_filter=json.dumps(dict(name=name), separators=(",", ":")),
        )
        project_list = self.query(
            method="GET",
            api=["projects"],
            field="projects",
            params=query_params,
        )
        if project_list and len(project_list) == 1:
            return project_list[0]
        elif len(project_list) > 1:
            self.module.fail_json(msg="Multiple projects found for name: " + name)
        else:
            return None

    def get_project(self, id: str):
        project = self.query(
            method="GET",
            api=["projects", id],
            squelch=[Squelch(403, None)],
        )
        if project:
            return project
        else:
            return None

    def find_job(self, project_id: str, name: str):
        query_params = dict(
            search_filter=json.dumps(dict(name=name), separators=(",", ":")),
        )
        job_list = self.query(
            method="GET",
            api=["projects", project_id, "jobs"],
            field="jobs",
            params=query_params,
        )
        if job_list and len(job_list) == 1:
            return job_list[0]
        elif len(job_list) > 1:
            self.module.fail_json(msg="Multiple jobs found for name: " + name)
        else:
            return None

    def get_job(self, project_id: str, id: str):
        job = self.query(
            method="GET",
            api=["projects", project_id, "jobs", id],
            squelch=[Squelch(403, None)],
        )
        if job:
            return job
        else:
            return None

    def find_model(self, project_id: str, name: str):
        query_params = dict(
            search_filter=json.dumps(dict(name=name), separators=(",", ":")),
        )
        model_list = self.query(
            method="GET",
            api=["projects", project_id, "models"],
            field="models",
            params=query_params,
        )
        if model_list and len(model_list) == 1:
            return model_list[0]
        elif len(model_list) > 1:
            self.module.fail_json(msg="Multiple models found for name: " + name)
        else:
            return None

    def get_model(self, project_id: str, id: str):
        model = self.query(
            method="GET",
            api=["projects", project_id, "models", id],
            squelch=[Squelch(403, None)],
        )
        if model:
            return model
        else:
            return None

    def find_latest_build(self, project_id: str, model_id: str):
        build_list = self.query(
            method="GET",
            api=["projects", project_id, "models", model_id, "builds"],
            field="model_builds",
            params=dict(
                sort="-created_at",
                search_filter=json.dumps(dict(status="built"), separators=(",", ":")),
            ),
        )
        if build_list:
            return build_list[0]
        else:
            return None

    def get_build(self, project_id: str, model_id: str, id: str):
        build = self.query(
            method="GET",
            api=["projects", project_id, "models", model_id, "builds", id],
            squelch=[Squelch(403, None)],
        )
        if build:
            return build
        else:
            return None

    def find_application(self, project_id: str, name: str):
        query_params = dict(
            search_filter=json.dumps(dict(name=name), separators=(",", ":")),
        )
        app_list = self.query(
            method="GET",
            api=["projects", project_id, "applications"],
            field="applications",
            params=query_params,
        )
        if app_list and len(app_list) == 1:
            return app_list[0]
        elif len(app_list) > 1:
            self.module.fail_json(msg="Multiple applications found for name: " + name)
        else:
            return None

    def get_application(self, project_id: str, id: str):
        app = self.query(
            method="GET",
            api=["projects", project_id, "applications", id],
            squelch=[Squelch(403, None)],
        )
        if app:
            return app
        else:
            return None

    def _process_request(self, req, squelch):
        resp = req.json()
        if req.status_code != 200:
            for s in squelch:
                if req.status_code == s.status_code:
                    return s.return_value
            self.module.fail_json(
                msg=resp["message"],
                error=resp["error"],
                code=resp["code"],
                details=resp["details"],
            )
        return resp

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
        api: List[str] = [],
        field: str = None,
        squelch: List[Squelch] = [],
        params={},
        body={},
    ):
        """Execute a Workspace API query"""

        def _api_call(query_args={}):
            req = self.requests.request(
                method.upper(),
                "/".join(self._api_path + api),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                params=query_args,
                data=json.dumps(body, separators=(",", ":")),
                verify=self.endpoint_tls,
            )
            return self._process_request(req, squelch)

        if field is None:
            return _api_call(params)
        else:
            return self._process_pagination(_api_call, params, field)

    @staticmethod
    def ansible_module(argument_spec={}, **kwargs):
        """Default Ansible module argument spec and dependencies for the CML API"""
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
                    fallback=(env_fallback, ["CML_API_KEY"]),
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
                endpoint_tls=dict(
                    required=False,
                    type="bool",
                    default=True,
                    aliases=["verify_endpoint_tls", "verify_tls", "verify_api_tls"],
                ),
            ),
            **kwargs,
        )


def validate_project_id(id: str):
    pattern = re.compile("^(?:[a-z0-9]{4}-){3}[a-z0-9]{4}$")
    return True if pattern.fullmatch(id) else False


def validate_build_id(id: str):
    pattern = re.compile(
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    )
    return True if pattern.fullmatch(id) else False


def validate_subdomain(subdomain: str):
    pattern = re.compile("^[a-z0-9]+(-[a-z0-9]+)*$")
    return True if pattern.fullmatch(subdomain) else False


def difference(source: any, target: any):
    if isinstance(source, dict) and isinstance(target, dict):
        collector = dict()
        if source.keys() != target.keys():
            s1 = set(source.keys())
            s2 = set(target.keys())
            common_keys = s1 & s2
            addl_keys = s1 - s2
        else:
            common_keys = set(source.keys())
            addl_keys = []
        for k in common_keys:
            result = difference(source[k], target[k])
            if result is not None:
                collector[k] = result
        for a in addl_keys:
            collector[a] = source[a]
        if collector:
            return collector
    elif isinstance(source, list) and isinstance(target, list):
        if len(source) != len(target):
            return source
        for i in range(len(source)):
            result = difference(source[i], target[i])
            if result:
                return source
    else:
        if source != target:
            return source

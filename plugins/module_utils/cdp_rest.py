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
A common Ansible Module for REST access to Cloudera Data Platform (CDP) Data Services.
"""

import io
import logging
import platform

from functools import wraps
from typing import Any, List

from requests import Session, Response, codes, request

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cloudera.services.plugins.module_utils.common import get_param

__credits__ = ["araujo@cloudera.com"]
__maintainer__ = ["araujo@cloudera.com", "wmudge@cloudera.com"]


class CdpRestResponse(object):
    STATUS_CODES = codes

    def __init__(
        self,
        return_code: int,
        return_value: any = None,
        extract_field: str = None,
    ) -> None:
        self.code = return_code
        self.value = return_value
        self.field = extract_field

    @property
    def return_code(self):
        return self.code

    @property
    def return_value(self):
        return self.value

    @property
    def extract_field(self):
        return self.field


class CdpRestModule(object):
    """A base module class for handling CDP REST APIs."""

    def __init__(self, module: AnsibleModule, name: str) -> None:
        self.module = module
        self.module_name = name

        # Set common parameters
        self.endpoint = get_param(self.module, "endpoint").rstrip("/")
        self.username = get_param(self.module, "username")
        self.password = get_param(self.module, "password")
        self.debug = get_param(self.module, "debug")
        self.agent_header = get_param(self.module, "agent_header")
        self.headers = get_param(self.module, "headers", {})

        # Set up debug log
        log_format = (
            "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
        )
        if self.debug:
            self._setup_logger(logging.DEBUG, log_format)
            self.logger.debug(self._user_agent())
        else:
            self._setup_logger(logging.ERROR, log_format)

        # Set up session
        self._session = Session()
        self._session.auth = (self.username, self.password)

        # Apply custom headers to the session
        for header_name, header_value in self.headers.items():
            self._session.headers.update({header_name: header_value})

        # Set up TLS verification
        if get_param(self.module, "verify_tls"):
            if get_param(self.module, "ca_cert_file", None) is None:
                self._session.verify = True
            else:
                self._session.verify = get_param(self.module, "ca_cert_file")
        else:
            self._session.verify = False

        # Initialize common return values
        self.log_out = None
        self.log_lines = []
        self.changed = False

    def _user_agent(self) -> str:
        return "%s Python/%s %s/%s" % (
            self.agent_header,
            platform.python_version(),
            platform.system(),
            platform.release(),
        )

    def _setup_logger(self, log_level, log_format) -> None:
        logging.basicConfig()
        logging.getLogger().setLevel(log_level)

        self.__log_capture = io.StringIO()
        handler = logging.StreamHandler(self.__log_capture)
        handler.setLevel(log_level)

        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        logging.getLogger().addHandler(handler)

        self.logger = logging.getLogger(self.module_name)

        httpclient_logger = logging.getLogger("http.client")
        httpclient_logger.propagate = True

        # See https://stackoverflow.com/questions/16337511/log-all-requests-from-the-python-requests-module
        def httpclient_logging_patch(level=logging.DEBUG):
            """Enable HTTPConnection debug logging to the logging framework"""

            def httpclient_log(*args):
                httpclient_logger.log(level, " ".join(args))

            import http.client

            http.client.print = httpclient_log
            http.client.HTTPConnection.debuglevel = 2

        httpclient_logging_patch()

    def get_log(self) -> str:
        """Returns the accumulated logs"""
        contents = self.__log_capture.getvalue()
        self.__log_capture.truncate(0)
        return contents

    @classmethod
    def process_debug(cls, f) -> Any:
        """Wraps the function to append the accumulated execution logs"""

        @wraps(f)
        def _impl(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            if self.debug:
                self.log_out = self.get_log()
                self.log_lines.append(self.log_out.splitlines())
            return result

        return _impl

    # @DeprecationWarning
    def _get_param(self, param, default=None) -> Any:
        """Fetches an Ansible input parameter if it exists, otherwise returns an optional default or None"""
        if self.module is not None:
            return self.module.params[param] if param in self.module.params else default
        return default

    def process_response(
        self,
        resp: Response,
        codes: List[CdpRestResponse] = [],
        error_message: str = None,
    ) -> Any:
        """Process a Response object according to expected outcomes"""

        for c in codes:
            if c.return_code == resp.status_code:
                if c.return_value is not None:
                    return c.return_value
                else:
                    results = resp.json()
                    if c.extract_field:
                        return results[c.extract_field]
                    else:
                        return results

        def _serialize(obj):
            if obj.__class__.__name__ == "CaseInsensitiveDict":
                return dict(obj)
            elif isinstance(obj, bytes):
                return obj.decode("utf-8")
            else:
                return obj

        if not error_message:
            error_message = "Call to URL %s failed." % resp.url

        clean_request = dict(
            [
                (k, _serialize(getattr(resp.request, k)))
                for k in dir(resp.request)
                if not k.startswith("_") and not callable(getattr(resp.request, k))
            ],
        )
        fail_payload = dict(
            msg=error_message,
            code=resp.status_code,
            resp=resp.text,
            req=clean_request,
        )

        if self.debug:
            log_out = self.get_log()
            fail_payload.update(sdk_out=log_out, sdk_out_lines=log_out.splitlines())

        self._session.close()
        self.module.fail_json(**fail_payload)

    def _assert_response(self, resp, expected_codes=None, message=None) -> None:
        if not expected_codes:
            expected_codes = []
        if not message:
            message = "Call to URL {} failed.".format(resp.url)
        if resp.status_code not in expected_codes:
            # try:
            def _serialize(obj):
                if obj.__class__.__name__ == "CaseInsensitiveDict":
                    return dict(obj)
                elif isinstance(obj, bytes):
                    return obj.decode("utf-8")
                else:
                    return obj

            # serialized_request = json.dumps(dict([(k, _serialize(getattr(resp.request, k))) for k in dir(resp.request) if not k.startswith('_') and not callable(getattr(resp.request, k))]))
            clean_request = dict(
                [
                    (k, _serialize(getattr(resp.request, k)))
                    for k in dir(resp.request)
                    if not k.startswith("_") and not callable(getattr(resp.request, k))
                ],
            )

            self._session.close()

            fail_payload = dict(
                msg=message,
                code=resp.status_code,
                resp=resp.text,
                req=clean_request,
            )
            # if self.debug:
            #     log_out = self.get_log()
            #     fail_payload.update(log_out=log_out, log_lines=log_out.splitlines())

            self.module.fail_json(**fail_payload)

    def _request(self, method, path, **kwargs) -> Response:
        url = "{}{}".format(self.endpoint, path)
        return self._session.request(method, url, **kwargs)

    def _get(self, path, **kwargs) -> Response:
        return self._request("GET", path, **kwargs)

    def _post(self, path, **kwargs) -> Response:
        return self._request("POST", path, **kwargs)

    def _put(self, path, **kwargs) -> Response:
        return self._request("PUT", path, **kwargs)

    def _delete(self, path, **kwargs) -> Response:
        return self._request("DELETE", path, **kwargs)

    def _options(self, path, **kwargs) -> Response:
        return self._request("OPTIONS", path, **kwargs)

    def _head(self, path, **kwargs) -> Response:
        return self._request("HEAD", path, **kwargs)

    def _patch(self, path, **kwargs) -> Response:
        return self._request("PATCH", path, **kwargs)

    def _isolated_request(self, method, path, **kwargs) -> Response:
        """Create and send a Request without using the existing Session."""
        payload = dict(
            method=method,
            url="{}{}".format(self.endpoint, path),
            auth=(self.username, self.password),
        )

        # Add headers to the request
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        # Add any custom headers defined at the module level
        for header_name, header_value in self.headers.items():
            kwargs["headers"][header_name] = header_value

        if get_param(self.module, "verify_tls"):
            if get_param(self.module, "ca_cert_file", None) is None:
                payload.update(verify=True)
            else:
                payload.update(verify=get_param(self.module, "ca_cert_file"))
        else:
            payload.update(verify=False)

        payload.update(**kwargs)
        return request(**payload)

    @property
    def status_codes(self) -> dict:
        return codes

    @staticmethod
    def merge_specs(*specs: dict) -> dict:
        if not specs:
            return
        base_spec = specs[0]
        for spec in specs[1:]:
            for key in spec.keys():
                if key not in base_spec:
                    base_spec[key] = spec[key]
                else:
                    if isinstance(spec[key], dict):
                        for option in spec[key]:
                            if option in base_spec[key]:
                                raise RuntimeError(
                                    "Duplicated key in [{}]: {}".format(key, option),
                                )
                            else:
                                base_spec[key][option] = spec[key][option]
                    elif isinstance(spec[key], list):
                        base_spec[key].extend(spec[key])
        return base_spec

    @staticmethod
    def module_spec(**spec: dict) -> dict:
        """Default Ansible Module spec values"""
        return CdpRestModule.merge_specs(
            dict(
                argument_spec=dict(
                    endpoint=dict(required=True, type="str", aliases=["url"]),
                    username=dict(required=True, type="str", aliases=["user", "usr"]),
                    password=dict(
                        required=True,
                        type="str",
                        aliases=["pass", "pwd"],
                        no_log=True,
                    ),
                    verify_tls=dict(
                        required=False,
                        type="bool",
                        default=True,
                        aliases=["tls"],
                    ),
                    ca_cert_file=dict(
                        required=False,
                        type="path",
                        aliases=["cert", "truststore"],
                    ),
                    agent_header=dict(
                        required=False,
                        type="str",
                        default="CDP_REST",
                        aliases=["agent"],
                    ),
                    headers=dict(
                        required=False,
                        type="dict",
                        default={},
                        aliases=["http_headers"],
                    ),
                    debug=dict(
                        required=False,
                        type="bool",
                        default=False,
                        aliases=["debug_endpoints"],
                    ),
                ),
            ),
            spec,
        )

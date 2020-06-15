#!/usr/bin/python
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

import json
import logging
import requests

from ansible.module_utils.basic import AnsibleModule


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: ml_workspace_env
short_description: Set environment variables for a Cloudera Machine Learning (CML) workspace
description:
  - Get environment variables for a Cloudera Machine Learning (CML) workspace.
  - The module supports check_mode.
  - The module supports the C(v1) API only.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  debug:
    description:
      - Flag to capture and return the debugging log of the underlying CDP SDK.
      - If set, the log level will be set from ERROR to DEBUG.
    aliases:
      - debug_cdpsdk
    default: False
    type: bool
"""

EXAMPLES = r"""

"""

RETURN = r"""
---
sdk_out:
    description: Returns the captured CDP SDK log.
    returned: when supported
    type: str
sdk_out_lines:
    description: Returns a list of each line of the captured CDP SDK log.
    returned: when supported
    type: list
    elements: str
"""


class MLWorkspaceEnv(AnsibleModule):
    def __init__(self, module):
        # Set parameters
        self.module = module
        self.endpoint = self._get_param("endpoint").strip("/")
        self.user = self._get_param("user")
        self.api_key = self._get_param("api_key")
        self.data = self._get_param("data")
        self.merge = self._get_param("merge")
        self.debug = self._get_param("debug")

        # Initialize the return values
        self.changed = False
        self.results = {}

        # Execute logic process
        self.process()

    def process(self):
        try:
            existing = self.get_env_vars()
            if self.merge:
                merged = existing.keys() | self.data.keys()
                payload = {
                    key: self.data.get(key) or existing.get(key) for key in merged
                }
            else:
                payload = self.data

            if not self.module.check_mode:
                if payload == existing:  # Shallow comparison
                    self.results = existing
                else:
                    self.changed = True
                    self.set_env_vars(payload)
                    self.results = self.get_env_vars()
        except ConnectionError as ce:
            self.module.fail_json(msg=str(ce))

    def set_env_vars(self, payload):
        env_endpoint = "/".join([self.endpoint, "api/v1/site/environment"])
        res = requests.put(
            env_endpoint,
            headers={"Content-Type": "application/json"},
            auth=(self.api_key, ""),
            data=json.dumps(payload),
        )
        if res.status_code != 204:
            response = res.json()
            self.module.fail_json(response["message"])

    def get_env_vars(self):
        env_endpoint = "/".join([self.endpoint, "api/v1/site/environment"])
        res = requests.get(
            env_endpoint,
            headers={"Content-Type": "application/json"},
            auth=(self.api_key, ""),
        )
        response = res.json()
        if res.status_code != 200:
            self.module.fail_json(response["message"])
        return response

    def _get_param(self, param, default=None):
        """Fetches an Ansible Input Parameter if it exists, else returns optional default or None"""
        if self.module is not None:
            return self.module.params[param] if param in self.module.params else default
        return default


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type="str", aliases=["url", "workspace_url"]),
            user=dict(required=True, type="str", aliases=["username"]),
            api_key=dict(required=True, type="str", no_log=True),
            data=dict(required=True, type="dict", aliases=["env", "env_vars"]),
            merge=dict(required=False, type="bool", default=False),
            debug=dict(required=False, type="bool", default=False),
        ),
        supports_check_mode=True,
    )

    result = MLWorkspaceEnv(module)

    output = dict(
        changed=result.changed,
        environment=result.results,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

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

from ansible_collections.cloudera.services.plugins.module_utils.ml import MLModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
module: ml_runtime_addons_info
short_description: Get runtime addon details for a Cloudera Machine Learning (CML) workspace
description:
  - Get runtime addon details for a Cloudera Machine Learning (CML) workspace.
  - The module supports check_mode.
  - The module supports the C(v2) API only.
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


class MLRuntimeAddonsInfo(MLModule):
    def __init__(self, module):
        super(MLRuntimeAddonsInfo, self).__init__(module)

        # Set parameters
        self.module = module
        self.identifier = self._get_param("identifier")
        self.component = self._get_param("component")
        self.name = self._get_param("name")
        self.status = self._get_param("status")

        # Initialize the return values
        self.changed = False
        self.runtime_addons = {}

        # Execute logic process
        self.process()

    @MLModule.process_debug
    def process(self):
        search_filter = dict()
        if self.identifier:
            search_filter["identifier"] = self.identifier
        if self.component:
            search_filter["component"] = self.component
        if self.name:
            search_filter["display_name"] = self.name
        if self.status:
            search_filter["status"] = self.status

        if search_filter:
            query_params = dict(
                search_filter=json.dumps(search_filter, separators=(",", ":")),
            )
            self.runtime_addons = self.query(
                method="GET",
                api=["runtimeaddons"],
                field="runtime_addons",
                params=query_params,
            )
        else:
            self.runtime_addons = self.query(
                method="GET",
                api=["runtimeaddons"],
                field="runtime_addons",
            )


def main():
    module = MLRuntimeAddonsInfo.ansible_module(
        argument_spec=dict(
            identifier=dict(required=False, type="str"),
            component=dict(required=False, type="str", choices=["HadoopCLI", "Spark"]),
            name=dict(required=False, type="str", aliases=["display_name"]),
            status=dict(required=False, type="str"),
        ),
        supports_check_mode=True,
    )

    result = MLRuntimeAddonsInfo(module)

    output = dict(
        changed=result.changed,
        runtime_addons=result.runtime_addons,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

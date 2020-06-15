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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.ml import MLModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: ml_runtimes_info
short_description: Get information for Cloudera Machine Learning (CML) runtimes
description:
  - Get information for the available Cloudera Machine Learning (CML) runtimes.
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


class MLRuntimesInfo(MLModule):
    def __init__(self, module):
        super(MLRuntimesInfo, self).__init__(module)

        # Set parameters
        self.image = self._get_param("image")
        self.editor = self._get_param("editor")
        self.kernel = self._get_param("kernel")
        self.edition = self._get_param("edition")
        self.desc = self._get_param("desc")
        self.version = self._get_param("version")

        # Initialize the return values
        self.runtimes = []

        # Execute logic process
        self.process()

    @MLModule.process_debug
    def process(self):
        search_filter = dict()
        if self.image:
            search_filter["image_identifier"] = self.image
        if self.editor:
            search_filter["editor"] = self.editor
        if self.kernel:
            search_filter["kernel"] = self.kernel
        if self.edition:
            search_filter["edition"] = self.edition
        if self.desc:
            search_filter["description"] = self.desc
        if self.version:
            search_filter["full_version"] = self.version

        if search_filter:
            query_params = dict(
                search_filter=json.dumps(search_filter, separators=(",", ":")),
            )
            self.runtimes = self.query(
                method="GET",
                api=["runtimes"],
                field="runtimes",
                params=query_params,
            )
        else:
            self.runtimes = self.query(method="GET", api=["runtimes"], field="runtimes")


def main():
    module = MLRuntimesInfo.ansible_module(
        argument_spec=dict(
            image=dict(required=False, type="str", aliases=["image_identifier"]),
            editor=dict(required=False, type="str"),
            kernel=dict(required=False, type="str"),
            edition=dict(required=False, type="str"),
            desc=dict(required=False, type="str", aliases=["description"]),
            version=dict(required=False, type="str", aliases=["full_version"]),
        ),
        supports_check_mode=True,
    )

    result = MLRuntimesInfo(module)

    output = dict(
        changed=False,
        runtimes=result.runtimes,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

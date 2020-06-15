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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.cdp_efm import (
    CdpEfmModule,
)

DOCUMENTATION = r"""
module: efm_designer_flow_info
short_description: ""
description: ""
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
extends_documentation_fragment:
  - cloudera.services.cdp_rest
"""

EXAMPLES = r"""
"""

RETURN = r"""
sdk_out:
    description: Returns the captured CDP REST API log.
    returned: when supported
    type: str
sdk_out_lines:
    description: Returns a list of each line of the captured CDP REST API log.
    returned: when supported
    type: list
    elements: str
"""


class CdpEfmDesignerFlowInfo(CdpEfmModule):
    def __init__(self, module):
        super(CdpEfmDesignerFlowInfo, self).__init__(
            module,
            "cloudera.services.efm_designer_flow_info",
        )

        self.name = self._get_param("name")

        # Initialize the return values
        self.changed = False
        self.elements = []

    @CdpEfmModule.process_debug
    def process(self):
        if self.name:
            results = self._get_designer_flow(self.name)
            if results:
                self.elements.append(results)
        else:
            for flow in self._get_designer_flows():
                self.elements.append(self._get_designer_flow(flow["identifier"]))


def main():
    module = AnsibleModule(
        **CdpEfmDesignerFlowInfo.module_spec(
            argument_spec=dict(
                name=dict(type="str", aliases=["flow", "flow_id"]),
            ),
            supports_check_mode=True,
        ),
    )

    result = CdpEfmDesignerFlowInfo(module)
    result.process()

    output = dict(
        changed=result.changed,
        elements=result.elements,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: efm_agent_class_info
short_description: Get the MiNiFi agent classes registered with EFM
description:
    - Get one or all MiNiFi Agent Classes registered with a Cloudera Edge Flow Manager (EFM) server.
author:
    - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
    - requests
options:
    name:
        description: Name of the Agent Class to retrieve
        type: str
extends_documentation_fragment:
    - cloudera.services.cdp_rest
"""

EXAMPLES = r"""
- name: List all Agent Classes
  cloudera.services.efm_agent_class_info:

- name: Retrieve the details for an individual Agent Class
  cloudera.services.efm_agent_class_info:
    name: minifi-example-01
"""

RETURN = r"""
---
agent_classes:
    description: List of Agent Classes registered with the EFM service.
    returned: always
    type: list
    elements: dict
    contains:
        name:
            description: Name of the Agent Class
            returned: always
            type: str
        description:
            description: Description of the Agent Class
            returned: when supported
            type: str
        agentManifests:
            description: List of identifiers of registered Agents
            returned: when supported
            type: list
            elements: str
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


class CdpEfmAgentClassInfo(CdpEfmModule):
    def __init__(self, module):
        super(CdpEfmAgentClassInfo, self).__init__(
            module,
            "cloudera.services.efm_agent_class_info",
        )

        self.name = self._get_param("name")

        # Initialize the return values
        self.changed = False
        self.agent_classes = []

    @CdpEfmModule.process_debug
    def process(self):
        if self.name:
            result = self._get_agent_class(self.name)
            if result:
                self.agent_classes.append(result)
        else:
            self.agent_classes = self._get_agent_classes()


def main():
    module = AnsibleModule(
        **CdpEfmAgentClassInfo.module_spec(
            argument_spec=dict(
                name=dict(),
            ),
            supports_check_mode=True,
        ),
    )

    result = CdpEfmAgentClassInfo(module)
    result.process()

    output = dict(
        changed=result.changed,
        agent_classes=result.agent_classes,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

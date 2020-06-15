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
module: efm_access_info
short_description: Return the current client's authenticated identity.
description:
  - Returns the current client's authenticated identity.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
extends_documentation_fragment:
  - cloudera.services.cdp_rest
"""

EXAMPLES = r"""
- name: Get client details
  cloudera.services.efm_access_info:
"""

RETURN = r"""
---
access:
    description:
        - Identity and access details
    returned: when supported
    type: dict
    contains:
        anonymous:
            description:
                - Flag indicating if access is anonymous
            returned: always
            type: bool
        canLogin:
            description:
                - Flag indicating if identity can log into EFM
            returned: always
            type: bool
        canLogout:
            description:
                - Flag indicating if identity can log out of EFM
            returned: always
            type: bool
        globalPermissions:
            description:
                - Access permissions for the identity
            returned: always
            type: dict
            contains:
                accessAdministration:
                    description:
                        - Flag indicating if identity has Administration access
                    returned: always
                    type: bool
        identity:
            description:
                - Username of the identity
            returned: always
            type: str
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


class CdpEfmInfo(CdpEfmModule):
    def __init__(self, module):
        super(CdpEfmInfo, self).__init__(module, "cloudera.services.efm_access_info")

        # Initialize the return value
        self.access = {}

    @CdpEfmModule.process_debug
    def process(self):
        resp = self._get("/efm/api/access")
        self._assert_response(
            resp,
            [self.status_codes.ok],
            "Failed to retrieve user info.",
        )
        self.access = resp.json()


def main():
    module = AnsibleModule(**CdpEfmInfo.module_spec())

    result = CdpEfmInfo(module)
    result.process()

    output = dict(
        changed=result.changed,
        access=result.access,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

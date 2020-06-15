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

DOCUMENTATION = r"""
module: ssb_user_info
short_description: Retrieve information about the current SSB user
description:
  - Retrieve information about the currently authenticated Cloudera SSB user.
  - Returns user profile data including username, email, active status, and keytab information.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
extends_documentation_fragment:
  - cloudera.services.services_client
"""

EXAMPLES = r"""
- name: Get current user information
  cloudera.services.ssb_user_info:
  register: current_user
"""

RETURN = r"""
user:
    description: Information about the current SSB user.
    returned: always
    type: dict
    contains:
        id:
            description: The unique identifier of the user.
            type: str
            returned: always
        username:
            description: The username of the user.
            type: str
            returned: always
        email:
            description: The email address of the user.
            type: str
            returned: when available
        first_name:
            description: The first name of the user.
            type: str
            returned: when available
        last_name:
            description: The last name of the user.
            type: str
            returned: when available
        is_active:
            description: Whether the user account is active.
            type: bool
            returned: when available
        primary_project_id:
            description: The ID of the user's primary project.
            type: str
            returned: when available
        project_id:
            description: The ID of the user's currently active project.
            type: str
            returned: when available
        keytab:
            description: Base64-encoded keytab data for the user.
            type: str
            returned: when available
        keytab_principal:
            description: The Kerberos principal associated with the user's keytab.
            type: str
            returned: when available
        keytab_last_modified:
            description: Timestamp of when the keytab was last modified.
            type: str
            returned: when available
        granted_authorities:
            description: List of roles and authorities granted to the user.
            type: list
            elements: str
            returned: when available
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

from typing import Any, Dict, Optional

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUser,
    SsbUserClient,
)


class SsbUserInfoModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(),
            supports_check_mode=True,
        )

        # Initialize result variables
        self.user: Optional[SsbUser] = None

    def process(self) -> None:
        client = SsbUserClient(self.api_client)
        self.user = client.get_current_user()


def main():
    result = SsbUserInfoModule()

    output: Dict[str, Any] = dict(
        changed=False,
        user=to_dict(result.user) if result.user else {},
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

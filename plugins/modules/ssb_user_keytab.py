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
module: ssb_user_keytab
short_description: Set the user keytab in SSB
description:
  - Set or remove the user keytab in Cloudera SSB.
  - The module can either upload an existing keytab file or data, or generate a new keytab using a provided password.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
  - "Andre Araujo (@asdaraujo)"
version_added: "1.0.0"
options:
  principal:
    description:
      - The Kerberos principal associated with the keytab.
      - This parameter is required when O(state) is C(present).
    type: str
    required: false
  keytab_password:
    description:
      - The password to use to generate a new keytab.
      - This parameter is mutually exclusive with O(keytab_file) and O(keytab_base64).
      - This parameter is not logged.
    type: str
    required: false
  keytab_file:
    description:
      - The path to an existing keytab file to upload.
      - This parameter is mutually exclusive with O(keytab_password) and O(keytab_base64).
    type: str
    required: false
  keytab_base64:
    description:
      - The raw data of an existing keytab to upload as base64.
      - This parameter is mutually exclusive with O(keytab_password) and O(keytab_file).
      - This parameter is not logged.
    type: str
    required: false
  state:
    description:
      - The desired state of the keytab.
    type: str
    choices:
      - present
      - absent
    default: present
    required: false
extends_documentation_fragment:
  - cloudera.services.services_client
"""

EXAMPLES = r"""
- name: Generate a new keytab for a user
  cloudera.services.ssb_user_keytab:
    principal: "user@REALM.COM"
    keytab_password: "password"
    state: present

- name: Upload an existing keytab file for a user
  cloudera.services.ssb_user_keytab:
    principal: "user@REALM.COM"
    keytab_file: "/path/to/user.keytab"
    state: present

- name: Upload an existing keytab from base64 data for a user
  cloudera.services.ssb_user_keytab:
    principal: "user@REALM.COM"
    keytab_base64: "{{ lookup('file', '/path/to/user.keytab') | ansible.builtin.b64encode }}"
    state: present

- name: Remove the keytab for a user
  cloudera.services.ssb_user_keytab:
    principal: "user@REALM.COM"
    state: absent
"""

RETURN = r"""
principal:
    description: The Kerberos principal associated with the keytab.
    returned: when O(state=present)
    type: str
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

from base64 import b64decode
from typing import Any, Dict

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUserKeytab,
    SsbUserKeytabClient,
)


class SsbUserKeytabModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                principal=dict(required=False, type="str"),
                keytab_password=dict(required=False, type="str", no_log=True),
                keytab_file=dict(required=False, type="path"),
                keytab_base64=dict(required=False, type="str", no_log=True),
                state=dict(
                    required=False,
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
            ),
            mutually_exclusive=[
                ["keytab_file", "keytab_base64"],
                ["keytab_password", "keytab_file"],
                ["keytab_password", "keytab_base64"],
            ],
            required_if=[
                ["state", "present", ["principal"], False],
                [
                    "state",
                    "present",
                    ["keytab_file", "keytab_base64", "keytab_password"],
                    True,
                ],
            ],
            supports_check_mode=True,
        )

        # Set parameters
        self.principal = self.get_param("principal")
        self.keytab_password = self.get_param("keytab_password")
        self.keytab_file = self.get_param("keytab_file")
        self.keytab_base64 = self.get_param("keytab_base64")
        self.state = self.get_param("state")

        # Initialize result variables
        self.output_principal: str = ""

    def process(self):
        client = SsbUserKeytabClient(self.api_client)

        if self.state == "present":
            if not self.module.check_mode:

                # Clear any existing keytab
                client.delete_keytab()

                if self.keytab_password:
                    user_keytab: SsbUserKeytab = client.generate_keytab(
                        principal=self.principal,
                        password=self.keytab_password,
                    )
                elif self.keytab_base64:
                    keytab_data = b64decode(self.keytab_base64)
                    user_keytab: SsbUserKeytab = client.upload_keytab(
                        principal=self.principal,
                        keytab_data=keytab_data,
                    )
                else:
                    user_keytab: SsbUserKeytab = client.upload_keytab(
                        principal=self.principal,
                        keytab_file=self.keytab_file,
                    )
                self.output_principal = user_keytab.principal
        elif self.state == "absent":
            if not self.module.check_mode:
                client.delete_keytab()


def main():
    result = SsbUserKeytabModule()

    output: Dict[str, Any] = dict(
        changed=True,
        principal=result.output_principal,
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

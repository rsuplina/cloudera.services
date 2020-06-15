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

from ansible_collections.cloudera.services.plugins.module_utils.ranger_utils import (
    RangerModule,
)
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: ranger_role_info
short_description: Retrieve role details from Apache Ranger
description:
  - Retrieve details of a specific role by ID or name.
  - If no identifier is provided, retrieves all roles.
author:
  - "Webster Mudge (@wmudge)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.0.0"
requirements:
  - apache-ranger
options:
  name:
    description:
      - Name of the Ranger role.
    type: str
    required: false
  id:
    description:
      - ID of the Ranger role to retrieve.
    type: str
    required: false
extends_documentation_fragment:
  - cloudera.services.ranger
"""

EXAMPLES = r"""
---
- name: Retrieve role by ID
  cloudera.services.ranger_role_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    id: 5

- name: Retrieve role by name
  cloudera.services.ranger_role_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "test_user_role"

- name: Retrieve all roles
  cloudera.services.ranger_role_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
"""

RETURN = r"""
---
roles:
  description:
    - List of roles matching the given criteria, or all roles if no filter is applied.
  type: list
  elements: dict
  returned: always
  contains:
    id:
      description:
        - Unique numeric ID of the role.
      type: int
      returned: always
    is_enabled:
      description:
        - Whether the role is currently enabled.
      type: bool
      returned: always
    created_by:
      description:
        - Username of the role creator.
      type: str
      returned: always
    updated_by:
      description:
        - Username of the last person who updated the role.
      type: str
      returned: always
    create_time:
      description:
        - Epoch timestamp when the role was created.
      type: int
      returned: always
    update_time:
      description:
        - Epoch timestamp when the role was last updated.
      type: int
      returned: always
    name:
      description:
        - Name of the role.
      type: str
      returned: always
    description:
      description:
        - Optional description of the role.
      type: str
      returned: always
    users:
      description:
        - List of users assigned to this role.
      type: list
      elements: dict
      returned: always
    groups:
      description:
        - List of groups assigned to this role.
      type: list
      elements: dict
      returned: always
    roles:
      description:
        - List of roles assigned to this role.
      type: list
      elements: dict
      returned: always
"""


class RoleInfo(RangerModule):
    def __init__(self, module):
        super(RoleInfo, self).__init__(module)

        # Set parameters
        self.name = self.get_param("name")
        self.id = self.get_param("id")

        # Initialize the return values
        self.output = []

        # Execute logic process
        self.process()

    def process(self):
        try:
            if self.id:
                self.output = [self.ranger.get_role_by_id(self.id)]
            elif self.name:
                self.output = [
                    self.ranger.get_role(
                        roleName=self.name,
                        execUser=None,
                        serviceName=None,
                    ),
                ]
            else:
                self.output = self.ranger.find_roles()

            self.output = [camel_dict_to_snake_dict(r) for r in self.output]

        except Exception as e:
            self.module.fail_json(msg=f"Failed to retrieve role: {str(e)}")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type="str"),
            username=dict(required=True, type="str"),
            password=dict(required=True, type="str", no_log=True),
            verify_tls=dict(required=False, type="bool", default=True),
            ssl_ca_cert=dict(required=False, type="str"),
            name=dict(required=False, type="str"),
            id=dict(required=False, type="int"),
        ),
        supports_check_mode=True,
    )

    result = RoleInfo(module)

    output = dict(
        changed=False,
        roles=result.output,
    )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

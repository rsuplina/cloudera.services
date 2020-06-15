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
from ansible.module_utils.common.dict_transformations import (
    camel_dict_to_snake_dict,
    recursive_diff,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.ranger_utils import (
    populate_role_payload,
    clean_dict,
)


DOCUMENTATION = r"""
module: ranger_role
short_description: Manage (create, update, delete) roles in Apache Ranger
description:
  - Create, update, or delete roles in Apache Ranger using the REST API.
  - If a role with the specified name exists, it will be updated.
  - If it does not exist and state is C(present), it will be created.
  - If it exists and state is C(absent), it will be deleted.
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
    required: true
    type: str
  state:
    description:
      - Whether the role should be present or absent.
    required: false
    type: str
    choices: ["present", "absent"]
    default: "present"
  service:
    description:
      - Optional service associated with the role.
    required: false
    type: str
  description:
    description:
      - Description of the Ranger role.
    required: false
    type: str
  users:
    description:
      - List of users to assign to the role.
      - Each item should be a dictionary with C(name) and optional C(is_admin) boolean.
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Username to assign to the role.
        required: true
        type: str
      is_admin:
        description:
          - Whether the user is an admin in this role.
        required: true
        type: bool
  groups:
    description:
      - List of groups to assign to the role.
      - Each item should be a dictionary with C(name) and optional C(is_admin) boolean.
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Group to assign to the role.
        required: true
        type: str
      is_admin:
        description:
          - Whether the group is an admin in this role.
        required: true
        type: bool
  roles:
    description:
      - List of nested roles to assign to the role.
      - Each item should be a dictionary with C(name) and optional C(is_admin) boolean.
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Role to assign to the role.
        required: true
        type: str
      is_admin:
        description:
          - Whether the role is an admin in this role.
        required: true
        type: bool
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.services.ranger
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
"""

EXAMPLES = r"""
- name: Create a new Ranger role
  cloudera.services.ranger_role:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    verify_tls: false
    name: "test_role_00"
    service: "cm_hdfs"
    description: "Role for HDFS users"
    users:
      - name: "admin"
        is_admin: false
      - name: "atlas"
        is_admin: true
    groups:
      - name: "atlas"
        is_admin: true
    state: "present"

- name: Update an existing Ranger role
  cloudera.services.ranger_role:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "test_role_01"
    description: "Updated description for HDFS users"
    users:
      - name: "nifi"
        is_admin: false
      - name: "new_user"
        is_admin: true
    groups:
      - name: "atlas"
        is_admin: true
    roles:
      - name: "superuser_role"
        is_admin: true
    state: "present"

- name: Delete a Ranger role
  cloudera.services.ranger_role:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "test_role_01"
    state: "absent"
"""

RETURN = r"""
role:
  description:
    - A dictionary containing details about the role.
  type: dict
  elements: complex
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


class Role(RangerModule):
    def __init__(self, module):
        super(Role, self).__init__(module)

        # Set parameters

        self.name = self.get_param("name")
        self.description = self.get_param("description")
        self.service = self.get_param("service")
        self.state = self.get_param("state")
        self.users = self.get_param("users")
        self.groups = self.get_param("groups")
        self.roles = self.get_param("roles")

        # Initialize the return values
        self.changed = False
        self.diff = dict(before=dict(), after=dict())
        self.output = []

        # Execute logic process
        self.process()

    def process(self):
        try:
            roles = self.ranger.find_roles()
            existing_role = {}
            for role in roles:
                if role["name"] == self.name:
                    existing_role = self.ranger.get_role_by_id(roleId=role["id"])
                    break
            incoming_role = populate_role_payload(self)

            if self.state == "present":
                if existing_role:
                    existing_role = clean_dict(existing_role)
                    incoming_role = clean_dict(incoming_role)

                    if self.module._diff:
                        before_diff, after_diff = recursive_diff(
                            existing_role,
                            incoming_role,
                        )
                        self.diff.update(before=before_diff, after=after_diff)

                    if not self.module.check_mode:
                        self.output = self.ranger.update_role(
                            roleId=role.id,
                            role=incoming_role,
                        )
                else:
                    self.output = self.ranger.create_role(
                        serviceName=self.service,
                        role=incoming_role,
                    )
                self.changed = True
                self.output = camel_dict_to_snake_dict(self.output)

            if self.state == "absent":
                if existing_role:
                    self.changed = True
                    if self.module._diff:
                        self.diff = dict(before=existing_role, after=dict())
                    if not self.module.check_mode:
                        self.output = self.ranger.delete_role_by_id(roleId=role.id)
        except Exception as e:
            self.module.fail_json(msg=f"Role processing failed: {str(e)}")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type="str"),
            username=dict(required=True, type="str"),
            password=dict(required=True, type="str", no_log=True),
            verify_tls=dict(required=False, type="bool", default=True),
            ssl_ca_cert=dict(required=False, type="str"),
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            name=dict(required=True, type="str"),
            service=dict(required=False, type="str"),
            description=dict(required=False, type="str"),
            users=dict(
                required=False,
                type="list",
                elements="dict",
                options=dict(
                    name=dict(required=True, type="str"),
                    is_admin=dict(required=False, type="bool"),
                ),
            ),
            groups=dict(
                required=False,
                type="list",
                elements="dict",
                options=dict(
                    name=dict(required=True, type="str"),
                    is_admin=dict(required=False, type="bool"),
                ),
            ),
            roles=dict(
                required=False,
                type="list",
                elements="dict",
                options=dict(
                    name=dict(required=True, type="str"),
                    is_admin=dict(required=False, type="bool"),
                ),
            ),
        ),
        supports_check_mode=True,
    )

    result = Role(module)

    output = dict(
        changed=result.changed,
        role=result.output,
    )
    if module._diff:
        output.update(diff=result.diff)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

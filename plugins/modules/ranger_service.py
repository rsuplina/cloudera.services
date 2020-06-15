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
    RangerMutableModule,
)
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.common.dict_transformations import (
    camel_dict_to_snake_dict,
    recursive_diff,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.ranger_utils import (
    populate_service_payload,
    clean_dict,
)


DOCUMENTATION = r"""
module: ranger_service
short_description: Manage services in Apache Ranger
description:
  - Create, update, or delete services in Apache Ranger.
  - This module replaces existing services entirely when changes are detected.
  - It does not perform partial merges of services configfs or audit filters.
  - If it does not exist and state is C(present), service will be created.
  - If it exists and state is C(absent), service will be deleted.
author:
  - "Webster Mudge (@wmudge)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.0.0"
requirements:
  - apache-ranger
options:
  name:
    description:
      - Name of the Ranger service
    required: true
    type: str
  type:
    description:
      - Type of the Ranger service (e.g., hdfs, hive).
    type: str
    required: false
  display_name:
    description:
      - Display name for the Ranger service.
    type: str
    required: false
  enabled:
    description:
      - Whether the policy is enabled.
    type: bool
    default: true
    aliases:
      - is_enabled
  description:
    description:
      - Description of the service.
    type: str
    required: false
  tag_service:
    description:
      - The name of the tag service associated with this service.
    type: str
    required: false
  configs:
    description:
      - A dictionary of configuration properties specific to the service type.
    type: dict
    required: false
  state:
    description:
      - Whether the service should be present or absent.
    type: str
    required: false
    default: present
    choices: ["present", "absent"]
extends_documentation_fragment:
  - cloudera.services.ranger
"""

EXAMPLES = r"""
- name: Create a Ranger service
  cloudera.services.ranger_service:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    password: "changeme"
    name: "test02"
    type: "hdfs"
    configs:
      username: "hdfs"
      password: "hdfs"
      fs.default.name: "hdfs://namenode:8020"
      hadoop.security.authentication: "simple"
      hadoop.security.authorization: "true"

- name: Delete Ranger service
  cloudera.services.ranger_service:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "test02"
    state: "absent"
"""

RETURN = r"""
service:
  description:
    - A dictionary containing details about the service.
  type: dict
  returned: always
  contains:
    id:
      description:
        - Unique numeric ID of the service.
      type: int
      returned: always
    guid:
      description:
        - Globally unique identifier of the service.
      type: str
      returned: always
    is_enabled:
      description:
        - Whether the service is enabled.
      type: bool
      returned: always
    created_by:
      description:
        - Username of the creator of the service.
      type: str
      returned: always
    updated_by:
      description:
        - Username of the last user who updated the service.
      type: str
      returned: always
    create_time:
      description:
        - Timestamp of when the service was created (epoch millis).
      type: int
      returned: always
    update_time:
      description:
        - Timestamp of the last update (epoch millis).
      type: int
      returned: always
    version:
      description:
        - Version number of the service definition.
      type: int
      returned: always
    type:
      description:
        - Service type (e.g., hdfs, hive, kafka).
      type: str
      returned: always
    name:
      description:
        - Internal name of the service.
      type: str
      returned: always
    display_name:
      description:
        - Display name of the service.
      type: str
      returned: always
    description:
      description:
        - Description of the service.
      type: str
      returned: always
    tag_service:
      description:
        - Name of the tag-based service used for classification.
      type: str
      returned: sometimes
    configs:
      description:
        - Dictionary of service configuration properties.
      type: dict
      returned: always
    policy_version:
      description:
        - Version number of the policy associated with this service.
      type: int
      returned: always
    policy_update_time:
      description:
        - Timestamp of the last policy update (epoch millis).
      type: int
      returned: always
    tag_version:
      description:
        - Version number of the tag policy for the service.
      type: int
      returned: sometimes
    tag_update_time:
      description:
        - Timestamp of the last tag policy update (epoch millis).
      type: int
      returned: sometimes
"""


class Service(RangerMutableModule):
    def __init__(self, module):
        super(Service, self).__init__(module)

        # Set parameters
        self.endpoint = self.get_param("endpoint")
        self.username = self.get_param("username")
        self.password = self.get_param("password")

        self.name = self.get_param("name")
        self.type = self.get_param("type")
        self.enabled = self.get_param("enabled")

        self.display_name = self.get_param("display_name")
        self.description = self.get_param("description")
        self.tag_service = self.get_param("tag_service")
        self.configs = self.get_param("configs")
        self.state = self.get_param("state")

        # Initialize the return values
        self.changed = False
        self.diff = dict(before=dict(), after=dict())
        self.output = []

        # Execute logic process
        self.process()

    def process(self):
        try:
            existing_service = {}
            existing_service = self.ranger.get_service(serviceName=self.name)
            incoming_service = populate_service_payload(self)

            if self.state == "present":
                if existing_service:
                    existing_service = clean_dict(existing_service)
                    incoming_service = clean_dict(incoming_service)

                    if self.module._diff:
                        before_diff, after_diff = recursive_diff(
                            existing_service,
                            incoming_service,
                        )
                        self.diff.update(before=before_diff, after=after_diff)

                    if not self.module.check_mode:
                        self.changed = True
                        self.output = self.ranger.update_service(
                            serviceName=self.name,
                            service=incoming_service,
                        )
                else:
                    self.output = self.ranger.create_service(service=incoming_service)
                self.output = camel_dict_to_snake_dict(self.output)

            if self.state == "absent":
                if existing_service:
                    self.changed = True
                    if self.module._diff:
                        self.diff = dict(before=existing_service, after=dict())
                    if not self.module.check_mode:
                        self.output = self.ranger.delete_service(serviceName=self.name)

        except Exception as e:
            self.module.fail_json(msg=f"Failed to retrieve service: {str(e)}")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type="str"),
            username=dict(required=True, type="str"),
            password=dict(required=True, type="str", no_log=True),
            verify_tls=dict(required=False, type="bool", default=True),
            ssl_ca_cert=dict(required=False, type="str"),
            name=dict(required=True, type="str"),
            type=dict(required=False, type="str"),
            enabled=dict(
                required=False,
                type="bool",
                default="True",
                aliases=["is_enabled"],
            ),
            display_name=dict(required=False, type="str"),
            description=dict(required=False, type="str"),
            tag_service=dict(required=False, type="str"),
            configs=dict(required=False, type="dict"),
            state=dict(default="present", choices=["present", "absent"]),
        ),
        supports_check_mode=True,
    )

    result = Service(module)

    output = dict(
        changed=result.changed,
        service=result.output,
    )
    if module._diff:
        output.update(diff=result.diff)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

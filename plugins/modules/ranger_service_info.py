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
from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
module: ranger_service_info
short_description: Retrieve service details from Apache Ranger
description:
  - Retrieve details of a specific service by ID or name.
  - If no identifier is provided, retrieves all services.
author:
  - "Webster Mudge (@wmudge)"
  - "Ronald Suplina (@rsuplina)"
version_added: "1.0.0"
requirements:
  - apache-ranger
options:
  name:
    description:
      - Name of the Ranger service.
    type: str
    required: false
  id:
    description:
      - ID of the Ranger service to retrieve.
    type: str
    required: false
extends_documentation_fragment:
  - cloudera.services.ranger
"""

EXAMPLES = r"""
- name: Retrieve service by ID
  cloudera.services.ranger_service_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    id: 5

- name: Retrieve service by name
  cloudera.services.ranger_service_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "test_service"

- name: Retrieve all services
  cloudera.services.ranger_service_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
"""

RETURN = r"""
services:
  description:
    - List of Ranger services matching the given criteria, or all services if no filter is applied.
  type: list
  elements: dict
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


class ServiceInfo(RangerMutableModule):
    def __init__(self, module):
        super(ServiceInfo, self).__init__(module)

        # Set parameters
        self.endpoint = self.get_param("endpoint")
        self.username = self.get_param("username")
        self.password = self.get_param("password")

        self.name = self.get_param("name")
        self.id = self.get_param("id")

        # Initialize the return values
        self.changed = False
        self.output = []

        # Execute logic process
        self.process()

    def process(self):
        try:
            if self.id:
                self.output = [self.ranger.get_service_by_id(self.id)]
            elif self.name:
                self.output = [self.ranger.get_service(serviceName=self.name)]
            else:
                self.output = self.ranger.find_services()

            self.output = [camel_dict_to_snake_dict(r) for r in self.output]

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
            name=dict(required=False, type="str"),
            id=dict(required=False, type="int"),
        ),
        supports_check_mode=False,
    )

    result = ServiceInfo(module)

    output = dict(
        changed=result.changed,
        services=result.output,
    )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

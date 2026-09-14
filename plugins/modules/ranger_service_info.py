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
module: ranger_service_info
short_description: Retrieve service details from Apache Ranger
description:
  - Retrieve details of a specific service by ID or name.
  - If no identifier is provided, retrieves all services.
  - The module supports C(check_mode).
version_added: "1.1.0"
author:
  - "Ronald Suplina (@rsuplina)"
options:
  name:
    description:
      - Name of the Ranger service.
      - This parameter is mutually exclusive with O(id).
    type: str
    required: false
  id:
    description:
      - ID of the Ranger service to retrieve.
      - This parameter is mutually exclusive with O(name).
    type: int
    required: false
extends_documentation_fragment:
  - cloudera.services.services_client
"""

EXAMPLES = r"""
# NOTE: Examples do not include connection and authentication fields

- name: Retrieve service by ID
  cloudera.services.ranger_service_info:
    id: 5

- name: Retrieve service by name
  cloudera.services.ranger_service_info:
    name: "test_service"

- name: Retrieve all services
  cloudera.services.ranger_service_info:
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

from typing import Any, Dict, List

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerService,
    RangerServiceClient,
)


class RangerServiceInfoModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(type="str", required=False),
                id=dict(type="int", required=False),
            ),
            mutually_exclusive=[["name", "id"]],
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")
        self.id = self.get_param("id")

        # Initialize result variables
        self.service_list: List[RangerService] = []

    def process(self) -> None:
        client = RangerServiceClient(self.api_client)

        if self.id:
            service = client.get_service_by_id(service_id=self.id)
            if service:
                self.service_list.append(service)

        elif self.name:
            service = client.get_service_by_name(service_name=self.name)
            if service:
                self.service_list.append(service)

        else:
            self.service_list.extend(client.list_services())


def main():
    result = RangerServiceInfoModule()

    output: Dict[str, Any] = dict(
        changed=False,
        services=[to_dict(service) for service in result.service_list],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

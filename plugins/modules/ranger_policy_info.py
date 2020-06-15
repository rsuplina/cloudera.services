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
---
module: ranger_policy_info
short_description: Retrieve policy details from Apache Ranger
description:
  - Retrieve details of a specific policy by ID or name and service.
  - If no identifier is provided, retrieves all policies or all policies within a given service.
  - The module supports C(check_mode).
author:
  - "Ronald Suplina (@rsuplina)"
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
options:
  service:
    description:
      - Name of the Ranger service associated with the policy.
      - When provided with O(name), retrieves a specific policy.
      - When provided alone, retrieves all policies for the service.
    type: str
    required: false
  name:
    description:
      - Name of the Ranger policy.
      - This parameter is mutually exclusive with O(policy_id).
    type: str
    required: false
    aliases:
      - policy_name
  policy_id:
    description:
      - ID of the Ranger policy to retrieve.
      - This parameter is mutually exclusive with O(name).
    type: int
    required: false
extends_documentation_fragment:
  - cloudera.services.ranger
"""

EXAMPLES = r"""
---
- name: Retrieve policy by ID
  cloudera.services.ranger_policy_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    policy_id: 67

- name: Retrieve policy by name and service
  cloudera.services.ranger_policy_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "all - global"
    service: "hive"

- name: Retrieve all policies in a specific service
  cloudera.services.ranger_policy_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    service: "hive"

- name: Retrieve all policies
  cloudera.services.ranger_policy_info:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
"""

RETURN = r"""
---
policies:
  description:
    - List of policies matching the given criteria, or all policies if no filter is applied.
  type: list
  elements: dict
  returned: always
  contains:
    id:
      description:
        - Unique numeric ID of the policy.
      type: int
      returned: always
    guid:
      description:
        - Globally unique identifier for the policy.
      type: str
      returned: always
    is_enabled:
      description:
        - Whether the policy is currently enabled.
      type: bool
      returned: always
    created_by:
      description:
        - Username of the policy creator.
      type: str
      returned: always
    updated_by:
      description:
        - Username of the last person who updated the policy.
      type: str
      returned: always
    create_time:
      description:
        - Epoch timestamp when the policy was created.
      type: int
      returned: always
    update_time:
      description:
        - Epoch timestamp when the policy was last updated.
      type: int
      returned: always
    version:
      description:
        - Version number of the policy.
      type: int
      returned: always
    service:
      description:
        - Name of the service this policy applies to.
      type: str
      returned: always
    name:
      description:
        - Name of the policy.
      type: str
      returned: always
    policy_type:
      description:
        - Numeric identifier for the type of policy.
      type: int
      returned: always
    policy_priority:
      description:
        - Priority value for the policy.
      type: int
      returned: always
    description:
      description:
        - Optional description of the policy.
      type: str
      returned: always
    resource_signature:
      description:
        - Signature hash of the resources in the policy.
      type: str
      returned: always
    is_audit_enabled:
      description:
        - Whether auditing is enabled for the policy.
      type: bool
      returned: always
    resources:
      description:
        - Dictionary of resources the policy applies to.
      type: dict
      returned: always
    conditions:
      description:
        - List of policy conditions.
      type: list
      returned: always
    policy_items:
      description:
        - List of allow policy items.
      type: list
      returned: always
    deny_policy_items:
      description:
        - List of deny policy items.
      type: list
      returned: always
    allow_exceptions:
      description:
        - List of allow exception policy items.
      type: list
      returned: always
    deny_exceptions:
      description:
        - List of deny exception policy items.
      type: list
      returned: always
    data_mask_policy_items:
      description:
        - List of data mask policy items.
      type: list
      returned: always
    row_filter_policy_items:
      description:
        - List of row filter policy items.
      type: list
      returned: always
    service_type:
      description:
        - Type of the service (e.g., hive, hdfs) this policy applies to.
      type: str
      returned: always
    options:
      description:
        - Dictionary of policy options.
      type: dict
      returned: always
    validity_schedules:
      description:
        - List of validity schedules attached to the policy.
      type: list
      returned: always
    policy_labels:
      description:
        - List of policy labels.
      type: list
      returned: always
    zone_name:
      description:
        - Name of the security zone this policy belongs to.
      type: str
      returned: always
    is_deny_all_else:
      description:
        - Whether the policy denies all accesses not explicitly allowed.
      type: bool
      returned: always
"""

from typing import Any, Dict, List

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyClient,
)


class RangerPolicyInfoModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(type="str", required=False, aliases=["policy_name"]),
                policy_id=dict(type="int", required=False),
                service=dict(type="str", required=False),
            ),
            mutually_exclusive=[["name", "policy_id"]],
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")
        self.policy_id = self.get_param("policy_id")
        self.service = self.get_param("service")

        # Initialize result variables
        self.policy_list: List[RangerPolicy] = []

    def process(self) -> None:
        client = RangerPolicyClient(self.api_client)

        if self.policy_id:
            # Get policy by ID
            policy = client.get_policy_by_id(policy_id=self.policy_id)
            if policy:
                self.policy_list.append(policy)

        elif self.name:
            # Get policy by name (and optionally service)
            if self.service:
                policy = client.get_policy_by_name(
                    service_name=self.service,
                    policy_name=self.name,
                )
                if policy:
                    self.policy_list.append(policy)
            else:
                # If no service specified, search all policies for matching name
                policies = client.list_policies()
                self.policy_list.extend([p for p in policies if p.name == self.name])

        elif self.service:
            # List all policies for a service
            self.policy_list.extend(client.list_policies(service_name=self.service))

        else:
            # List all policies
            self.policy_list.extend(client.list_policies())


def main():
    result = RangerPolicyInfoModule()

    output: Dict[str, Any] = dict(
        changed=False,
        policies=[to_dict(policy) for policy in result.policy_list],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

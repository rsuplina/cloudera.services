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
module: ranger_policy
short_description: Manage policies in Apache Ranger
description:
  - Create, update, or delete policies in Apache Ranger.
  - This module replaces existing policies entirely when changes are detected.
  - It does not perform partial merges of access rules or user permissions.
author:
  - "Ronald Suplina (@rsuplina)"
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - apache-ranger
options:
  state:
    description:
      - Whether the policy should be present or absent.
    type: str
    choices: ["present", "absent"]
    default: present
  service:
    description:
      - Name of the Ranger service associated with the policy.
    type: str
    required: true
  name:
    description:
      - Name of the policy.
    type: str
    required: true
  enabled:
    description:
      - Whether the policy is enabled.
    type: bool
    default: true
    aliases:
      - is_enabled
  resources:
    description:
      - Dictionary of resource definitions for the policy.
    type: dict
    required: false
  policy_type:
    description:
      - Type of the policy (e.g., 0 for access, 1 for data mask, 2 for row filter).
    type: int
    default: 0
  policy_priority:
    description:
      - Priority of the policy.
    type: int
    required: false
  description:
    description:
      - Description of the policy.
    type: str
    required: false
  resource_signature:
    description:
      - Resource signature for the policy.
    type: str
    required: false
    aliases:
      - signature
  audit_enabled:
    description:
      - Whether auditing is enabled for the policy.
    type: bool
    default: true
    aliases:
      - is_audit_enabled
  additional_resources:
    description:
      - Additional resource definitions.
    type: list
    elements: dict
    required: false
  access_policies:
    description:
      - List of allow policy items.
    type: list
    elements: dict
    required: false
    aliases:
      - policy_items
  deny_policies:
    description:
      - List of deny policy items.
    type: list
    elements: dict
    required: false
    aliases:
      - deny_policy_items
  allow_exceptions:
    description:
      - List of allow exception policy items.
    type: list
    elements: dict
    required: false
  deny_exceptions:
    description:
      - List of deny exception policy items.
    type: list
    elements: dict
    required: false
  data_mask_policies:
    description:
      - List of data masking policy items.
    type: list
    elements: dict
    required: false
    aliases:
      - data_mask_policy_items
  row_filter_policies:
    description:
      - List of row filtering policy items.
    type: list
    elements: dict
    required: false
    aliases:
      - row_filter_policy_items
  service_type:
    description:
      - Type of the service (e.g., hive, hdfs, etc.).
    type: str
    required: false
  options:
    description:
      - Dictionary of additional options for the policy.
    type: dict
    required: false
  validity_schedules:
    description:
      - Time-based policy schedules.
    type: list
    elements: dict
    required: false
  policy_labels:
    description:
      - List of labels associated with the policy.
    type: list
    elements: str
    required: false
  zone_name:
    description:
      - Name of the security zone the policy belongs to.
    type: str
    required: false
  conditions:
    description:
      - List of custom conditions for the policy.
    type: list
    elements: dict
    required: false
  deny_all:
    description:
      - Whether to deny all other requests not matching the policy.
    type: bool
    aliases:
      - deny_all_else
      - is_deny_all_else
  merged:
    description:
      - Whether to merge the provided policy items with the existing policy or replace it entirely.
      - When C(true), the module will add new users, groups, and accesses to existing policy items by concatenating lists.
      - When C(false), the module performs full replacement (default behavior).
      - This is useful when you want to add users to an existing policy without having to specify all existing users.
    type: bool
    default: false
extends_documentation_fragment:
  - ansible.builtin.action_common_attributes
  - cloudera.services.ranger
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
notes:
  - When I(merged=false) (default), the module performs full replacements of existing policies rather than merges.
  - If the desired state differs from the current policy, the existing policy will be fully overwritten with the new definition.
  - This guarantees consistent, predictable updates and avoids the risk of duplicate or conflicting entries.
  - When I(merged=true), the module will concatenate lists (users, groups, accesses) with existing ones.
  - Merge mode is useful for adding users, groups, or accesses to existing policies without specifying all current values.
  - However, merge mode may create duplicate entries in lists if the same values are provided multiple times.
  - Use merge mode carefully and verify the results when working with complex policies.
"""

EXAMPLES = r"""
- name: Create a basic Ranger policy
  cloud.runtime.ranger_policy:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "Test Policy 2"
    service: "cm_hdfs"
    service_type: "hdfs"
    description: "Description1"
    resources:
      path:
        values:
          - "/hbase/archive2"

- name: Update an existing Ranger policy
  cloud.runtime.ranger_policy:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "Policy test create request"
    service: "cm_hdfs"
    resources:
      path:
        values:
          - "/tmp/test"


- name: Create a policy with users, groups, and multiple accesses
  cloud.runtime.ranger_policy:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "atlas-policy"
    service: "cm_atlas"
    resources:
      entity-type:
        values:
          - "hive_table"
    access_policies:
      - accesses:
          - type: "type-create"
            isAllowed: true
          - type: "type-read"
            isAllowed: true
        users:
          - "admin"
          - "impala"
          - "flink"
          - "zookeeper"
        groups:
          - "public"
        roles: []
        conditions: []

- name: Add a user to existing policy using merge mode
  cloud.runtime.ranger_policy:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "all - database, table"
    service: "cm_kudu"
    merged: true
    access_policies:
      - users:
          - "kafka"
        accesses:
          - type: "select"
            isAllowed: true

- name: Delete a Ranger policy
  cloud.runtime.ranger_policy:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    name: "Test Policy 6"
    service: "cm_hdfs"
    state: "absent"
"""

RETURN = r"""
---
policy:
  description:
    - A dictionary containing details about the policy.
  type: dict
  elements: complex
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

from typing import Any, Dict, Optional

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
    diff_dict,
    to_dict,
    NULLABLE,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyClient,
    merge_policies,
    is_policy_subset,
    build_policy_from_params,
    extract_policy_params,
)


class RangerPolicyModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                **RangerPolicy.argument_spec(),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
                merged=dict(
                    type="bool",
                    default=False,
                ),
            ),
            required_if=[
                ("state", "present", ["name", "service"]),
            ],
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")
        self.service = self.get_param("service")
        self.state = self.get_param("state")
        self.merged = self.get_param("merged")
        self.service_type = self.get_param("service_type")
        self.description = self.get_param("description")
        self.policy_type = self.get_param("policy_type")
        self.policy_priority = self.get_param("policy_priority")
        self.is_enabled = self.get_param("is_enabled")
        self.is_audit_enabled = self.get_param("is_audit_enabled")
        self.is_deny_all_else = self.get_param("deny_all")
        self.zone_name = self.get_param("zone_name")
        self.resources = self.get_param("resources")
        self.additional_resources = self.get_param("additional_resources")
        self.conditions = self.get_param("conditions")
        self.policy_items = self.get_param("policy_items")
        self.deny_policy_items = self.get_param("deny_policy_items")
        self.allow_exceptions = self.get_param("allow_exceptions")
        self.deny_exceptions = self.get_param("deny_exceptions")
        self.data_mask_policy_items = self.get_param("data_mask_policy_items")
        self.row_filter_policy_items = self.get_param("row_filter_policy_items")
        self.validity_schedules = self.get_param("validity_schedules")
        self.policy_labels = self.get_param("policy_labels")
        self.options = self.get_param("options")

        # Initialize result variables
        self.changed = False
        self.diff = {}
        self.policy: Optional[RangerPolicy] = None

    def process(self) -> None:
        client = RangerPolicyClient(self.api_client)

        existing: Optional[RangerPolicy] = None

        if self.name and self.service:
            existing = client.get_policy_by_name(
                service_name=self.service,
                policy_name=self.name,
            )

        if self.state == "absent":
            if existing:
                self.changed = True

                if self.module._diff:
                    before_dict, after_dict = diff_dict(
                        existing,
                        RangerPolicy(name="", service=""),
                    )
                    self.diff = {"before": before_dict, "after": {}}

                if not self.module.check_mode:
                    client.delete_policy_by_id(existing.id)

        elif self.state == "present":
            if not existing:
                incoming = build_policy_from_params(
                    extract_policy_params(self),
                    none_as_nullable=True,
                )

                self.changed = True

                if self.module._diff:
                    before_dict, after_dict = diff_dict(
                        RangerPolicy(name="", service=""),
                        incoming,
                        filter_nullable=False,
                    )
                    self.diff = {"before": {}, "after": after_dict}

                if not self.module.check_mode:
                    self.policy = client.create_policy(incoming)
                else:
                    self.policy = incoming

            else:
                if self.merged:
                    # Build a partial policy with only user-provided (non-None) fields
                    partial_policy = build_policy_from_params(
                        extract_policy_params(self),
                        none_as_nullable=True,
                    )

                    # Check if the partial policy is already a subset of existing
                    partial_dict = to_dict(partial_policy)
                    existing_dict = to_dict(existing)

                    if is_policy_subset(partial_dict, existing_dict):
                        self.changed = False
                        self.policy = existing
                    else:
                        # Merge the policies
                        self.changed = True
                        incoming = merge_policies(existing, partial_policy)

                        # Preserve read-only fields
                        incoming.id = existing.id
                        incoming.guid = existing.guid
                        incoming.version = existing.version
                        incoming.resource_signature = existing.resource_signature

                        if self.module._diff:
                            prev_config, next_config = diff_dict(existing, incoming)
                            self.diff = {
                                "before": prev_config,
                                "after": next_config,
                            }

                        if not self.module.check_mode:
                            self.policy = client.update_policy(incoming)
                        else:
                            self.policy = incoming
                else:
                    incoming = build_policy_from_params(
                        extract_policy_params(self),
                        existing=existing,
                        none_as_nullable=False,
                    )

                    prev_config, next_config = diff_dict(existing, incoming)

                    if prev_config or next_config:
                        self.changed = True

                        if self.module._diff:
                            self.diff = {
                                "before": prev_config,
                                "after": next_config,
                            }

                        if not self.module.check_mode:
                            self.policy = client.update_policy(incoming)
                        else:
                            self.policy = incoming
                    else:
                        self.policy = existing

        else:
            self.module.fail_json(msg=f"Invalid state '{self.state}'.")


def main():
    result = RangerPolicyModule()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        policy=to_dict(result.policy) if result.policy else {},
    )

    if result.module._diff:
        output.update(diff=result.diff)

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

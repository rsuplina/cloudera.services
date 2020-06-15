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
from ansible.module_utils.common.dict_transformations import (
    camel_dict_to_snake_dict,
    recursive_diff,
)
from apache_ranger.model.ranger_service import RangerService
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.ranger_utils import (
    populate_service_payload,
    populate_policy_payload,
    clean_dict,
)


DOCUMENTATION = r"""
module: ranger
short_description: Manage Apache Ranger services and policies.
description:
  - This module manages services and their associated policies in Apache Ranger.
  - It replaces existing services entirely when changes are detected.
  - It does not perform partial merges of services configfs or audit filters.
  - If it does not exist and state is C(present), service will be created.
  - If it exists and state is C(absent), service will be deleted.
author:
  - "Ronald Suplina (@rsuplina)"
  - "Andre Araujo (@asdaraujo)"
version_added: "1.0.0"
requirements:
  - apache-ranger
options:
  state:
    description:
      - Whether the service and policies should be present or absent.
    type: str
    choices: ["present", "absent"]
    default: present
  services:
    description:
      - List of services to manage in Apache Ranger.
    required: true
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - The name of the Ranger service.
        required: true
        type: str
      type:
        description:
          - The type of the service (e.g., hive, hdfs, etc.).
        required: false
        type: str
      enabled:
        description:
          - Whether the service is enabled.
        type: bool
        default: true
        aliases:
          - is_enabled
      display_name:
        description:
          - A human-readable name for the service.
        type: str
        required: false
      description:
        description:
          - A description of the service.
        type: str
      tag_service:
        description:
          - The name of the tag-based service linked to this service.
        type: str
        required: false
      configs:
        description:
          - A dictionary of configuration options for the service.
        type: dict
        required: false
      policies:
        description:
          - A list of policies to apply to this service.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - The name of the policy.
            required: true
            type: str
          enabled:
            description:
              - Whether the policy is enabled.
            type: bool
            default: true
            aliases:
              - is_enabled
          resources:
            description:
              - Resources that the policy applies to.
            type: dict
          policy_type:
            description:
              - Integer representing the type of policy.
            type: int
          policy_priority:
            description:
              - Integer defining policy priority.
            type: int
          description:
            description:
              - A description of the policy.
            type: str
          resource_signature:
            description:
              - Signature for resource definition.
            type: str
            aliases:
              - signature
          enable_audit:
            description:
              - Whether audit logging is enabled for this policy.
            type: bool
            default: true
            aliases:
              - is_audit_enabled
          additional_resources:
            description:
              - A list of additional resources for the policy.
            type: list
            elements: dict
          access_policies:
            description:
              - Access policies (allow rules).
            type: list
            elements: dict
            aliases:
              - policy_items
          deny_policies:
            description:
              - Deny rules.
            type: list
            elements: dict
            aliases:
              - deny_policy_items
          allow_exceptions:
            description:
              - Exceptions to allow rules.
            type: list
            elements: dict
          deny_exceptions:
            description:
              - Exceptions to deny rules.
            type: list
            elements: dict
          data_mask_policies:
            description:
              - Data mask policies for sensitive data.
            type: list
            elements: dict
            aliases:
              - data_mask_policy_items
          row_filter_policies:
            description:
              - Row-level filtering policies.
            type: list
            elements: dict
            aliases:
              - row_filter_policy_items
          service_type:
            description:
              - Type of service the policy belongs to (may override service type).
            type: str
          options:
            description:
              - A dictionary of additional policy options.
            type: dict
          validity_schedules:
            description:
              - A list of time-based validity conditions for the policy.
            type: list
            elements: dict
          policy_labels:
            description:
              - Labels associated with the policy.
            type: list
            elements: str
          zone_name:
            description:
              - The name of the security zone the policy belongs to.
            type: str
          conditions:
            description:
              - List of custom conditions for this policy.
            type: list
            elements: dict
          deny_all_else:
            description:
              - Whether to deny all requests not explicitly allowed.
            type: bool
            default: false
            aliases:
              - is_deny_all_else
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
- name: Create a new Hive Ranger service with 1 policy
  cloudera.services.ranger:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    state: present
    services:
      - name: hive_service_1
        type: hive
        displayName: "Hive Service 1"
        description: "Hive service with 1 policy"
        configs:
          username: "hive"
          password: "hive"
          jdbc.driverClassName: "org.apache.hive.jdbc.HiveDriver"
          jdbc.url: "jdbc:hive2://ranger-hadoop:10000"
          hadoop.security.authorization: true
        policies:
          - name: "policy_one"
            policyType: 0
            policyPriority: 1
            isAuditEnabled: true
            resources:
              database:
                values: ["db1"]
                isExcludes: false
                isRecursive: false
              table:
                values: ["tbl1"]
                isExcludes: false
                isRecursive: false
              column:
                values: ["*"]
                isExcludes: false
                isRecursive: false
            policyItems:
              - users: ["admin"]
                accesses: [{ type: "select" }]
                groups: ["hadoop"]
                delegateAdmin: true

- name: Create a new Hive Ranger service with 2 policies
  cloudera.services.ranger:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    state: present
    services:
      - name: custom_hive_service
        type: hive
        displayName: "Hive Service 2"
        description: "Hive service with 2 policies"
        configs:
          username: "hive"
          password: "hive"
          jdbc.driverClassName: "org.apache.hive.jdbc.HiveDriver"
          jdbc.url: "jdbc:hive2://ranger-hadoop:10000"
          hadoop.security.authorization: true
        policies:
          - name: "policy_read"
            policyType: 0
            isAuditEnabled: true
            resources:
              database:
                values: ["db2"]
                isExcludes: false
                isRecursive: false
              table:
                values: ["tbl2"]
                isExcludes: false
                isRecursive: false
              column:
                values: ["*"]
                isExcludes: false
                isRecursive: false
            policyItems:
              - users: ["data_reader"]
                accesses: [{ type: "select" }]
                delegateAdmin: false
          - name: "policy_write"
            policyType: 0
            isAuditEnabled: true
            resources:
              database:
                values: ["db2"]
                isExcludes: false
                isRecursive: false
              table:
                values: ["tbl2"]
                isExcludes: false
                isRecursive: false
              column:
                values: ["*"]
                isExcludes: false
                isRecursive: false
            policyItems:
              - users: ["data_writer"]
                accesses: [{ type: "update" }]
                delegateAdmin: false

- name: Create 2 Hive Ranger servics
  cloudera.services.ranger:
    endpoint: "https://ranger.example.com"
    username: "admin"
    password: "changeme"
    state: present
    services:
      - name: first_custom_hive_service
        type: hive
        displayName: "Hive Service"
        configs:
          username: "hive"
          password: "hive"
          jdbc.driverClassName: "org.apache.hive.jdbc.HiveDriver"
          jdbc.url: "jdbc:hive2://ranger-hadoop:10000"
          hadoop.security.authorization: true
      - name: second_custom_hive_service
        type: hive
        displayName: "Hive Service 2"
        configs:
          username: "hive"
          password: "hive"
          jdbc.driverClassName: "org.apache.hive.jdbc.HiveDriver"
          jdbc.url: "jdbc:hive2://ranger-hadoop:10000"
          hadoop.security.authorization: true
"""

RETURN = r"""
---
services:
  description:
    - A list of dictionaries containing details about each processed service.
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
    tag_version:
      description:
        - Version number of the tag policy for the service.
      type: int
    tag_update_time:
      description:
        - Timestamp of the last tag policy update (epoch millis).
      type: int
    policy_update_time:
      description:
        - Timestamp of the last policy update (epoch millis).
      type: int
      returned: always
"""


class Ranger(RangerMutableModule):
    def __init__(self, module):
        super(Ranger, self).__init__(module)

        # Set parameters

        self.services = self.get_param("services")
        self.state = self.get_param("state")

        # Initialize the return values
        self.changed = False
        self.diff = dict(before=[], after=[])

        self.output = []

        # Execute logic process
        self.process()

    def process(self):
        for service in self.services:
            try:
                incoming_service = populate_service_payload(RangerService(service))
                existing_service = self.ranger.get_service(serviceName=service["name"])

                if self.state == "present":
                    if existing_service:

                        if before_diff or after_diff:
                            self.changed = True
                            if not self.module.check_mode:
                                self.ranger.update_service(
                                    serviceName=service["name"],
                                    service=incoming_service,
                                )
                    else:
                        self.changed = True
                        if not self.module.check_mode:
                            self.output.append(
                                self.ranger.create_service(service=incoming_service),
                            )
                    if service["policies"]:
                        for policy in service["policies"]:
                            policy["service"] = service["name"]

                            incoming_policy = clean_dict(policy)
                            existing_policy = self.ranger.get_policy(
                                serviceName=policy["service"],
                                policyName=policy["name"],
                            )

                            if existing_policy:
                                existing_policy = clean_dict(existing_policy)

                                if self.module._diff:
                                    before_diff, after_diff = recursive_diff(
                                        existing_policy,
                                        incoming_policy,
                                    )
                                    self.diff["before"].append(before_diff)
                                    self.diff["after"].append(after_diff)

                                if before_diff or after_diff:
                                    self.changed = True
                                    if not self.module.check_mode:
                                        self.ranger.update_policy(
                                            serviceName=policy["service"],
                                            policyName=policy["name"],
                                            policy=incoming_policy,
                                        )
                            else:
                                self.changed = True
                                if not self.module.check_mode:
                                    self.ranger.create_policy(policy=incoming_policy)

                elif self.state == "absent" and existing_service:
                    self.changed = True
                    if self.module._diff:
                        self.diff = dict(before=existing_service, after=dict())
                    if not self.module.check_mode:
                        self.output.append(
                            self.ranger.delete_service(serviceName=service["name"]),
                        )
                print(self.output)
            except Exception as e:
                self.module.fail_json(
                    msg=f"Error processing service {service['name']}: {str(e)}",
                )


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type="str"),
            username=dict(required=True, type="str"),
            password=dict(required=True, type="str", no_log=True),
            verify_tls=dict(required=False, type="bool", default=True),
            ssl_ca_cert=dict(required=False, type="str"),
            state=dict(default="present", choices=["present", "absent"]),
            services=dict(
                required=True,
                type="list",
                elements="dict",
                options=dict(
                    name=dict(required=True, type="str"),
                    type=dict(required=False, type="str"),
                    enabled=dict(
                        required=False,
                        type="bool",
                        default=True,
                        aliases=["is_enabled"],
                    ),
                    display_name=dict(required=False, type="str"),
                    description=dict(required=False, type="str"),
                    tag_service=dict(required=False, type="str"),
                    configs=dict(required=False, type="dict"),
                    policies=dict(
                        required=False,
                        type="list",
                        elements="dict",
                        options=dict(
                            name=dict(required=True, type="str"),
                            enabled=dict(
                                required=False,
                                type="bool",
                                default=True,
                                aliases=["is_enabled"],
                            ),
                            resources=dict(required=False, type="dict"),
                            policy_type=dict(required=False, type="int"),
                            policy_priority=dict(required=False, type="int"),
                            description=dict(required=False, type="str"),
                            resource_signature=dict(
                                required=False,
                                type="str",
                                aliases=["signature"],
                            ),
                            enable_audit=dict(
                                required=False,
                                type="bool",
                                default=True,
                                aliases=["is_audit_enabled"],
                            ),
                            additional_resources=dict(
                                required=False,
                                type="list",
                                elements="dict",
                            ),
                            access_policies=dict(
                                required=False,
                                type="list",
                                elements="dict",
                                aliases=["policy_items"],
                            ),
                            deny_policies=dict(
                                required=False,
                                type="list",
                                elements="dict",
                                aliases=["deny_policy_items"],
                            ),
                            allow_exceptions=dict(
                                required=False,
                                type="list",
                                elements="dict",
                            ),
                            deny_exceptions=dict(
                                required=False,
                                type="list",
                                elements="dict",
                            ),
                            data_mask_policies=dict(
                                required=False,
                                type="list",
                                elements="dict",
                                aliases=["data_mask_policy_items"],
                            ),
                            row_filter_policies=dict(
                                required=False,
                                type="list",
                                elements="dict",
                                aliases=["row_filter_policy_items"],
                            ),
                            service_type=dict(required=False, type="str"),
                            options=dict(required=False, type="dict"),
                            validity_schedules=dict(
                                required=False,
                                type="list",
                                elements="dict",
                            ),
                            policy_labels=dict(
                                required=False,
                                type="list",
                                elements="str",
                            ),
                            zone_name=dict(required=False, type="str"),
                            conditions=dict(
                                required=False,
                                type="list",
                                elements="dict",
                            ),
                            deny_all_else=dict(
                                required=False,
                                type="bool",
                                default=False,
                                aliases=["is_deny_all_else"],
                            ),
                        ),
                    ),
                ),
            ),
        ),
        supports_check_mode=True,
    )

    result = Ranger(module)

    output = dict(
        changed=result.changed,
        services=result.output,
    )
    if module._diff:
        output.update(diff=result.diff)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

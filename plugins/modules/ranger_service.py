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
module: ranger_service
short_description: Manage services in Apache Ranger
description:
  - Create, update, or delete services in Apache Ranger.
author:
  - "Ronald Suplina (@rsuplina)"
version_added: "1.1.0"
options:
  name:
    description:
      - Name of the Ranger service.
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
  is_enabled:
    description:
      - Whether the service is enabled.
    type: bool
    default: true
    aliases:
      - enabled
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
      - Configuration property names are sent to Ranger verbatim.
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
  - cloudera.services.services_client
attributes:
  check_mode:
    description:
      - This module supports check mode.
    support: full
  diff_mode:
    description:
      - This module supports diff mode.
    support: full
    platforms:
      - all
"""

EXAMPLES = r"""
# NOTE: Examples do not include connection and authentication fields

- name: Create a Ranger service
  cloudera.services.ranger_service:
    name: "test02"
    type: "hdfs"
    configs:
      username: "hdfs"
      password: "hdfs"
      fs.default.name: "hdfs://namenode:8020"
      hadoop.security.authentication: "simple"
      hadoop.security.authorization: "true"

- name: Delete a Ranger service
  cloudera.services.ranger_service:
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

from typing import Any, Dict, Optional

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
    build_from_params,
    diff_dict,
    to_dict,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerService,
    RangerServiceClient,
    extract_service_params,
)


class RangerServiceModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                **RangerService.argument_spec(),
                state=dict(
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
            ),
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")
        self.type = self.get_param("type")
        self.display_name = self.get_param("display_name")
        self.description = self.get_param("description")
        self.tag_service = self.get_param("tag_service")
        self.is_enabled = self.get_param("is_enabled")
        self.configs = self.get_param("configs")
        self.state = self.get_param("state")

        # Initialize result variables
        self.changed = False
        self.diff = {}
        self.service: Optional[RangerService] = None

    def process(self) -> None:
        client = RangerServiceClient(self.api_client)

        existing: Optional[RangerService] = None
        if self.name:
            existing = client.get_service_by_name(self.name)

        if self.state == "absent":
            if existing:
                self.changed = True

                if self.module._diff:
                    self.diff = {"before": to_dict(existing), "after": {}}

                if not self.module.check_mode:
                    client.delete_service_by_id(existing.id)

        elif self.state == "present":
            if not existing:
                incoming = build_from_params(
                    RangerService,
                    extract_service_params(self),
                )

                self.changed = True

                if self.module._diff:
                    self.diff = {"before": {}, "after": to_dict(incoming)}

                if not self.module.check_mode:
                    self.service = client.create_service(incoming)
                else:
                    self.service = incoming

            else:
                incoming = build_from_params(
                    RangerService,
                    extract_service_params(self),
                    existing=existing,
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
                        self.service = client.update_service(incoming)
                    else:
                        self.service = incoming
                else:
                    self.service = existing

        else:
            self.module.fail_json(msg=f"Invalid state '{self.state}'.")


def main():
    result = RangerServiceModule()

    output: Dict[str, Any] = dict(
        changed=result.changed,
        service=to_dict(result.service) if result.service else {},
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

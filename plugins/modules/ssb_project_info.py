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
module: ssb_project_info
short_description: Retrieve information about SSB projects
description:
  - Retrieve information about one or more Cloudera SSB projects.
  - The module can list all projects or filter by name or id.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
options:
  name:
    description:
      - The name of the project to retrieve.
      - This parameter is mutually exclusive with O(id).
    type: str
    required: false
  id:
    description:
      - The unique identifier of the project to retrieve.
      - This parameter is mutually exclusive with O(name).
    type: str
    required: false
    aliases:
      - project_id
extends_documentation_fragment:
  - cloudera.services.services_client
"""

EXAMPLES = r"""
- name: List all SSB projects
  cloudera.services.ssb_project_info:
  register: all_projects

- name: Get information about a specific project by name
  cloudera.services.ssb_project_info:
    name: "my-project"
  register: project_by_name

- name: Get information about a specific project by id
  cloudera.services.ssb_project_info:
    id: "12345"
  register: project_by_id
"""

RETURN = r"""
projects:
    description: List of SSB projects.
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The unique identifier of the project.
            type: int
            returned: when available
        name:
            description: The name of the project.
            type: str
            returned: always
        description:
            description: A description of the project.
            type: str
            returned: when available
        mv_prefix:
            description: The materialized view prefix for the project.
            type: str
            returned: when available
        active_environment:
            description: The ID of the active environment for the project.
            type: int
            returned: when available
        sync_source_config:
            description: Configuration for the project's sync source.
            type: dict
            returned: when available
            contains:
                type:
                    description: The type of sync source.
                    type: str
                    returned: always
                clone_url:
                    description: The URL to clone the sync source repository.
                    type: str
                    returned: always
                branch:
                    description: The branch to sync from the repository.
                    type: str
                    returned: when available
                allow_deletions:
                    description: Whether to allow deletions from the sync source.
                    type: bool
                    returned: when available
                credential:
                    description: Credentials for accessing the sync source.
                    type: dict
                    returned: when available
                    contains:
                        type:
                            description: The type of credential (e.g., password, ssh).
                            type: str
                            returned: always
                        username:
                            description: The username for authentication.
                            type: str
                            returned: when available
                        password:
                            description: The password for authentication.
                            type: str
                            returned: when available
                        ssh_private_key:
                            description: The SSH private key for authentication.
                            type: str
                            returned: when available
                        ssh_public_key:
                            description: The SSH public key for authentication.
                            type: str
                            returned: when available
                        ssh_passphrase:
                            description: The passphrase for the SSH key.
                            type: str
                            returned: when available
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

from typing import Any, Dict, List

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbProject,
    SsbProjectClient,
)


class SsbProjectInfoModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                name=dict(type="str", required=False),
                id=dict(type="str", required=False, aliases=["project_id"]),
            ),
            mutually_exclusive=[["name", "id"]],
            supports_check_mode=True,
        )

        # Set parameters
        self.name = self.get_param("name")
        self.project_id = self.get_param("id")

        # Initialize result variables
        self.project_list: List[SsbProject] = []

    def process(self) -> None:
        client = SsbProjectClient(self.api_client)
        if self.project_id:
            project = client.describe_project(project_id=self.project_id)
            if project:
                self.project_list.append(project)
        else:
            projects = client.list_projects()
            if self.name:
                projects = [p for p in projects if p.name == self.name]
            self.project_list.extend(projects)


def main():
    result = SsbProjectInfoModule()

    output: Dict[str, Any] = dict(
        changed=False,
        projects=[to_dict(project) for project in result.project_list],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

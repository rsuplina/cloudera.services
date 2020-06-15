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

import json

from ansible_collections.cloudera.services.plugins.module_utils.ml import MLModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: ml_project_info
short_description: Get information for Cloudera Machine Learning (CML) projects
description:
  - Get information for one or more Cloudera Machine Learning (CML) projects.
  - The module supports C(check_mode).
  - The module supports the C(v2) API only.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  id:
    description:
      - The identifier of a project to retrieve.
      - Mutually exclusive with C(name).
    type: int
    required: False
    aliases:
      - project_id
  name:
    description:
      - The name of a project to retrieve.
      - Mutually exclusive with C(id).
    type: str
    required: False
    aliases:
      - project_name
extends_documentation_fragment:
  - cloudera.services.ml_endpoint
"""

EXAMPLES = r"""
- name: Get details on all projects
  cloudera.services.ml_project_info:
    endpoint: "{{ cml_endpoint }}"
    api_key: "{{ cml_api_key }}"

- name: Get details on a single project by name
  cloudera.services.ml_project_info:
    endpoint: "{{ cml_endpoint }}"
    api_key: "{{ cml_api_key }}"
    name: Name of the project
"""

RETURN = r"""
---
projects:
  description: List of discovered projects
  returned: always
  type: list
  elements: dict
  contains:
    created_at:
      description: Creation timestamp
      returned: always
      type: str
      sample: "2022-12-05T16:03:05.435018Z"
    creation_status:
      description: Current creation state
      returned: always
      type: str
      sample: "success"
    creator:
      description: Details on the project creator
      returned: always
      type: dict
      contains:
        email:
          description: Email address of the project creator
          returned: when supported
          type: str
        name:
          description: Name of the project creator
          returned: when supported
          type: str
        username:
          description: Username of the project creator
          returned: always
          type: str
    default_engine_type:
      description: Runtime engine
      returned: always
      type: str
      sample: "ml_runtime"
    description:
      description: Description of the project
      returned: always
      type: str
    environment:
      description: Set of environmental variables for the project
      returned: always
      type: dict
    id:
      description: Identifier for the project
      returned: always
      type: str
      sample: "d5tv-auiv-yl59-ncmc"
    name:
      description: Name of the project
      returned: always
      type: str
    owner:
      description: Details on the project owner
      returned: when supported
      type: dict
      contains:
        email:
          description: Email address of the project owner
          returned: when supported
          type: str
        name:
          description: Name of the project owner
          returned: when supported
          type: str
        username:
          description: Username of the project owner
          returned: always
          type: str
    permissions:
      description: Details on project permissions
      returned: always
      type: dict
      contains:
        admin:
          description: Administrative access
          returned: always
          type: bool
        business_user:
          description: Business User access
          returned: always
          type: bool
        operator:
          description: Operator access
          returned: always
          type: bool
        read:
          description: Read access
          returned: always
          type: bool
        write:
          description: Write access
          returned: always
          type: bool
    shared_memory_limit:
      description: Shared memory limit for the project
      returned: when supported
      type: int
    updated_at:
      description: Update timestamp
      returned: when supported
      type: str
      sample: "2022-12-05T17:40:34.154573Z"
    visibility:
      description: Privacy flag for the project
      returned: always
      type: str
      sample: "private"
sdk_out:
  description: Returns the captured CML SDK log.
  returned: when supported
  type: str
sdk_out_lines:
  description: Returns a list of each line of the captured CML SDK log.
  returned: when supported
  type: list
  elements: str
"""


class MLProjectInfo(MLModule):
    def __init__(self, module):
        super(MLProjectInfo, self).__init__(module)

        # Set parameters
        self.public = self._get_param("public")
        self.user = self._get_param("user")
        self.name = self._get_param("name")
        self.id = self._get_param("id")

        # Initialize the return values
        self.projects = []

        # Execute logic process
        self.process()

    @MLModule.process_debug
    def process(self):
        if self.id:
            existing = self.get_project(self.id)
            self.projects = [existing]
            return

        query_params = dict(include_public_projects=self.public)

        search_filter = dict()
        if self.user:
            search_filter["creator.username"] = self.user
        if self.name:
            search_filter["name"] = self.name

        if search_filter:
            query_params["search_filter"] = json.dumps(
                search_filter,
                separators=(",", ":"),
            )

        self.projects = self.query(
            method="GET",
            api=["projects"],
            field="projects",
            params=query_params,
        )


def main():
    module = MLModule.ansible_module(
        # TODO Expand to creator and owner
        argument_spec=dict(
            public=dict(
                required=False,
                type=bool,
                default=True,
                aliases=["include_public_projects"],
            ),
            user=dict(
                required=False,
                type="str",
                aliases=["username", "creator_username"],
            ),
            name=dict(required=False, type="str", aliases=["project"]),
            id=dict(required=False, type="str", aliases=["project_id"]),
        ),
        mutually_exclusive=[
            ["name", "id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectInfo(module)

    output = dict(
        changed=result.changed,
        projects=result.projects,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

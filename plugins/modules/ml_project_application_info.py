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

from ansible_collections.cloudera.services.plugins.module_utils.ml import (
    MLModule,
    validate_project_id,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: ml_project_application_info
short_description: Get information for Cloudera Machine Learning (CML) project applications
description:
  - Get information for the available Cloudera Machine Learning (CML) project applications.
  - The module supports C(check_mode).
  - The module supports the C(v2) API only.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  project_name:
    description:
      - Full name of the Project within the CML Workspace.
      - Mutually exclusive with I(project_id).
    type: str
    required: True
  project_id:
    description:
      - Identifier of the Project within the CML Workspace.
      - Mutually exclusive with I(project_name).
    type: str
    required: True
  id:
    description:
      - Identifier of the Application.
    type: str
    aliases:
      - application_id
  auth:
    description:
      - Flag to toggle L(restricted access,https://docs.cloudera.com/machine-learning/cloud/applications/topics/ml-securing-applications.html) to the Application.
    type: bool
    default: True
    aliases:
      - auth_enabled
  creator:
    description:
      - Creator of the Application within the Project.
    type: dict
    suboptions:
      name:
        description:
          - Name of the creator of the Application.
        type: str
      username:
        description:
          - Username of the creator of the Application.
        type: str
      email:
        description:
          - Email address of the creator of the Application.
  name:
    description:
      - Name of the Application.
    type: str
  kernel:
    description:
      - Name of the kernel enabled for the Application.
    type: str
  subdomain:
    description:
      - DNS subdomain for the Application.
    type: str
  desc:
    description:
      - Description of the Application.
    type: str
    aliases:
      - description
  script:
    description:
      - Name of the entrypoint script executed within the kernel of the Application.
    type: str
  status:
    description:
      - Runtime state of the Application.
    type: str
    choices:
      - running
      - stopping
      - stopped
      - starting
      - failed
extends_documentation_fragment:
  - cloudera.services.ml_endpoint
"""

EXAMPLES = r"""
- name: Get all Applications within the Project
  cloudera.services.ml_project_application_info:
    project_name: Example Project

- name: Get all Applications within the Project created by 'jdoe'
  cloudera.services.ml_project_application_info:
    project_name: Example Project
    creator:
      username: jdoe

- name: Get all Applications within the Project that are stopped
  cloudera.services.ml_project_application_info:
    project_name: Example Project
    status: stopped

- name: Get all Applications within the Project that are public
  cloudera.services.ml_project_application_info:
    project_name: Example Project
    auth_enabled: no
"""

RETURN = r"""
---
applications:
  description: Returns all Applications based on selection criteria.
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description:
        - Identifier of the Application.
      returned: always
      type: str
    name:
      description:
        - Name of the Application.
      returned: always
      type: str
    description:
      description:
        - Description of the Application.
      returned: always
      type: str
    creator:
      description:
        - Details on the creator of the Application.
      returned: always
      type: dict
      contains:
        username:
          description:
            - Username of the Application creator.
          returned: always
          type: str
        name:
          description:
            - Name of the Application creator.
          returned: always
          type: str
        email:
          description:
            - Email address of the Application creator
    script:
      description:
        - Entrypoint script for the Application executed by the kernel.
      returned: always
      type: str
    subdomain:
      description:
        - DNS subdomain of the Application.
      returned: always
      type: str
    status:
      description:
        - Current state of the Application.
      returned: always
      type: str
    created_at:
      description:
        - Creation timestamp of the Application.
      returned: always
      type: str
      sample:
        - "2022-07-11T21:03:13.809Z"
    stopped_at:
      description:
        - Last stopped timestamp of the Application.
      returned: when supported
      type: str
      sample:
        - "2022-07-11T21:03:13.809Z"
    updated_at:
      description:
        - Last updated timestamp of the Application.
      returned: when supported
      type: str
      sample:
        - "2022-07-11T21:03:13.809Z"
    starting_at:
      description:
        - Last started timestamp of the Application.
      returned: when supported
      type: str
      sample:
        - "2022-07-11T21:03:13.809Z"
    running_at:
      description:
        - Last running timestamp of the Application.
      returned: when supported
      type: str
      sample:
        - "2022-07-11T21:03:13.809Z"
    kernel:
      description:
        - Name of the kernel for the Application
      returned: always
      type: str
    cpu:
      description:
        - Allocated vCPU for the Application.
      returned: always
      type: float
    memory:
      description:
        - Allocated RAM for the Application.
      returned: always
      type: float
    nvidia_gpu:
      description:
        - Allocated Nvidia GPUs for the Application.
      returned: always
      type: int
    bypass_authentication:
      description:
        - Flag indicating if Application access is restricted or public.
      returned: always
      type: bool
    environment:
      description:
        - Environment variables defined for the Application.
      returned: always
      type: json
    runtime_identifier:
      description:
        - Identifier of the Runtime defined for the Application.
      returned: always
      type: str
sdk_out:
    description: Returns the captured SDK log.
    returned: when supported
    type: str
sdk_out_lines:
    description: Returns a list of each line of the captured SDK log.
    returned: when supported
    type: list
    elements: str
"""


class MLProjectApplicationInfo(MLModule):
    def __init__(self, module):
        super(MLProjectApplicationInfo, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.id = self._get_param("id")
        self.auth = self._get_param("auth")
        self.creator_email = self._get_param("creator", "email")
        self.creator_name = self._get_param("creator", "name")
        self.creator_username = self._get_param("creator", "username")
        self.name = self._get_param("name")
        self.kernel = self._get_param("kernel")
        self.subdomain = self._get_param("subdomain")
        self.desc = self._get_param("desc")
        self.script = self._get_param("script")
        self.status = self._get_param("status")

        # Initialize the return values
        self.applications = []

        # Execute logic process
        self.process()

    @MLModule.process_debug
    def process(self):
        if self.project_id:
            if not validate_project_id(self.project_id):
                self.module.fail_json(msg="Invalid Project ID: " + self.project_id)
            project = self.get_project(self.project_id)
        else:
            project = self.find_project(self.project_name)

        if not project:
            self.module.fail_json(msg="Project not found")

        if self.id:
            self.applications = [self.get_application(project["id"], self.id)]
        else:
            search_filter = dict()
            if self.creator_email:
                search_filter["creator.email"] = self.creator_email
            if self.creator_name:
                search_filter["creator.name"] = self.creator_name
            if self.creator_username:
                search_filter["creator.username"] = self.creator_username
            if self.name:
                search_filter["name"] = self.name
            if self.kernel:
                search_filter["kernel"] = self.kernel
            if self.auth is not None:
                search_filter["bypass_authentication"] = not self.auth  # Note negation
            if self.desc:
                search_filter["description"] = self.desc
            if self.subdomain:
                search_filter["subdomain"] = self.subdomain
            if self.script:
                search_filter["script"] = self.script
            if self.status:
                search_filter["status"] = self.status

            query = dict(
                method="GET",
                api=["projects", project["id"], "applications"],
                field="applications",
            )

            if search_filter:
                query.update(
                    params=dict(
                        search_filter=json.dumps(search_filter, separators=(",", ":")),
                    ),
                )

            self.applications = self.query(**query)


def main():
    module = MLProjectApplicationInfo.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            id=dict(required=False, type="str", aliases=["application_id"]),
            auth=dict(required=False, type="bool", aliases=["auth_enabled"]),
            creator=dict(
                required=False,
                type="dict",
                options=dict(
                    name=dict(required=False, type="str"),
                    username=dict(required=False, type="str"),
                    email=dict(required=False, type="str"),
                ),
            ),
            name=dict(required=False, type="str"),
            kernel=dict(required=False, type="str"),
            subdomain=dict(required=False, type="str"),
            desc=dict(required=False, type="str", aliases=["description"]),
            script=dict(required=False, type="str"),
            status=dict(
                required=False,
                type="str",
                choices=[
                    "running",
                    "stopping",
                    "stopped",
                    "starting",
                    "failed",
                ],
            ),
        ),
        required_one_of=[
            ["project_name", "project_id"],
        ],
        mutually_exclusive=[
            ["project_name", "project_id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectApplicationInfo(module)

    output = dict(
        changed=False,
        applications=result.applications,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

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

from ansible_collections.cloudera.services.plugins.module_utils.ml_v1 import (
    MLModuleV1,
    Squelch,
    kebab,
)


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: ml_project_dataviz_info
short_description: Get information for a Cloudera Machine Learning (CML) Data Visualization application.
description:
  - Get information for a Cloudera Machine Learning (CML) Data Visualization application.
  - The module supports check_mode.
  - The module supports the deprecated C(v1) API.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  user:
    description:
      - The username of the project containing the DataViz application.
    type: str
    required: True
    aliases:
      - username
  project:
    description:
      - The name of the project containing the DataViz application.
    type: str
    required: True
    aliases:
      - project_name
extends_documentation_fragment:
  - cloudera.services.ml_endpoint_v1
"""

EXAMPLES = r"""
- name: Get the details for a project's DataViz application
  cloudera.services.ml_project_dataviz_info:
    endpoint: https://endpoint.example
    api_key: ANAPIKEY
    user: jdoe
    project: The Project
  register: dataviz_info
"""

RETURN = r"""
---
application:
  description: Returns the details of the DataViz application.
  returned: always
  type: dict
  contains:
    bypass_authentication:
      description: Flag indicating if user authentication is required for access.
      returned: always
      type: bool
    cdvApp:
      description: Flag indicating if this application is a DataViz application.
      returned: always
      type: bool
    createdAt:
      description: Creation timestamp
      returned: always
      type: str
      sample: "2022-11-30T20:57:17.389Z"
    creator:
      description: Details on the application's creator.
      returned: always
      type: dict
      contains:
        name:
          description: The name of the creator.
          returned: always
          type: str
        username:
          description: The username of the creator.
          returned: always
          type: str
    creatorHtmlUrl:
      description: URL to the creator's profile page within the project.
      returned: always
      type: str
    currentDashboard:
      description: Details regarding the current dashboard configuration.
      returned: when supported
      type: dict
      contains:
        cpu:
          description: The allocated vCPU for the dashboard.
          returned: when supported
          type: float
        creator:
          description: Details on the dashboard's creator.
          returned: when supported
          type: dict
          contains:
            username:
              description: The username of the dashboard creator.
              returned: when supported
              type: str
        creatorHtmlUrl:
          description: URL to the dashboard creator's profile page.
          returned: when supported
          type: str
        exitCode:
          description: Exit code
          returned: when supported
          type: str
        kernel:
          description: Kernel
          returned: when supported
          type: str
        memory:
          description: The allocated RAM
          returned: when supported
          type: int
        name:
          description: Name of the dashboard
          returned: when supported
          type: str
        nvidiaGpu:
          description: The allocated Nvidia GPU
          returned: when supported
          type: int
        runtime:
          description: Details about the dashboard's runtime
          returned: when supported
          type: dict
          contains:
            description:
              description: Description of the runtime
              returned: when supported
              type: str
            edition:
              description: The edition of the runtime
              returned: when supported
              type: str
            editor:
              description: The name of the editor
              returned: when supported
              type: str
            fullVersion:
              description: The version of the runtime
              returned: when supported
              type: str
              sample: "6.4.1-b7.1"
            gbn:
              description: GBN number
              returned: when supported
              type: int
            gitHash:
              description: Git hash
              returned: when supported
              type: str
            id:
              description: Identity of the runtime
              returned: when supported
              type: int
            imageIdentifier:
              description: Image identifier of the runtime
              returned: when supported
              type: str
              sample: "docker.repository.cloudera.com/cloudera/cdv/runtimedataviz:6.4.1-b7"
            kernel:
              description: Name of the runtime kernel
              returned: when supported
              type: str
            maintenanceVersion:
              description: Maintenance version
              returned: when supported
              type: int
            runtimeMetadataVersion:
              description: Metadata version
              returned: when supported
              type: int
            shortVersion:
              description: The short version of the runtime
              returned: when supported
              type: str
              sample: "6.4.1-b7"
            status:
              description: Dashboard status
              returned: when supported
              type: str
              sample: "ENABLED"
        startingAt:
          description: Starting timestamp of the dashboard
          returned: when supported
          type: str
          sample: "2022-11-30T20:57:58.592Z"
        statusName:
          description: Status label for the dashboard state
          returned: when supported
          type: str
          sample: "running"
    currentDashboardId:
      description: Identifier of the dashboard
      returned: always
      type: str
      sample: "sy4ky46ip8y81kyq"
    description:
      description: The description of the dashboard
      returned: always
      type: str
    engineDiff:
      description: Engine diff
      returned: when supported
      type: bool
    environment:
      description: Set of environment variables set for the dashboard
      returned: when supported
      type: dict
    id:
      description: Dashboard application identifier
      returned: always
      type: int
    name:
      description: Name of the dashboard application
      returned: always
      type: str
    permissions:
      description: Access and process permissions for the dashboard application
      returned: always
      type: dict
      contains:
        delete:
          description: Flag for delete access
          returned: always
          type: bool
        restart:
          description: Flag for restart access
          returned: always
          type: bool
        stop:
          description: Flag for stop access
          returned: always
          type: bool
        update:
          description: Flag for update access
          returned: always
          type: bool
    project:
      description: Details about the enclosing CML project of the dashboard application
      returned: always
      type: dict
      contains:
        createdAt:
          description: Project creation timestamp
          returned: always
          type: str
          sample: "2022-11-30T20:57:05.467Z"
        creator:
          description: Details on the project creator
          returned: always
          type: dict
          contains:
            name:
              description: The name of the project creator
              returned: always
              type: str
            username:
              description: The username of the project creator
              returned: always
              type: str
        description:
          description: Project description
          returned: when supported
          type: str
        name:
          description: Project name
          returned: always
          type: str
        owner:
          description: Details on the project owner
          returned: when supported
          type: dict
          contains:
            name:
              description: The name of the project owner
              returned: always
              type: str
            username:
              description: The username of the project owner
              returned: always
              type: str
        slug:
          description: Prefixed, URL-encoded name of the project
          returned: always
          type: str
          sample: "username/project-name"
        slug_raw:
          description: URL-encoded name of the project
          returned: always
          type: str
          sample: "project-name"
        updatedAt:
          description: Project update timestamp
          returned: when supported
          type: str
          sample: "2022-11-30T21:30:54.717Z"
    projectHtmlUrl:
      description: URL to the project
      returned: always
      type: str
    projectId:
      description: Project identifier
      returned: always
      type: int
    script:
      description: Entrypoint script for the DataViz application
      returned: always
      type: str
      sample: "/opt/vizapps/tools/arcviz/startup_app.py"
    status:
      description: State of the DataViz application
      returned: always
      type: str
      sample: "running"
    stoppedAt:
      description: DataViz application stop timestamp
      returned: when supported
      type: str
      sample: "2022-11-30T21:30:54.717Z"
    subdomain:
      description: Subdomain for the DataViz application
      returned: always
      type: str
      sample: "embedviz-8"
    updatedAt:
      description: DataViz application update timestamp
      returned: when supported
      type: str
      sample: "2022-11-30T20:59:20.063Z"
    url:
      description: URL to the DataViz application
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


class MLProjectDataVizInfo(MLModuleV1):
    def __init__(self, module):
        super(MLProjectDataVizInfo, self).__init__(module)

        # Set parameters
        self.user = self._get_param("user")
        self.project = self._get_param("project")

        # Initialize the return value
        self.application = {}

        # Execute logic process
        self.process()

    @MLModuleV1.process_debug
    def process(self):
        query = dict(
            method="GET",
            api=["projects", self.user, kebab(self.project), "applications"],
        )

        existing_apps = self.query(**query, squelch=[Squelch(403, [])])

        if existing_apps:
            self.application = next(
                filter(lambda app: app["cdvApp"] is True, existing_apps),
                {},
            )


def main():
    module = MLModuleV1.ansible_module(
        argument_spec=dict(
            user=dict(required=True, type="str", aliases=["username"]),
            project=dict(required=True, type="str", aliases=["project_name"]),
        ),
        supports_check_mode=True,
    )

    result = MLProjectDataVizInfo(module)

    output = dict(
        changed=False,
        application=result.application,
    )

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

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
    difference,
    validate_project_id,
    validate_subdomain,
)


DOCUMENTATION = r"""
module: ml_project_application
short_description: Create, update, and delete a Cloudera Machine Learning (CML) project application.
description:
  - Create, update, and delete a Cloudera Machine Learning (CML) project application.
  - The module supports check_mode.
  - The module supports the C(v2) API only.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  project_name:
    description:
      - The enclosing project name for the application.
      - Either C(project_name) or C(project_id) is required.
    type: str
    required: False
  project_id:
    description:
      - The enclosing project ID for the application.
      - Either C(project_name) or C(project_id) is required.
    type: str
    required: False
  name:
    description:
      - The name of the application.
      - Either C(name) or C(id) is required.
    type: str
    required: False
  id:
    description:
      - The ID of the application.
      - Either C(name) or C(id) is required.
    type: str
    aliases:
      - application_id
    required: False
  auth:
    description:
      - Flag indicating if user authentication is required to use the application.
    type: bool
    required: False
    aliases:
      - auth_enabled
  cpu:
    description:
      - The vCPU allocated to the application.
    type: float
    required: False
  creator:
    description:
      - Details for the creator of the application.
    type: dict
    required: False
    suboptions:
      email:
        description:
          - The email address of the application creator.
        type: str
        required: False
      name:
        description:
          - The description for the application creator.
        type: str
        required: False
      username:
        description:
          - The username of the application creator.
        type: str
        required: False
  desc:
    description:
      - The description for the application.
    type: str
    required: False
    aliases:
      - description
  env:
    description:
      - A set of environment variables to set on the application.
    type: dict
    required: False
    aliases:
      - env_vars
  kernel:
    description:
      - The kernel to use for the application.
    type: str
    required: False
    choices:
      - python3
      - python2
      - r
      - scala
  memory:
    description:
      - The RAM allocated to the application, in GB.
    type: float
    required: False
  gpu:
    description:
      - The count of Nvidia GPUs allocated to the application.
    type: int
    required: False
    aliases:
      - nvidia_gpu
  addons:
    description:
      - A list of runtime addon identifiers within the application.
    type: list
    elements: str
    required: False
    aliases:
      - runtime_addons
      - runtime_addon_identifiers
  runtime:
    description:
      - The container runtime identifier for the application.
    type: str
    required: False
    aliases:
      - runtime_image_id
      - runtime_identifier
  script:
    description:
      - Name of the execution script for the application.
    type: str
    required: False
  subdomain:
    description:
      - The subdomain for the application.
    type: str
    required: False
  state:
    description:
      - The state of the application.
    type: str
    required: False
    default: present
    choices:
      - present
      - restarted
      - stopped
      - absent
extends_documentation_fragment:
  - cloudera.services.ml_endpoint
"""

EXAMPLES = r"""
- name: Start application
  cloudera.services.ml_project_application:
    endpoint: "{{ endpoint }}"
    api_key: "{{ api_key }}"
    project_id: "{{ project_id }}"
    name: "My Application"
    auth: True
    script: "runme.py"
    subdomain: "test-example"
    env:
        FOO: bar
    state: present
"""

RETURN = r"""
application:
    description: Returns the application.
    returned: on success
    type: dict
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
                    returned: always
                    type: str
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

# APPLICATION_STARTING, APPLICATION_STOPPED, APPLICATION_RUNNING


class MLProjectApplication(MLModule):
    def __init__(self, module):
        super(MLProjectApplication, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.auth = self._get_param("auth")
        self.cpu = self._get_param("cpu")
        self.creator = self._get_param("creator")
        self.desc = self._get_param("desc")
        self.env = self._get_param("env")
        self.kernel = self._get_param("kernel")
        self.memory = self._get_param("memory")
        self.gpu = self._get_param("gpu")
        self.addons = self._get_param("addons")
        self.runtime = self._get_param("runtime")
        self.script = self._get_param("script")
        self.subdomain = self._get_param("subdomain")
        self.state = self._get_param("state")

        # Initialize the return values
        self.changed = False
        self.application = {}

        # Execute logic process
        self.process()

    @MLModule.process_debug
    def process(self):
        project = None
        if self.project_id:
            if not validate_project_id(self.project_id):
                self.module.fail_json(msg="Invalid Project ID: " + self.id)
            project = self.get_project(self.project_id)
        else:
            project = self.find_project(self.project_name)

        if not project:
            self.module.fail_json(msg="Project not found")

        existing = None
        if self.id:
            existing = self.get_application(project["id"], self.id)
        else:
            existing = self.find_application(project["id"], self.name)

        if self.state in ["present", "restarted", "stopped"]:
            payload = dict()
            # Create or update
            if self.name:
                payload.update(name=self.name)
            if self.auth is not None:
                payload.update(bypass_authentication=not self.auth)  # Note negation
            if self.cpu:
                payload.update(cpu=self.cpu)
            if self.creator:
                payload.update(creator=self.creator)
            if self.desc:
                payload.update(description=self.desc)
            if self.kernel:
                payload.update(kernel=self.kernel)
            if self.memory:
                payload.update(memory=self.memory)
            if self.gpu:
                payload.update(nvidia_gpu=self.gpu)
            if self.addons:
                payload.update(runtime_addon_identifiers=self.addons)
            if self.runtime:
                payload.update(runtime_identifier=self.runtime)
            if self.script:
                payload.update(script=self.script)
            if self.subdomain:
                if not validate_subdomain(self.subdomain):
                    self.module.fail_json(msg="Invalid subdomain format")
                payload.update(subdomain=self.subdomain)

            if existing:
                if self.env:
                    payload.update(
                        environment=json.dumps(self.env, separators=(",", ":")),
                    )
                diff = difference(payload, existing)

                if diff and not self.module.check_mode:
                    # Update the application
                    self.changed = True
                    self.application = self.query(
                        method="PATCH",
                        api=["projects", project["id"], "applications", existing["id"]],
                        body=diff,
                    )
                else:
                    self.application = existing

                if (
                    self.state == "restarted"
                ):  # TODO Check existing status, i.e. and existing['status'] == ???
                    # Force restart the application
                    self.application = self.query(
                        method="POST",
                        api=[
                            "projects",
                            project["id"],
                            "applications",
                            existing["id"] + ":restart",
                        ],
                    )
                elif self.state == "stopped":  # TODO Check existing status
                    # Stop the application
                    self.application = self.query(
                        method="POST",
                        api=[
                            "projects",
                            project["id"],
                            "applications",
                            existing["id"] + ":stop",
                        ],
                    )
            else:
                # Create the application
                if self.env:
                    payload.update(environment=self.env)

                missing_keys = set(["subdomain", "script", "runtime_identifier"]) - set(
                    payload.keys(),
                )
                if missing_keys:
                    self.module.fail_json(
                        msg="Missing required parameters for creation: "
                        + ", ".join(missing_keys),
                    )

                if not self.module.check_mode:
                    self.changed = True
                    self.application = self.query(
                        method="POST",
                        api=["projects", project["id"], "applications"],
                        body=payload,
                    )
        elif existing and not self.module.check_mode:
            # Delete the application
            self.changed = True
            self.query(
                method="DELETE",
                api=["projects", project["id"], "applications", existing["id"]],
            )


def main():
    module = MLProjectApplication.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            name=dict(required=False, type="str"),
            id=dict(required=False, type="str", aliases=["application_id"]),
            auth=dict(required=False, type="bool", aliases=["auth_enabled"]),
            cpu=dict(required=False, type="float"),  # vCPU
            creator=dict(
                required=False,
                type="dict",
                options=dict(
                    email=dict(required=False, type="str"),
                    name=dict(required=False, type="str"),
                    username=dict(required=False, type="str"),
                ),
            ),
            desc=dict(required=False, type="str", aliases=["description"]),
            env=dict(required=False, type="dict", aliases=["env_vars"]),
            kernel=dict(
                required=False,
                type="str",
                choices=["python3", "python2", "r", "scala"],
            ),
            memory=dict(required=False, type="float"),  # GB
            gpu=dict(required=False, type="int", aliases=["nvidia_gpu"]),
            addons=dict(
                required=False,
                type="list",
                elements="str",
                aliases=["runtime_addons", "runtime_addon_identifiers"],
            ),
            runtime=dict(
                required=False,
                type="str",
                aliases=["runtime_image_id", "runtime_identifier"],
            ),
            script=dict(required=False, type="str"),
            subdomain=dict(required=False, type="str"),
            state=dict(
                required=False,
                type="str",
                choices=["present", "restarted", "stopped", "absent"],
                default="present",
            ),
        ),
        required_one_of=[
            ["name", "id"],
            ["project_name", "project_id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectApplication(module)

    output = dict(
        changed=result.changed,
        application=result.application,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

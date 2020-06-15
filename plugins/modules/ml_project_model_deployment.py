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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.ml import (
    MLModule,
    difference,
    validate_project_id,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: ml_project_model_deployment
short_description: Create, update, and delete a Cloudera Machine Learning (CML) project model deployment.
description:
  - Create, update, and delete a Cloudera Machine Learning (CML) project model deployment.
  - The module supports check_mode.
  - The module supports the C(v2) API only.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  debug:
    description:
      - Flag to capture and return the debugging log of the underlying CDP SDK.
      - If set, the log level will be set from ERROR to DEBUG.
    aliases:
      - debug_cdpsdk
    default: False
    type: bool
"""

EXAMPLES = r"""

"""

RETURN = r"""
---
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


class MLProjectModelDeployment(MLModule):
    def __init__(self, module):
        super(MLProjectModelDeployment, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.model_name = self._get_param("model_name")
        self.model_id = self._get_param("model_id")
        self.build_id = self._get_param("build_id")
        self.id = self._get_param("id")
        self.cpu = self._get_param("cpu")
        self.env = self._get_param("env")
        self.memory = self._get_param("memory")
        self.gpu = self._get_param("gpu")
        self.state = self._get_param("state")

        # Initialize the return values
        self.changed = False
        self.deployment = {}

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

        model = None
        if self.model_id:
            model = self.get_model(project["id"], self.model_id)
        else:
            model = self.find_model(project["id"], self.model_name)

        if not model:
            self.module.fail_json(msg="Model not found")

        build = None
        if self.build_id:
            build = self.get_build(project["id"], model["id"], self.build_id)
        else:
            build = self.find_latest_build(project["id"], model["id"])

        if not build:
            self.module.fail_json(msg="Model build not found")

        existing = None
        if self.id:
            existing = self.query(
                method="GET",
                api=[
                    "projects",
                    project["id"],
                    "models",
                    model["id"],
                    "builds",
                    build["id"],
                    "deployments",
                    self.id,
                ],
            )
        else:
            deployment_list = self.query(
                method="GET",
                api=[
                    "projects",
                    project["id"],
                    "models",
                    model["id"],
                    "builds",
                    build["id"],
                    "deployments",
                ],
                params=dict(
                    sorted="-created_at",
                    search_filter=json.dumps(
                        dict(status="deployed"),
                        separators=(",", ":"),
                    ),
                ),
                field="model_deployments",
            )
            if deployment_list:
                existing = deployment_list[0]

        if self.state == "started":
            payload = dict()
            if self.cpu:
                payload.update(cpu=self.cpu)
            if self.memory:
                payload.update(memory=self.memory)
            if self.gpu:
                payload.update(nvidia_gpus=self.gpu)

            if existing:
                if self.env:
                    payload.update(
                        environment=json.dumps(self.env, separators=(",", ":")),
                    )
                diff = difference(payload, existing)
                if diff:
                    self.module.warn(
                        "Deployment exists and deployment reconciliation is not supported. "
                        + "To change, explicitly rebuild the model and redeploy.",
                    )
                self.deployment = existing
            else:
                if self.env:
                    payload.update(environment=self.env)
                if not self.module.check_mode:
                    self.changed = True
                    self.deployment = self.query(
                        method="POST",
                        api=[
                            "projects",
                            project["id"],
                            "models",
                            model["id"],
                            "builds",
                            build["id"],
                            "deployments",
                        ],
                        body=payload,
                    )
        elif existing and not self.module.check_mode:
            self.changed = True
            self.deployment = self.query(
                method="POST",
                api=[
                    "projects",
                    project["id"],
                    "models",
                    model["id"],
                    "builds",
                    build["id"],
                    "deployments",
                    existing["id"] + ":stop",
                ],
            )


def main():
    module = MLProjectModelDeployment.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            model_name=dict(required=False, type="str"),
            model_id=dict(required=False, type="str"),
            build_id=dict(required=False, type="str"),
            id=dict(required=False, type="str", aliases=["deployment_id"]),
            cpu=dict(required=False, type="int"),
            env=dict(required=False, type="dict", aliases=["env_vars"]),
            memory=dict(required=False, type="int"),
            gpu=dict(required=False, type="int", aliases=["nvidia_gpus"]),
            state=dict(
                required=False,
                type="str",
                choices=["started", "stopped"],
                default="started",
            ),
        ),
        required_one_of=[
            ["project_name", "project_id"],
            ["model_name", "model_id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectModelDeployment(module)

    output = dict(
        changed=result.changed,
        deployment=result.deployment,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

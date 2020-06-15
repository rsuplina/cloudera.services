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
module: ml_project_model_build
short_description: Create, update, and delete a Cloudera Machine Learning (CML) project model build.
description:
  - Create, update, and delete a Cloudera Machine Learning (CML) project model build.
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


class MLProjectModelBuild(MLModule):
    def __init__(self, module):
        super(MLProjectModelBuild, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.model_name = self._get_param("model_name")
        self.model_id = self._get_param("model_id")
        self.id = self._get_param("id")
        self.comment = self._get_param("comment")
        self.file = self._get_param("file")
        self.function = self._get_param("function")
        self.kernel = self._get_param("kernel")
        self.addons = self._get_param("addons")
        self.runtime = self._get_param("runtime")
        self.state = self._get_param("state")

        # Initialize the return values
        self.changed = False
        self.build = {}

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

        existing = None
        if self.id:
            existing = self.get_build(project["id"], model["id"], self.id)

        if self.state == "present":
            payload = dict()
            if self.comment:
                payload.update(comment=self.comment)
            if self.file:
                payload.update(file_path=self.file)
            if self.function:
                payload.update(function_name=self.function)
            if self.kernel:
                payload.update(kernel=self.kernel)
            if self.addons:
                payload.update(runtime_addon_identifiers=self.addons)
            if self.runtime:
                payload.update(runtime_identifier=self.runtime)

            if existing:
                diff = difference(payload, existing)
                if diff:
                    self.module.warn(
                        "Build exists and build reconciliation is not supported. "
                        + "To change, explicitly delete and recreate the build.",
                    )
                self.build = existing
            else:
                if not self.module.check_mode:
                    self.changed = True
                    self.build = self.query(
                        method="POST",
                        api=[
                            "projects",
                            project["id"],
                            "models",
                            model["id"],
                            "builds",
                        ],
                        body=payload,
                    )
        elif existing and not self.module.check_mode:
            self.changed = True
            self.query(
                method="DELETE",
                api=[
                    "projects",
                    project["id"],
                    "models",
                    model["id"],
                    "builds",
                    existing["id"],
                ],
            )


def main():
    module = MLProjectModelBuild.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            model_name=dict(required=False, type="str"),
            model_id=dict(required=False, type="str"),
            id=dict(required=False, type="str"),
            comment=dict(required=False, type="str"),
            file=dict(required=False, type="str", aliases=["file_path"]),
            function=dict(required=False, type="str", aliases=["function_name"]),
            kernel=dict(
                required=False,
                type="str",
                choices=["python3", "python2", "r"],
            ),
            addons=dict(
                required=False,
                type="list",
                elements="str",
                aliases=["runtime_addon_ids"],
            ),
            runtime=dict(required=False, type="str", aliases=["runtime_id"]),
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
        ),
        required_one_of=[
            ["project_name", "project_id"],
            ["model_name", "model_id"],
            ["id", "file"],
        ],
        required_together=[
            ["file", "function", "runtime"],
        ],
        required_by={
            "kernel": ["runtime"],
            "addons": ["runtime"],
        },
        supports_check_mode=True,
    )

    result = MLProjectModelBuild(module)

    output = dict(
        changed=result.changed,
        build=result.build,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

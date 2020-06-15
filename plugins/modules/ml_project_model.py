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
module: ml_project_model
short_description: Create, update, and delete a Cloudera Machine Learning (CML) project model.
description:
  - Create, update, and delete a Cloudera Machine Learning (CML) project model.
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


class MLProjectModel(MLModule):
    def __init__(self, module):
        super(MLProjectModel, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.desc = self._get_param("desc")
        self.auth = self._get_param("auth")
        self.state = self._get_param("state")

        # Initialize the return values
        self.changed = False
        self.model = {}

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

        if self.id:
            existing = self.get_model(project["id"], self.id)
            if not existing:
                self.module.fail_json(msg="Model not found")
        else:
            existing = self.find_model(project["id"], self.name)

        if self.state == "present":
            payload = dict()
            if self.name:
                payload.update(name=self.name)
            if self.desc:
                payload.update(description=self.desc)
            if self.auth is not None:
                payload.update(disable_authentication=not self.auth)  # Note reversal

            if existing:
                diff = difference(payload, existing)
                if diff:
                    self.module.warn(
                        "Model exists and model reconciliation is not supported. "
                        + "To change, explicitly delete and recreate the model.",
                    )
                self.model = existing
            else:
                if not payload["description"]:
                    self.module.fail_json(
                        msg="the following is required for new models: 'desc'",
                    )
                if not self.module.check_mode:
                    self.changed = True
                    self.model = self.query(
                        method="POST",
                        api=["projects", project["id"], "models"],
                        body=payload,
                    )
        elif existing and not self.module.check_mode:
            self.changed = True
            self.query(
                method="DELETE",
                api=["projects", project["id"], "models", existing["id"]],
            )


def main():
    module = MLProjectModel.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            name=dict(required=False, type="str", aliases=["model_name"]),
            id=dict(required=False, type="str", aliases=["model_id"]),
            desc=dict(required=False, type="str", aliases=["description"]),
            auth=dict(required=False, type="bool", aliases=["auth_enabled"]),
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
        ),
        required_one_of=[
            ["project_name", "project_id"],
            ["name", "id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectModel(module)

    output = dict(
        changed=result.changed,
        model=result.model,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

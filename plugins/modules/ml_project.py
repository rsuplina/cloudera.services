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
module: ml_project
short_description: Create and delete Cloudera Machine Learning (CML) project
description:
  - Create and delete a Cloudera Machine Learning (CML) project.
  - The module supports check_mode.
  - The module supports the C(v1) API only.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  name:
    description:
      - The name of the CML project
    required: false
    type: str
    aliases:
      - project
  id:
    description:
      - Id of an existing CML project
    required: false
    type: str
    aliases:
      - project_id
  desc:
    description:
      - Description of the project
    required: false
    type: str
    aliases:
      - description
  template:
    description:
      - Template to use for the CML project
    required: false
    type: str
    choices:
      - R
      - Python
      - PySpark
      - Scala
      - Churn Predictor
      - local
      - git
      - blank
  visibility:
    description:
      - Visibility of the project
    required: false
    type: str
    choices:
      - public
      - private
      - organization
  git:
    description:
      - URL of the Git repository.
      - Required for I(template=git).
    required: false
    type: str
    aliases:
      - git_url
  git_branch:
    description:
      - Branch for the Git repository.
      - Only used if I(template=git) is specified.
    required: false
    type: str
    aliases:
      - git_ref
  runtime:
    description:
      - Runtime of the CML project
    required: false
    type: str
    choices:
      - ml_runtime
      - legacy_engine
    aliases:
      - default_project_engine_type
  env:
    description:
      - Environment variables that can be accessed from your scripts within the project
    required: false
    type: dict
    aliases:
      - environment_variables
  permission:
    description:
      - Permissions for a user inside the CML project
    required: false
    type: str
    aliases:
      - organization_permission
  parent:
    description:
      - Name of parent project
    required: false
    type: str
    aliases:
      - parent_project
  memory:
    description:
      - Additional shared memory limit that each engine in this project has.
      - Expressed in MB.
    required: false
    type: int
    aliases:
      - shared_memory_limit
  state:
    description:
      - The declarative state of the CML project
    required: false
    type: str
    default: present
    choices:
      - present
      - absent
extends_documentation_fragment:
  - cloudera.services.ml_endpoint
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


class MLProject(MLModule):
    def __init__(self, module):
        super(MLProject, self).__init__(module)

        # Set parameters
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.desc = self._get_param("desc")
        self.user = self._get_param("user")
        self.template = self._get_param("template")
        self.visibility = self._get_param("visibility")
        self.git = self._get_param("git")
        self.git_branch = self._get_param("git_branch")
        self.runtime = self._get_param("runtime")
        self.env = self._get_param("env")
        self.permission = self._get_param("permission")
        self.parent = self._get_param("parent")
        self.memory = self._get_param("memory")
        self.state = self._get_param("state")

        # Initialize the return values
        self.changed = False
        self.project = {}

        # Execute logic process
        self.process()

    def process(self):
        existing = None
        if self.id:
            if not validate_project_id(self.id):
                self.module.fail_json(msg="Invalid Project ID: " + self.id)
            existing = self.get_project(self.id)
        else:
            existing = self.find_project(self.name)

        if self.state == "present":
            payload = dict()
            # Create and update
            if self.name:
                payload.update(name=self.name)
            if self.desc:
                payload.update(description=self.desc)
            if self.env:
                payload.update(environment=self.env)
            if self.permission:
                payload.update(organization_permission=self.permission)
            if self.parent:
                payload.update(parent_project=self.parent)
            if self.memory:
                payload.update(shared_memory_limit=self.memory)
            if self.visibility:
                payload.update(visibility=self.visibility)

            # Update the project
            if existing:
                if self.runtime:
                    payload.update(default_engine_type=self.runtime)
                if self.env:
                    # Merge environment variables if they are present in the existing project
                    if "environment" in existing:
                        merged_env = {**json.loads(existing["environment"]), **self.env}
                        payload.update(
                            environment=json.dumps(merged_env, separators=(",", ":")),
                        )
                    else:
                        payload.update(
                            environment=json.dumps(self.env, separators=(",", ":")),
                        )
                # creator
                # owner
                diff = difference(payload, existing)
                if diff and not self.module.check_mode:
                    self.changed = True
                    self.project = self.query(
                        method="PATCH",
                        api=["projects", existing["id"]],
                        body=diff,
                    )
                else:
                    self.project = existing
            # Create the project
            else:
                if self.git:
                    payload.update(git_url=self.git)
                if self.git_branch:
                    payload.update(git_ref=self.git_branch)
                if self.template:
                    payload.update(template=self.template)
                if self.runtime:
                    payload.update(default_project_engine_type=self.runtime)
                if "template" not in payload:
                    payload.update(template="blank")
                if not self.module.check_mode:
                    self.changed = True
                    self.project = self.query(
                        method="POST",
                        api=["projects"],
                        body=payload,
                    )
        elif existing and not self.module.check_mode:
            # Delete the project
            self.changed = True
            self.query(method="DELETE", api=["projects", existing["id"]])


def main():
    # TODO Add creator and owner dicts
    module = MLProject.ansible_module(
        argument_spec=dict(
            name=dict(required=False, type="str", aliases=["project"]),
            id=dict(required=False, type="str", aliases=["project_id"]),
            desc=dict(required=False, type="str", aliases=["description"]),
            user=dict(required=False, type="str", aliases=["username"]),
            template=dict(
                required=False,
                type="str",
                choices=[
                    "R",
                    "Python",
                    "PySpark",
                    "Scala",
                    "Churn Predictor",
                    "local",
                    "git",
                    "blank",
                ],
            ),
            visibility=dict(
                required=False,
                type="str",
                choices=["public", "organization", "private"],
            ),
            git=dict(required=False, type="str", aliases=["git_url"]),
            git_branch=dict(required=False, type="str", aliases=["git_ref"]),
            runtime=dict(
                required=False,
                type="str",
                choices=["ml_runtime", "legacy_engine"],
                aliases=["default_project_engine_type"],
            ),
            env=dict(required=False, type="dict", aliases=["environment_variables"]),
            permission=dict(
                required=False,
                type="str",
                aliases=["organization_permission"],
            ),
            parent=dict(required=False, type="str", aliases=["parent_project"]),
            memory=dict(required=False, type="int", aliases=["shared_memory_limit"]),
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
        ),
        required_one_of=[["name", "id"]],
        supports_check_mode=True,
    )

    result = MLProject(module)

    output = dict(
        changed=result.changed,
        project=result.project,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

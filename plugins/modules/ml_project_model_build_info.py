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
    validate_project_id,
)


DOCUMENTATION = r"""
module: ml_project_model_build_info
short_description: Get information for Cloudera Machine Learning (CML) project model builds
description:
  - Get information for one or more Cloudera Machine Learning (CML) project model builds
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


class MLProjectModelBuildInfo(MLModule):
    def __init__(self, module):
        super(MLProjectModelBuildInfo, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.comment = self._get_param("comment")
        self.creator_email = self._get_param("creator", "email")
        self.creator_name = self._get_param("creator", "name")
        self.creator_username = self._get_param("creator", "username")
        self.crn = self._get_param("crn")
        self.status = self._get_param("status")

        # Initialize the return values
        self.builds = []

        # Execute logic process
        self.process()

    @MLModule.process_debug
    def process(self):
        project = None
        if self.project_id:
            if not validate_project_id(self.project_id):
                self.module.fail_json(msg="Invalid Project ID: " + self.project_id)
            project = self.get_project(self.project_id)
        else:
            project = self.find_project(self.project_name)

        if not project:
            self.module.fail_json(msg="Project not found")

        model = None
        if self.id:
            model = self.get_model(project["id"], self.id)
        else:
            model = self.find_model(project["id"], self.name)

        if not model:
            self.module.fail_json(msg="Model not found")

        search_filter = dict()
        if self.comment:
            search_filter["comment"] = self.comment
        if self.creator_email:
            search_filter["creator.email"] = self.creator_email
        if self.creator_name:
            search_filter["creator.name"] = self.creator_name
        if self.creator_username:
            search_filter["creator.username"] = self.creator_username
        if self.crn:
            search_filter["crn"] = self.crn
        if self.status:
            search_filter["status"] = self.status

        query_params = dict(sort="-updated_at")
        if search_filter:
            query_params.update(
                search_filter=json.dumps(search_filter, separators=(",", ":")),
            )

        self.builds = self.query(
            method="GET",
            api=["projects", project["id"], "models", model["id"], "builds"],
            field="model_builds",
            params=query_params,
        )


def main():
    module = MLProjectModelBuildInfo.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            name=dict(required=False, type="str", aliases=["model_name"]),
            id=dict(required=False, type="str", aliases=["model_id"]),
            comment=dict(required=False, type="str"),
            creator=dict(
                required=False,
                type="dict",
                options=dict(
                    email=dict(required=False, type="str"),
                    name=dict(required=False, type="str"),
                    username=dict(required=False, type="str"),
                ),
            ),
            crn=dict(required=False, type="str"),
            status=dict(
                required=False,
                type="str",
                choices=[
                    "pending",
                    "succeeded",
                    "built",
                    "build failed",
                    "timedout",
                    "pushing",
                    "queued",
                    "unknown",
                ],
            ),
        ),
        required_one_of=[
            ["project_name", "project_id"],
            ["name", "id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectModelBuildInfo(module)

    output = dict(
        changed=result.changed,
        model_builds=result.builds,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

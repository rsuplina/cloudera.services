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
module: ml_project_model_info
short_description: Get information for Cloudera Machine Learning (CML) project models
description:
  - Get information for one or more Cloudera Machine Learning (CML) project models
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


class MLProjectModelInfo(MLModule):
    def __init__(self, module):
        super(MLProjectModelInfo, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.auth = self._get_param("auth")
        self.creator_email = self._get_param("creator", "email")
        self.creator_name = self._get_param("creator", "name")
        self.creator_username = self._get_param("creator", "username")
        self.desc = self._get_param("desc")

        # Initialize the return values
        self.models = []

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
            self.models = [self.get_model(project["id"], self.id)]
        else:
            search_filter = dict()
            if self.auth is not None:
                search_filter["auth_enabled"] = str(self.auth)
            if self.creator_email:
                search_filter["creator.email"] = self.creator_email
            if self.creator_name:
                search_filter["creator.name"] = self.creator_name
            if self.creator_username:
                search_filter["creator.username"] = self.creator_username
            if self.desc:
                search_filter["description"] = self.desc
            if self.name:
                search_filter["name"] = self.name

            query = dict(
                method="GET",
                api=["projects", project["id"], "models"],
                field="models",
            )

            if search_filter:
                self.models = self.query(
                    **query,
                    params=dict(
                        search_filter=json.dumps(search_filter, separators=(",", ":")),
                    ),
                )
            else:
                self.models = self.query(**query)


def main():
    module = MLProjectModelInfo.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            name=dict(required=False, type="str", aliases=["model"]),
            id=dict(required=False, type="str", aliases=["model_id"]),
            auth=dict(required=False, type="bool", aliases=["auth_enabled"]),
            creator=dict(
                required=False,
                type="dict",
                options=dict(
                    email=dict(required=False, type="str"),
                    name=dict(required=False, type="str"),
                    username=dict(required=False, type="str"),
                ),
            ),
            desc=dict(required=False, type="str"),
        ),
        required_one_of=[
            ["project_name", "project_id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectModelInfo(module)

    output = dict(
        changed=result.changed,
        models=result.models,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

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

DOCUMENTATION = r"""
module: ssb_table_info
short_description: Retrieve information about SSB project tables
description:
  - Retrieve information about one or more Cloudera SSB project tables.
  - The module can list all tables in a project or filter by table name or id.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
options:
  project_id:
    description:
      - The unique identifier of the project containing the table(s).
      - Required for all operations.
    type: str
    required: true
  table_name:
    description:
      - The name of the table to retrieve.
      - This parameter is mutually exclusive with O(id).
    type: str
    required: false
  id:
    description:
      - The unique identifier of the table to retrieve.
      - This parameter is mutually exclusive with O(table_name).
    type: int
    required: false
    aliases:
      - table_id
extends_documentation_fragment:
  - cloudera.services.services_client
"""

EXAMPLES = r"""
- name: List all SSB tables in a project
  cloudera.services.ssb_table_info:
    project_id: "12345"
  register: all_tables

- name: Get information about a specific table by name
  cloudera.services.ssb_table_info:
    project_id: "12345"
    table_name: "my_table"
  register: table_by_name

- name: Get information about a specific table by id
  cloudera.services.ssb_table_info:
    project_id: "12345"
    id: 789
  register: table_by_id
"""

RETURN = r"""
tables:
    description: List of SSB project tables.
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The unique identifier of the table.
            type: int
            returned: when available
        table_name:
            description: The name of the table.
            type: str
            returned: always
        type:
            description: The type of the table.
            type: str
            returned: always
        metadata:
            description: Dictionary of metadata for the table.
            type: dict
            returned: always
        transform_code:
            description: Optional transformation code for the table.
            type: str
            returned: when available
        transform_code_b64_encoded:
            description: Whether the transform_code is base64 encoded.
            type: bool
            returned: when available
        project_id:
            description: The project identifier this table belongs to.
            type: str
            returned: when available
        created_at:
            description: Timestamp when the table was created.
            type: str
            returned: when available
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

from typing import Any, Dict, List

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesModule,
    to_dict,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbTable,
    SsbTableClient,
)


class SsbTableInfoModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                project_id=dict(type="str", required=True),
                table_name=dict(type="str", required=False),
                id=dict(type="int", required=False, aliases=["table_id"]),
            ),
            mutually_exclusive=[["table_name", "id"]],
            supports_check_mode=True,
        )

        # Set parameters
        self.project_id = self.get_param("project_id")
        self.table_name = self.get_param("table_name")
        self.table_id = self.get_param("id")

        # Initialize result variables
        self.table_list: List[SsbTable] = []

    def process(self) -> None:
        client = SsbTableClient(self.api_client)
        if self.table_id:
            table = client.describe_table(
                project_id=self.project_id,
                table_id=self.table_id,
            )
            if table:
                self.table_list.append(table)
        else:
            tables = client.list_tables(project_id=self.project_id)
            if self.table_name:
                tables = [t for t in tables if t.table_name == self.table_name]
            self.table_list.extend(tables)


def main():
    result = SsbTableInfoModule()

    output: Dict[str, Any] = dict(
        changed=False,
        tables=[to_dict(table) for table in result.table_list],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

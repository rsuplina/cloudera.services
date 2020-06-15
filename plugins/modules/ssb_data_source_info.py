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
module: ssb_data_source_info
short_description: Retrieve information about SSB project data sources
description:
  - Retrieve information about one or more Cloudera SSB project data sources.
  - The module can list all data sources in a project or filter by name or id.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
options:
  project_id:
    description:
      - The unique identifier of the project containing the data source(s).
      - Required for all operations.
    type: str
    required: true
  name:
    description:
      - The name of the data source to retrieve.
      - This parameter is mutually exclusive with O(id).
    type: str
    required: false
  id:
    description:
      - The unique identifier of the data source to retrieve.
      - This parameter is mutually exclusive with O(name).
    type: str
    required: false
    aliases:
      - data_source_id
  kafka:
    description:
      - When listing data sources, filter to only Kafka data sources.
      - Is ignored if O(id) is specified.
    type: bool
    default: false
extends_documentation_fragment:
  - cloudera.services.services_client
"""

EXAMPLES = r"""
- name: List all SSB data sources in a project
  cloudera.services.ssb_data_source_info:
    project_id: "12345"
  register: all_data_sources

- name: List only Kafka data sources in a project
  cloudera.services.ssb_data_source_info:
    project_id: "12345"
    kafka: true
  register: kafka_data_sources

- name: Get information about a specific data source by name
  cloudera.services.ssb_data_source_info:
    project_id: "12345"
    name: "my-kafka-source"
  register: data_source_by_name

- name: Get information about a specific data source by id
  cloudera.services.ssb_data_source_info:
    project_id: "12345"
    id: "789"
  register: data_source_by_id
"""

RETURN = r"""
data_sources:
    description: List of SSB project data sources.
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The unique identifier of the data source.
            type: str
            returned: when available
        name:
            description: The name of the data source.
            type: str
            returned: always
        type:
            description: The type of the data source (e.g., KAFKA, POSTGRES).
            type: str
            returned: when available
        properties:
            description: Dictionary of configuration properties for the data source.
            type: dict
            returned: when available
        custom_truststore:
            description: Path to custom truststore file.
            type: str
            returned: when available
        created_at:
            description: Timestamp when the data source was created.
            type: str
            returned: when available
        updated_at:
            description: Timestamp when the data source was last updated.
            type: str
            returned: when available
        project_id:
            description: The project identifier this data source belongs to.
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
    SsbDataSource,
    SsbDataSourceClient,
)


class SsbDataSourceInfoModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                project_id=dict(type="str", required=True),
                name=dict(type="str", required=False),
                id=dict(type="str", required=False, aliases=["data_source_id"]),
                kafka=dict(type="bool", required=False, default=False),
            ),
            mutually_exclusive=[["name", "id"]],
            supports_check_mode=True,
        )

        # Set parameters
        self.project_id = self.get_param("project_id")
        self.name = self.get_param("name")
        self.data_source_id = self.get_param("id")
        self.kafka = self.get_param("kafka")

        # Initialize result variables
        self.data_source_list: List[SsbDataSource] = []

    def process(self) -> None:
        client = SsbDataSourceClient(self.api_client)
        if self.data_source_id:
            data_source = client.describe_data_source(
                project_id=self.project_id,
                data_source_id=self.data_source_id,
            )
            if data_source:
                self.data_source_list.append(data_source)
        else:
            data_sources = client.list_data_sources(
                project_id=self.project_id,
                kafka=self.kafka,
            )
            if self.name:
                data_sources = [ds for ds in data_sources if ds.name == self.name]
            self.data_source_list.extend(data_sources)


def main():
    result = SsbDataSourceInfoModule()

    output: Dict[str, Any] = dict(
        changed=False,
        data_sources=[to_dict(data_source) for data_source in result.data_source_list],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

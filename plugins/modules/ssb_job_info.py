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
module: ssb_job_info
short_description: Retrieve information about SSB jobs
description:
  - Retrieve information about one or more Cloudera SQL Stream Builder (SSB) jobs.
  - The module can list all jobs in a project or filter by job ID, name, or state.
  - The module supports C(check_mode).
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
options:
  project_id:
    description:
      - The unique identifier of the project containing the jobs.
      - This parameter is required as jobs are scoped to projects.
    type: str
    required: true
  job_id:
    description:
      - The unique identifier of a specific job to retrieve.
      - When specified, only this job will be returned.
      - This parameter is mutually exclusive with O(name) and O(state).
    type: int
    required: false
  name:
    description:
      - The name of the job to filter by.
      - When specified, only jobs matching this name will be returned.
      - This parameter is mutually exclusive with O(job_id).
    type: str
    required: false
  state:
    description:
      - Filter jobs by their current state.
      - When specified, only jobs in this state will be returned.
      - This parameter is mutually exclusive with O(job_id).
    type: str
    required: false
    choices:
      - INITIALIZING
      - CREATED
      - RUNNING
      - FAILING
      - FAILED
      - CANCELLING
      - CANCELED
      - FINISHED
      - RESTARTING
      - SUSPENDED
      - RECONCILING
extends_documentation_fragment:
  - cloudera.services.services_client
"""

EXAMPLES = r"""
- name: List all jobs in a project
  cloudera.services.ssb_job_info:
    project_id: "12345"
  register: all_jobs

- name: Get information about a specific job by ID
  cloudera.services.ssb_job_info:
    project_id: "12345"
    job_id: 67890
  register: specific_job

- name: List all running jobs in a project
  cloudera.services.ssb_job_info:
    project_id: "12345"
    state: RUNNING
  register: running_jobs

- name: Get jobs by name
  cloudera.services.ssb_job_info:
    project_id: "12345"
    name: "my-streaming-job"
  register: jobs_by_name
"""

RETURN = r"""
jobs:
    description: List of SSB jobs matching the specified criteria.
    returned: always
    type: list
    elements: dict
    contains:
        job_id:
            description: The unique identifier of the job.
            type: int
            returned: when available
        name:
            description: The name of the job.
            type: str
            returned: always
        sql:
            description: The SQL query executed by this job.
            type: str
            returned: always
        state:
            description: The current state of the job.
            type: str
            returned: when available
        start_time:
            description: Timestamp when the job was started (epoch milliseconds).
            type: int
            returned: when available
        end_time:
            description: Timestamp when the job ended (epoch milliseconds).
            type: int
            returned: when available
        user_id:
            description: The ID of the user who created the job.
            type: str
            returned: when available
        username:
            description: The username of the user who created the job.
            type: str
            returned: when available
        project_id:
            description: The ID of the project containing this job.
            type: str
            returned: when available
        flink_job_id:
            description: The Flink job ID associated with this SSB job.
            type: str
            returned: when available
        created_at:
            description: Timestamp when the job was created.
            type: str
            returned: when available
        cluster_id:
            description: The ID of the cluster running this job.
            type: str
            returned: when available
        sample_id:
            description: The sample ID for this job.
            type: str
            returned: when available
        jm_url:
            description: The URL to the Flink JobManager for this job.
            type: str
            returned: when available
        mv_endpoints:
            description: List of materialized view API endpoints for this job.
            type: list
            elements: dict
            returned: when available
        mv_config:
            description: Materialized view configuration for this job.
            type: dict
            returned: when available
        checkpoint_config:
            description: Checkpoint configuration for this job.
            type: dict
            returned: when available
        kubernetes_config:
            description: Kubernetes configuration for this job.
            type: dict
            returned: when available
        autoscaler_config:
            description: Autoscaler configuration for this job.
            type: dict
            returned: when available
        savepoint_id:
            description: The ID of the savepoint associated with this job.
            type: int
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
    SsbJob,
    SsbJobClient,
)


class SsbJobInfoModule(ServicesModule):
    def __init__(self):
        super().__init__(
            argument_spec=dict(
                project_id=dict(type="str", required=True),
                job_id=dict(type="int", required=False),
                name=dict(type="str", required=False),
                state=dict(
                    type="str",
                    required=False,
                    choices=[
                        "INITIALIZING",
                        "CREATED",
                        "RUNNING",
                        "FAILING",
                        "FAILED",
                        "CANCELLING",
                        "CANCELED",
                        "FINISHED",
                        "RESTARTING",
                        "SUSPENDED",
                        "RECONCILING",
                    ],
                ),
            ),
            mutually_exclusive=[
                ["job_id", "name"],
                ["job_id", "state"],
            ],
            supports_check_mode=True,
        )

        # Set parameters
        self.project_id = self.get_param("project_id")
        self.job_id = self.get_param("job_id")
        self.name = self.get_param("name")
        self.state = self.get_param("state")

        # Initialize result variables
        self.job_list: List[SsbJob] = []

    def process(self) -> None:
        client = SsbJobClient(self.api_client)

        if self.job_id:
            # Get a specific job by ID
            job = client.describe_job(
                project_id=self.project_id,
                job_id=self.job_id,
            )
            if job:
                self.job_list.append(job)
        else:
            # List jobs, optionally filtered by state
            jobs = client.list_jobs(
                project_id=self.project_id,
                state=self.state,
            )

            # Further filter by name if specified
            if self.name:
                jobs = [j for j in jobs if j.name == self.name]

            self.job_list.extend(jobs)


def main():
    result = SsbJobInfoModule()

    output: Dict[str, Any] = dict(
        changed=False,
        jobs=[to_dict(job) for job in result.job_list],
    )

    if result.debug_log:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    result.module.exit_json(**output)


if __name__ == "__main__":
    main()

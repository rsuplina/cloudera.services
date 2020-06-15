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

import time

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
module: ml_project_job_run
short_description: Start and stop a Cloudera Machine Learning (CML) project job.
description:
  - Start and stop a Cloudera Machine Learning (CML) project job.
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

# ENGINE_SCHEDULING, ENGINE_STARTING, ENGINE_RUNNING, ENGINE_STOPPING, ENGINE_STOPPED,
# ENGINE_UNKNOWN, ENGINE_SUCCEEDED, ENGINE_FAILED, ENGINE_TIMEDOUT


class MLProjectJobRun(MLModule):
    def __init__(self, module):
        super(MLProjectJobRun, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.arguments = self._get_param("arguments")
        self.env = self._get_param("env")

        self.state = self._get_param("state")
        self.wait = self._get_param("wait")
        self.delay = self._get_param("delay")
        self.timeout = self._get_param("timeout")

        # Initialize the return values
        self.changed = False
        self.job_run = {}

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

        job = None
        if self.id:
            job = self.get_job(project["id"], self.id)
        else:
            job = self.find_job(project["id"], self.name)

        if not job:
            self.module.fail_json(msg="Job not found")

        history = self._get_history(project["id"], job["id"])

        if self.state == "started":
            # Start or scheduled to start
            payload = dict()
            if self.arguments:
                payload.update(arguments=self.arguments)
            if self.env:
                payload.update(environment=self.env)

            if not history or history[0]["status"] not in [
                "ENGINE_STARTING",
                "ENGINE_RUNNING",
                "ENGINE_SCHEDULING",
            ]:
                # If never run or not currently started or scheduled to start
                if not self.module.check_mode:
                    self.changed = True
                    query = dict(
                        method="POST",
                        api=["projects", project["id"], "jobs", job["id"], "runs"],
                    )
                    if payload:
                        query.update(body=payload)
                    self.job_run = self.query(**query)
            else:
                # Else has started or currently scheduled to start
                self.job_run = history[0]
            if self.wait:
                # Wait for a terminal condition
                self.job_run = self._wait_for_state(
                    project["id"],
                    job["id"],
                    ["ENGINE_SUCCEEDED"],
                    ["ENGINE_FAILED", "ENGINE_UNKNOWN", "ENGINE_STOPPED"],
                )
        else:
            # Stopped or stopping
            if history and history[0]["status"] in [
                "ENGINE_STARTING",
                "ENGINE_RUNNING",
                "ENGINE_SCHEDULING",
            ]:
                # If run before and is currently running, starting, or scheduled to start
                if not self.module.check_mode:
                    self.changed = True
                    self.job_run = self.query(
                        method="POST",
                        api=[
                            "projects",
                            project["id"],
                            "jobs",
                            job["id"],
                            "runs",
                            history[0]["id"] + ":stop",
                        ],
                    )
            elif history:
                # Else is stopping or is stopped or other terminal state
                self.job_run = history[0]
            if self.wait:
                # Wait for terminal condition
                self.job_run = self._wait_for_state(
                    project["id"],
                    job["id"],
                    ["ENGINE_STOPPED", "ENGINE_SUCCEEDED"],
                    [
                        "ENGINE_FAILED",
                        "ENGINE_TIMEDOUT",
                        "ENGINE_RUNNING",
                        "ENGINE_UNKNOWN",
                    ],
                )

    def _wait_for_state(
        self,
        project_id: str,
        job_id: str,
        success_status: list,
        error_status: list,
    ):
        timeout = time.time() + self.timeout
        while time.time() < timeout:
            history = self._get_history(project_id, job_id)
            if history:
                if history[0]["status"] in success_status:
                    return history[0]
                elif history[0]["status"] in error_status:
                    self.module.fail_json(
                        msg="Failed to reach target status. Status: %s"
                        % history[0]["status"],
                    )
                else:
                    time.sleep(self.delay)
        self.module.fail_json(
            msg="Failed to reach target status. Status: module timeout",
        )

    def _get_history(self, project_id: str, job_id: str):
        return self.query(
            method="GET",
            api=["projects", project_id, "jobs", job_id, "runs"],
            params=dict(sort="-created_at"),
            field="job_runs",
        )


def main():
    module = MLProjectJobRun.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            name=dict(required=False, type="str", aliases=["job"]),
            id=dict(required=False, type="str", aliases=["job_id"]),
            arguments=dict(required=False, type="str"),
            env=dict(required=False, type="dict", aliases=["env_vars"]),
            state=dict(
                required=False,
                type="str",
                default="started",
                choices=["started", "stopped"],
            ),
            wait=dict(required=False, type="bool", default=False),
            delay=dict(required=False, type="int", default=15),
            timeout=dict(required=False, type="int", default=3600),
        ),
        required_one_of=[
            ["project_name", "project_id"],
            ["name", "id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectJobRun(module)

    output = dict(
        changed=result.changed,
        job_run=result.job_run,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

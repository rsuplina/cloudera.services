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
module: ml_project_job
short_description: Create, update, and delete a Cloudera Machine Learning (CML) project job.
description:
  - Create, update, and delete a Cloudera Machine Learning (CML) project job.
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


class MLProjectJob(MLModule):
    def __init__(self, module):
        super(MLProjectJob, self).__init__(module)

        # Set parameters
        self.project_name = self._get_param("project_name")
        self.project_id = self._get_param("project_id")
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.arguments = self._get_param("arguments")
        self.attachments = self._get_param("attachments")
        self.cpu = self._get_param("cpu")
        self.creator = self._get_param("creator")
        self.engine = self._get_param("engine")
        self.env = self._get_param("env")
        self.kernel = self._get_param("kernel")
        self.kill = self._get_param("kill")
        self.memory = self._get_param("memory")
        self.gpu = self._get_param("gpu")
        self.parent = self._get_param("parent")
        self.addons = self._get_param("addons")
        self.runtime = self._get_param("runtime")
        self.schedule = self._get_param("schedule")
        self.script = self._get_param("script")
        self.timeout = self._get_param("timeout")
        self.recipients = self._get_param("recipients")
        self.state = self._get_param("state")

        # Initialize the return values
        self.changed = False
        self.job = {}

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

        existing = None
        if self.id:
            existing = self.get_job(project["id"], self.id)
        else:
            existing = self.find_job(project["id"], self.name)

        if self.state == "present":
            payload = dict()
            # Create and update
            if self.kernel:
                if project["default_engine_type"] == "ml_runtime":
                    self.module.fail_json(
                        msg="Invalid parameter, 'kernel'. Default project engine type is 'ML Runtime'.",
                    )
                payload.update(kernel=self.kernel)
            if self.runtime:
                payload.update(runtime_identifier=self.runtime)
            if self.name:
                payload.update(name=self.name)
            if self.id:
                payload.update(id=self.id)
            if self.arguments:
                payload.update(arguments=self.arguments)
            if self.cpu:
                payload.update(cpu=self.cpu)
            # Needed? if self.engine: payload.update(engine=self.engine)
            if self.kill is not None:
                payload.update(kill_on_timeout=self.kill)
            if self.memory:
                payload.update(memory=self.memory)
            if self.gpu:
                payload.update(nvidia_gpu=self.gpu)
            if self.addons:
                payload.update(runtime_addon_identifiers=self.addons)
            if self.schedule:
                payload.update(schedule=self.schedule)
            if self.script:
                payload.update(script=self.script)
            if self.timeout:
                payload.update(timeout=self.timeout)  # Might be a str for update

            # Update the job
            if existing:
                if self.env:
                    payload.update(
                        env=self.env,
                    )  # As multiple patch calls, one per entry
                if self.parent:
                    payload.update(parent_id=self.parent)
                if self.creator:
                    payload.update(
                        foo=self._get_param("creator", "email"),
                    )  # TODO Unroll suboptions

                # Merge runtime addon identifiers if they exist, giving priority to user-specified addons
                if self.addons:
                    if "runtime_addon_identifiers" in existing:
                        # Merge user addons with existing ones (user addons first)
                        merged_addons = list(self.addons)
                        for addon in existing["runtime_addon_identifiers"]:
                            if addon not in merged_addons:
                                merged_addons.append(addon)
                        # Sort to ensure consistent ordering for comparison
                        payload.update(runtime_addon_identifiers=sorted(merged_addons))
                    else:
                        # No existing addons, just use user-specified (sorted)
                        payload.update(runtime_addon_identifiers=sorted(self.addons))

                diff = difference(payload, existing)
                if diff and not self.module.check_mode:
                    self.changed = True
                    self.job = self.query(
                        method="PATCH",
                        api=["projects", project["id"], "jobs", existing["id"]],
                        body=diff,
                    )
                else:
                    self.job = existing
            # Create the job
            else:
                if self.attachments:
                    payload.update(attachments=self.attachments)
                if self.env:
                    payload.update(env=self.env)  # As a straight dict
                if self.parent:
                    payload.update(parent_job_id=self.parent)
                if not self.runtime and project["default_engine_type"] == "ml_runtime":
                    self.module.fail_json(
                        msg="Missing parameter, 'runtime'. Default project engine type is 'ML Runtime'.",
                    )
                    payload.update(runtime=self.runtime)
                if self.recipients:
                    payload.update(recipients=self.recipients)  # TODO Unroll suboptions
                if not self.module.check_mode:
                    self.changed = True
                    self.job = self.query(
                        method="POST",
                        api=["projects", project["id"], "jobs"],
                        body=payload,
                    )
        elif existing and not self.module.check_mode:
            # Delete the job
            self.changed = True
            self.query(
                method="DELETE",
                api=["projects", project["id"], "jobs", existing["id"]],
            )


def main():
    module = MLProjectJob.ansible_module(
        argument_spec=dict(
            project_name=dict(required=False, type="str"),
            project_id=dict(required=False, type="str"),
            name=dict(required=False, type="str", aliases=["job"]),
            id=dict(required=False, type="str", aliases=["job_id"]),
            arguments=dict(required=False, type="str"),
            attachments=dict(required=False, type="list", elements="str"),
            cpu=dict(required=False, type="int"),  # vCPU
            creator=dict(
                required=False,
                type="dict",
                options=dict(
                    email=dict(required=False, type="str"),
                    name=dict(required=False, type="str"),
                    username=dict(required=False, type="str"),
                ),
            ),
            # Not needed? engine=dict(required=False, type='str', aliases=['image', 'engine_image_id']),
            env=dict(required=False, type="dict", aliases=["env_vars"]),
            kernel=dict(
                required=False,
                type="str",
                choices=["python3", "python2", "r", "scala"],
            ),
            kill=dict(required=False, type="bool", aliases=["kill_on_timeout"]),
            memory=dict(required=False, type="float"),  # GB
            gpu=dict(required=False, type="int", aliases=["nvidia_gpu"]),
            parent=dict(required=False, type="str", aliases=["parent_job_id"]),
            # paused=dict(required=False, type='bool'),
            addons=dict(
                required=False,
                type="list",
                elements="str",
                aliases=["runtime_addon_ids", "runtime_addons"],
            ),
            runtime=dict(required=False, type="str", aliases=["runtime_image_id"]),
            schedule=dict(required=False, type="str"),
            script=dict(required=False, type="str"),
            timeout=dict(required=False, type="int"),
            recipients=dict(
                required=False,
                type="list",
                elements="dict",
                options=dict(
                    email=dict(required=True, type="str"),  # Collaborator
                    success=dict(required=False, type="bool", default=True),
                    failure=dict(required=False, type="bool", default=True),
                    timeout=dict(required=False, type="bool", default=True),
                    stopped=dict(required=False, type="bool", default=True),
                ),
            ),
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
        ),
        mutually_exclusive=[
            ["parent", "schedule"],
            ["kernel", "runtime"],
        ],
        required_by={
            "kill": ["timeout"],
        },
        required_one_of=[
            ["name", "id"],
            ["project_name", "project_id"],
        ],
        supports_check_mode=True,
    )

    result = MLProjectJob(module)

    output = dict(
        changed=result.changed,
        job=result.job,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

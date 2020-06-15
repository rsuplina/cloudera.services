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

import logging
import nipyapi
import os
import requests
import time
from nipyapi import config, canvas, security

from ansible.module_utils.basic import AnsibleModule

logging.basicConfig(level=logging.INFO)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: nifi_flow
short_description: Create, update, and delete NiFi flows
description:
  - Create, update, and delete NiFi flows.
  - Each flow is imported as a Process Group in the NiFi canvas.
  - The module supports check_mode.
author:
  - "Andre Araujo (@asdaraujo)"
version_added: "1.0.0"
requirements:
  - nipyapi
  - requests
options:
  parent_id:
    description:
      - UUID of the parent Process Group for the one being imported/deleted.
      - Mutually exclusive with parent_name.
      - One of parent_id or parent_name is required.
    type: str
    required: False
    default: root
  parent_name:
    description:
      - Name of the parent Process Group for the one being imported/deleted.
      - Mutually exclusive with parent_id.
      - One of parent_id or parent_name is required.
    type: str
    required: False
  pg_id:
    description:
      - UUID of the Process Group being deleted.
      - Only used when state==absent.
      - Mutually exclusive with pg_name.
      - When state==absent, one of pg_id or pg_name is required.
    type: str
    required: False
  pg_name:
    description:
      - Name of the Process Group being imported/deleted.
      - Mutually exclusive with pg_ig.
      - When state==absent, one of pg_id or pg_name is required.
    type: str
    required: False
  x_position:
    description:
      - X coordinate for the Process Group
    aliases: x
    type: float
    required: False
    default: 0.0
  y_position:
    description:
      - Y coordinate for the Process Group
    aliases: y
    type: float
    required: False
    default: 0.0
  flow_definition_file:
    description:
      - JSON file containing the flow definition to be imported.
      - Required if state==present.
    aliases: 'file'
    type: str
    required: False
  parameters:
    description:
      - Values for the parameters defined in the process group's parameter context, if any.
    type: dict
    required: False
  endpoint:
    description:
      - NiFi REST API endpoint.
    aliases: 'url'
    type: str
    required: True
  username:
    description:
      - Username for authentication with the NiFi REST API.
    aliases: 'user'
    type: str
    required: True
  password:
    description:
      - Password for authentication with the NiFi REST API.
    type: str
    required: True
  force_basic_auth:
    description:
      - Forces the use of basic authentication.
    type: bool
    required: False
    default: True
  ssl_ca_cert:
    description:
      - Path of a file containing a TLS root certificate in PEM format.
      - If provided, the certificate will be used to validate NiFi's certificate.
    type: str
    required: False
  state:
    description:
      - The declarative state of the CustomFlow
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
      - running
  debug:
    description:
      - Flag to capture and return the debugging log of the underlying CDP SDK.
      - If set, the log level will be set from ERROR to DEBUG.
    default: False
    type: bool
"""

EXAMPLES = r"""
# Import a NiFi flow
nifi_flow:
    endpoint: https://nifi-example.cloudera.site/nifi-cluster/cdp-proxy-api/nifi-app/nifi-api/
    username: alice
    password: supersecret
    pg_name: My New Flow
    parent_id: root
    flow_definition_file: /path/to/my-flow.json
    parameters:
      param1: value1
      param2: value2
    state: present

# Delete a NiFi flow
nifi_flow:
    endpoint: https://nifi-example.cloudera.site/nifi-cluster/cdp-proxy-api/nifi-app/nifi-api/
    username: alice
    password: supersecret
    pg_name: My New Flow
    state: absent
"""

RETURN = r"""
---
flow:
  description:
    - Returns the ProcessGroupEntity object associated with the imported flow.
    - Check the NiFi API documentation for full details on the ProcessGroupEntity attributes.
  returned: always
  type: dict
  contains:
    id:
      description: UUID of the ProcessGroup that was created by the flow import.
      returned: always
      type: str
"""


def _is_parameter_sensitive(context, name):
    parameters = context.component.parameters
    for p in parameters:
        if p.parameter.name == name:
            return p.parameter.sensitive
    return False


class NiFiFlow(AnsibleModule):
    def __init__(self, module):
        self.module = module

        self.endpoint = self._get_param("endpoint").rstrip(
            "/",
        )  # must not have the trailing slash
        self.username = self._get_param("username")
        self.password = self._get_param("password")
        self.force_basic_auth = self._get_param("force_basic_auth")
        self.ssl_ca_cert = self._get_param("ssl_ca_cert")
        self._init_nifi_config()

        self.parent_id = self._get_param("parent_id")
        self.parent_name = self._get_param("parent_name")
        self.pg_id = self._get_param("pg_id")
        self.pg_name = self._get_param("pg_name")
        self.x_position = "{:.1f}".format(self._get_param("x_position"))
        self.y_position = "{:.1f}".format(self._get_param("y_position"))
        self.flow_definition_file = self._get_param("flow_definition_file")
        self.parameters = self._get_param("parameters")

        self.state = self._get_param("state")

        self.logger = logging.getLogger("ranger_module")
        if self._get_param("debug"):
            self.logger.setLevel(logging.DEBUG)

        # Initialize the return values
        self.flow = {}
        self.changed = False

    def _get_param(self, param, default=None):
        """Fetches an Ansible Input Parameter if it exists, else returns optional default or None"""
        if self.module is not None and self.module.params is not None:
            return self.module.params.get(param, default)
        return default

    def _get_parent_pg(self):
        return self._get_pg(self.parent_name, self.parent_id, ignore_missing=False)

    def _get_pg(self, pg_name=None, pg_id=None, ignore_missing=True):
        if not pg_name and not pg_id:
            pg_name = self.pg_name
            pg_id = self.pg_id
        pgs = None
        try:
            if pg_name:
                pgs = canvas.get_process_group(
                    pg_name,
                    identifier_type="name",
                    greedy=False,
                )
            else:
                pgs = canvas.get_process_group(
                    pg_id,
                    identifier_type="id",
                    greedy=False,
                )
        except ValueError:
            pass

        if not pgs:
            if ignore_missing:
                return None
            self.module.fail_json(
                msg="Process group [{}] not found.".format(pg_name or pg_id),
            )
        elif isinstance(pgs, list):
            if len(pgs) > 1:
                self.module.fail_json(
                    msg="More than one process group matched the process group name [{}].".format(
                        pg_name or pg_id,
                    ),
                )
            pgs = pgs[0]
        return pgs

    def _init_nifi_config(self):
        config.nifi_config.host = self.endpoint
        config.nifi_config.force_basic_auth = self.force_basic_auth
        security.service_login(
            service="nifi",
            username=self.username,
            password=self.password,
        )
        if self.ssl_ca_cert:
            security.set_service_ssl_context(service="nifi", ca_file=self.ssl_ca_cert)

    def _upload_flow(self, parent_pg):
        url = "{}/process-groups/{}/process-groups/upload".format(
            self.endpoint,
            parent_pg.id,
        )
        resp = requests.post(
            url,
            auth=(self.username, self.password),
            data={
                "groupName": self.pg_name,
                "positionX": self.x_position,
                "positionY": self.y_position,
                "clientId": nipyapi.nifi.FlowApi().generate_client_id(),
            },
            files={
                "file": (
                    os.path.basename(self.flow_definition_file),
                    open(self.flow_definition_file, "r"),
                    "application/json",
                ),
            },
        )
        if resp.status_code != requests.codes.created:
            self.module.fail_json(
                msg="Failed to upload flow. Error code: {}. Output: {}".format(
                    resp.status_code,
                    resp.text,
                ),
            )
        self.flow = resp.json()

    def _get_controller_services(self, pg_id=None):
        if pg_id is None:
            pg_id = self.flow["id"]
        try:
            with nipyapi.utils.rest_exceptions():
                result = nipyapi.nifi.FlowApi().get_controller_services_from_group(
                    id=pg_id,
                    include_ancestor_groups=False,
                    include_descendant_groups=True,
                )
        except Exception as exc:
            self.module.fail_json(
                msg="Failed to retrieve controller services for process group {}."
                " Exception: {}".format(pg_id, exc),
            )
        return result.controller_services

    def _activate_controller_services(self, pg_id=None, enabled=True, timeout_secs=180):
        if pg_id is None:
            pg_id = self.flow["id"]
        target_state = "ENABLED" if enabled else "DISABLED"
        body = nipyapi.nifi.ActivateControllerServicesEntity(
            id=pg_id,
            state=target_state,
        )
        try:
            with nipyapi.utils.rest_exceptions():
                result = nipyapi.nifi.FlowApi().activate_controller_services(
                    id=pg_id,
                    body=body,
                )
                if result.state != target_state:
                    raise RuntimeError(
                        "Result state ({}) differs from target state ({}).".format(
                            result.state,
                            target_state,
                        ),
                    )
                start_time = time.time()
                while time.time() < start_time + timeout_secs:
                    controllers = self._get_controller_services(pg_id)
                    pending = []
                    for controller in controllers:
                        if controller.status.run_status != target_state:
                            pending.append(controller)
                    if not pending:
                        return
                    invalid = [
                        "{} ({})".format(c.component.name, c.component.type)
                        for c in pending
                        if c.status.validation_status == "INVALID"
                    ]
                    if invalid:
                        raise RuntimeError(
                            "The following controller services are invalid and"
                            " cannot be enabled: {}".format(", ".join(invalid)),
                        )
                raise RuntimeError("Parameter context update has timed out.")

        except Exception as exc:
            self.module.fail_json(
                msg="Failed to {} controller services. Exception: {}.".format(
                    "enable" if enabled else "disable",
                    exc,
                ),
            )

    def _empty_all_queues(self, pg_id=None):
        if pg_id is None:
            pg_id = self.flow["id"]
        try:
            with nipyapi.utils.rest_exceptions():
                nipyapi.nifi.ProcessGroupsApi().create_empty_all_connections_request(
                    id=pg_id,
                )
        except Exception as exc:
            self.module.fail_json(
                msg="Failed to empty queues. Exception: {}.".format(exc),
            )

    def _get_parameter_context(self):
        parameter_context = self.flow.get("parameterContext", None)
        if not parameter_context:
            return None
        context_id = parameter_context["id"]
        try:
            with nipyapi.utils.rest_exceptions():
                result = nipyapi.nifi.ParameterContextsApi().get_parameter_context(
                    id=context_id,
                )
        except Exception as exc:
            self.module.fail_json(
                msg="Failed to retrieve parameter context {}. Exception: {}".format(
                    context_id,
                    exc,
                ),
            )
        return result

    def _get_parameter_context_update(self, context_id, request_id):
        try:
            with nipyapi.utils.rest_exceptions():
                result = (
                    nipyapi.nifi.ParameterContextsApi().get_parameter_context_update(
                        context_id=context_id,
                        request_id=request_id,
                    )
                )
        except Exception as exc:
            self.module.fail_json(
                msg="Failed to retrieve parameter context update (context_id={}, request_id={})."
                " Exception: {}".format(context_id, request_id, exc),
            )
        return result

    def _update_parameter_context(self, timeout_secs=180):
        if not self.parameters:
            return
        context = self._get_parameter_context()
        if not context:
            return
        body = nipyapi.nifi.ParameterContextEntity(
            id=context.id,
            revision=context.revision,
            component=nipyapi.nifi.ParameterContextDTO(
                id=context.id,
                parameters=[
                    nipyapi.nifi.ParameterEntity(
                        parameter=nipyapi.nifi.ParameterDTO(
                            name=name,
                            value=value,
                            sensitive=_is_parameter_sensitive(context, name),
                        ),
                    )
                    for name, value in self.parameters.items()
                ],
            ),
        )
        try:
            with nipyapi.utils.rest_exceptions():
                result = (
                    nipyapi.nifi.ParameterContextsApi().submit_parameter_context_update(
                        context_id=context.id,
                        body=body,
                    )
                )
                start_time = time.time()
                while time.time() < start_time + timeout_secs:
                    update_state = self._get_parameter_context_update(
                        context.id,
                        result.request.request_id,
                    )
                    if update_state.request.complete:
                        if update_state.request.state == "Complete":
                            return
                        else:
                            raise RuntimeError(
                                "Parameter context update failed with reason: {}.".format(
                                    update_state.request.failure_reason,
                                ),
                            )
                raise RuntimeError("Parameter context update has timed out.")
        except Exception as exc:
            self.module.fail_json(
                msg="Failed to update parameter context {}. Exception: {}".format(
                    context.id,
                    exc,
                ),
            )

    def _delete_process_group(self, pg):
        canvas.schedule_process_group(pg.id, False)
        self._activate_controller_services(pg.id, False)
        self._empty_all_queues(pg.id)
        canvas.delete_process_group(pg)

    def process(self):
        if self.state in ["present", "running"]:
            self.changed = True
            if not self.module.check_mode:
                existing_pg = self._get_pg()
                parent_pg = self._get_parent_pg()
                if existing_pg:
                    self._delete_process_group(existing_pg)
                self._upload_flow(parent_pg)
                self._update_parameter_context()
                if self.state == "running":
                    self._activate_controller_services()
                    canvas.schedule_process_group(self.flow["id"], True)
        elif self.state == "absent":
            existing_pg = self._get_pg()
            if existing_pg:
                self.changed = True
                if not self.module.check_mode:
                    self._delete_process_group(existing_pg)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent", "running"],
                default="present",
            ),
            parent_id=dict(required=False, type="str", default="root"),
            parent_name=dict(required=False, type="str"),
            pg_id=dict(required=False, type="str"),
            pg_name=dict(required=False, type="str"),
            x_position=dict(required=False, type="float", default=0.0, aliases=["x"]),
            y_position=dict(required=False, type="float", default=0.0, aliases=["y"]),
            flow_definition_file=dict(required=False, type="str", aliases=["file"]),
            parameters=dict(required=False, type="dict"),
            endpoint=dict(required=True, type="str", aliases=["url"]),
            username=dict(required=True, type="str", aliases=["user"]),
            password=dict(required=True, type="str", no_log=True),
            force_basic_auth=dict(required=False, type="bool", default=True),
            ssl_ca_cert=dict(required=False, type="str"),
            debug=dict(required=False, type="bool", default=False),
        ),
        required_if=[
            ("state", "present", ("pg_name", "flow_definition_file")),
            ("state", "absent", ("pg_name", "pg_id"), True),
        ],
        mutually_exclusive=[
            ("parent_name", "parent_id"),
            ("pg_name", "pg_id"),
        ],
        supports_check_mode=True,
    )

    result = NiFiFlow(module)
    result.process()

    output = dict(
        changed=result.changed,
        flow=result.flow,
    )

    # if result.debug:
    #     output.update(
    #        sdk_out=result.log_out,
    #        sdk_out_lines=result.log_lines
    #     )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

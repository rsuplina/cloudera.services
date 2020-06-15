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

from ansible_collections.cloudera.services.plugins.module_utils.cdp_rest import (
    CdpRestResponse,
)
from ansible_collections.cloudera.services.plugins.module_utils.cdp_efm import (
    CdpEfmModule,
    CdpEfmFlowModule,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: efm_designer_flow
short_description: Create, delete, and publish EFM agent class flows
description:
    - Create, delete, and publish Cloudera Edge Flow Manager designer flows for agent classes.
    - Optionally, set flow parameters.
author:
    - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
    - requests
options:
    id:
        description:
            - Identifier of the EFM flow.
            - Mutually exclusive with I(agent_class).
        type: str
        aliases:
            - flow_id
    agent_class:
        description:
            - Name of the agent class associated with the EFM flow.
            - Mutually exclusive with I(id).
            - Required if I(content) is defined.
        type: str
        aliases:
            - agent_class_name
    comment:
        description:
            - Text to include if publishing the EFM flow.
            - Valid only is I(state=published); ignored otherwise.
        type: str
    content:
        description:
            - Content of the EFM flow.
            - Required if I(state=present).
        type: dict
        aliases:
            - flow_body
            - body
    parameters:
        description:
            - Values set on the EFM flow.
        type: dict
        aliases:
            - parameter_context
    force:
        description:
            - Flag to skip EFM flow validation when I(state=published).
        type: bool
        default: False
        aliases:
            - skip_validation
    state:
        description:
            - State of the EFM flow.
            - C(present) sets the flow, but does not push the flow to the agents or validate the flow.
            - C(published) will push the flow to the agents and will validate the flow unless I(validate=no).
extends_documentation_fragment:
    - cloudera.services.cdp_rest
"""

EXAMPLES = r"""
# These examples do not include authentication.
- name: Set a flow for an agent class from a file
  cloudera.services.efm_designer_flow:
    endpoint: "{{ efm_endpoint }}"
    state: present
    agent_class: example_group
    content: "{{ lookup('ansible.builtin.file', 'available_flow_file.json') }}"

- name: Set a flow with inline parameters and content
  cloudera.services.efm_designer_flow:
    endpoint: "{{ efm_endpoint }}"
    state: present
    agent_class: example_group
    content:
        flowContent:
            identifier: "7586bcd3-dc03-4bef-99de-9276ab9ecbc6"
            instanceIdentifier: "d80ad3c3-7b24-4a89-b252-d9ecf4387332"
            name: "root"
            position:
                x: 0
                y: 0
            processGroups: []
            remoteProcessGroups: []
            processors: []
            inputPorts: []
            outputPorts: []
            connections: []
            labels: []
            funnels: []
            controllerServices: []
            variables: {}
            parameterContextName: "9f4988b8-6f14-46da-b636-683b09d543f3"
            componentType: "PROCESS_GROUP"
        parameterContexts:
          - id: "9f4988b8-6f14-46da-b636-683b09d543f3"
            name": "9f4988b8-6f14-46da-b636-683b09d543f3"
            parameters:
              - name: "param0"
                sensitive: false
                description: "Example parameter"
                value: "value0"
    parameters:
        some_param: some_value
        param0: "Inline value"

- name: Publish a flow without validating and using the flow_id
  cloudera.services.efm_designer_flow:
    endpoint: "{{ efm_endpoint }}"
    state: publish
    id: 9f4988b8-ffff-aaaa-b636-683b09d543f3
    force: yes

- name: Set and publish a flow using the agent_class and an exported flow file
  cloudera.services.efm_designer_flow:
    endpoint: "{{ efm_endpoint }}"
    state: published
    agent_class: example_group
    content: "{{ lookup('ansible.builtin.file', 'available_flow_file.json') }}"
    parameters:
        param0: "Inline value"
        another_parameter: 1234

- name: Clear (delete) a flow from the agent class
  cloudera.services.efm_designer_flow:
    endpoint: "{{ efm_endpoint }}"
    state: absent
    agent_class: example_group
"""

RETURN = r"""
---
flow:
    description: Details for the EFM flow.
    returned: when supported
    type: dict
    contains:
        flowMetadata:
            description: Details on the EFM flow entity
            returned: always
            type: dict
            contains:
                agentClass:
                    description: Name of the agent class associated with the EFM flow
                    returned: always
                    type: str
                created:
                    description: Creation timestamp (epoch)
                    returned: always
                    type: int
                    sample: 1683746019934
                identifier:
                    description: UUID for the EFM flow
                    returned: always
                    type: str
                    sample: "d86b1297-fbe3-49f5-b97d-5a8cd7c999b6"
                rootProcessGroupIdentifier:
                    description: UID for the EFM root process group
                    returned: always
                    type: str
                    sample: "c85836a0-a040-479c-ac07-22efd3c2d555"
                updated:
                    description: Updated timestamp (epoch)
                    returned: when supported
                    type: int
                    sample: 1683746019934
        localFlowRevision:
            description: Identifier for the flow revision
            returned: always
            type: int
        versionInfo:
            description: Details on the publishing lifecycle of the EFM flow
            returned: when supported
            type: dict
            contains:
                dirty:
                    description: Flag indicating if the current flow has been changed since last published
                    returned: always
                    type: bool
                flowVersion:
                    description: Latest published flow version
                    returned: always
                    type: int
                lastPublished:
                    description: Publish timestamp (epoch)
                    returned: always
                    type: int
                    sample: 1683746463910
                lastPublishedBy:
                    description: Username of the publisher
                    returned: always
                    type: str
        flowContent:
            description: Details for the EFM flow
            returned: always
            type: dict
            contains:
                componentType:
                    description: Category of component
                    returned: always
                    type: str
                    sample: "PROCESS_GROUP"
                connections:
                    description: List of connections defined within the flow
                    returned: always
                    type: list
                    elements: complex
                controllerServices:
                    description: List of services defined within the flow
                    returned: always
                    type: list
                    elements: complex
                funnels:
                    description: List of funnels defined within the flow
                    returned: always
                    type: list
                    elements: complex
                identifier:
                    description: UUID of the flow content
                    returned: always
                    type: str
                    sample: "c85836a0-a040-479c-ac07-22efd3c2d555"
                inputPorts:
                    description: List of input ports defined within the flow
                    returned: always
                    type: list
                    elements: complex
                instanceIdentifier:
                    description: UUID of the flow's instance
                    returned: always
                    type: str
                    sample: "dc11b253-7656-4a88-aeef-bf4c5054334e"
                labels:
                    description: List of labels defined within the flow
                    returned: always
                    type: list
                    elements: complex
                name:
                    description: Name for the flow content
                    returned: always
                    type: str
                outputPorts:
                    description: List of output ports defined within the flow
                    returned: always
                    type: list
                    elements: complex
                parameterContextName:
                    description: UUID of the parameter context defined for the flow
                    returned: always
                    type: str
                    sample: "e9b47eb6-5c4c-4d28-a7b8-9b7f866a3676"
                position:
                    description: Coordinates for the flow content on the canvas
                    returned: always
                    type: dict
                    contains:
                        x:
                            description: The x-axis position
                            returned: always
                            type: float
                        y:
                            description: The y-axis position
                            returned: always
                            type: float
                processGroups:
                    description: List of process groups defined within the flow
                    returned: always
                    type: list
                    elements: complex
                processors:
                    description: List of processors defined within the flow
                    returned: always
                    type: list
                    elements: complex
                remoteProcessGroups:
                    description: List of remote process groups defined within the flow
                    returned: always
                    type: list
                    elements: complex
                variables:
                    description:
                        - Variables in the variable registry for the process group
                        - Does not include any ancestor or descendant process groups
                    returned: always
                    type: dict
        parameterContexts:
            description: Set of parameters associated with the EFM flow
            returned: always
            type: list
            elements: dict
            contains:
                id:
                    description: UUID of the parameter context
                    returned: always
                    type: str
                    sample: "e9b47eb6-5c4c-4d28-a7b8-9b7f866a3676"
                name:
                    description: Name of the parameter context
                    returned: always
                    type: str
                parameters:
                    description: List of parameters defined in the parameter context
                    returned: always
                    type: list
                    elements: dict
                    contains:
                        name:
                            description: Name of the parameter
                            returned: always
                            type: str
                        description:
                            description: Description of the parameter
                            returned: when supported
                            type: str
                        sensitive:
                            description: Flag indicating if the parameter contains sensitive information
                            returned: always
                            type: bool
                        value:
                            description: Value of the parameter
                            returned: always
                            type: raw
sdk_out:
    description: Returns the captured CDP REST API log.
    returned: when supported
    type: str
sdk_out_lines:
    description: Returns a list of each line of the captured CDP REST API log.
    returned: when supported
    type: list
    elements: str
"""


class CdpEfmDesignerFlow(CdpEfmModule):
    def __init__(self, module):
        super(CdpEfmDesignerFlow, self).__init__(
            module,
            "cloudera.services.efm_designer_flow",
        )

        self.flow_id = self._get_param("id")
        self.agent_class = self._get_param("agent_class")
        self.flow_body = self._get_param("content")
        self.parameters = self._get_param("parameters")
        self.comments = self._get_param("comments")
        self.force = self._get_param("force")
        self.state = self._get_param("state")

        # Initialize the return values
        self.changed = False
        self.flow = {}

    @CdpEfmFlowModule.process_debug
    def process(self):
        existing = None

        if self.flow_id:
            existing = self._get_designer_flow(self.flow_id)
            if not existing:
                self.module.fail_json(
                    msg="Flow identifier, '%s', not found" % self.flow_id,
                )
        else:
            flow_list = [
                f
                for f in self._get_designer_flows()
                if f["agentClass"] == self.agent_class
            ]
            if len(flow_list) == 1:
                existing = self._get_designer_flow(flow_list[0]["identifier"])
            elif len(flow_list) > 1:
                self.module.fail_json(
                    msg="Multiple flows found for agent class, %s" % self.agent_class,
                )

        if self.state == "absent":
            self.changed = True
            if not self.module.check_mode:
                self.process_response(
                    self._isolated_request(
                        "DELETE",
                        "/efm/api/designer/flows/%s"
                        % existing["flowMetadata"]["identifier"],
                    ),
                    [
                        CdpRestResponse(CdpRestResponse.STATUS_CODES.ok),
                        CdpRestResponse(
                            CdpRestResponse.STATUS_CODES.not_found,
                            return_value={},
                        ),
                    ],
                    "Failed to delete flow for agent class '%s'."
                    % existing["flowMetadata"]["agentClass"],
                )
        elif self.state == "present":
            self.changed = True

            if not self.module.check_mode:
                updated = self._import_flow(self.agent_class, self.flow_body)
                self.flow = self._get_designer_flow(updated["identifier"])

                if self.parameters:
                    self._set_flow_parameters(
                        self.parameters,
                        self.flow["flowMetadata"]["agentClass"],
                        self.flow["parameterContexts"][0]["id"],
                    )
                    self.flow = self._get_designer_flow(updated["identifier"])

        elif self.state == "published":
            if self.flow_body:
                self.changed = True
                if not self.module.check_mode:
                    updated = self._import_flow(self.agent_class, self.flow_body)
                    existing = self._get_designer_flow(updated["identifier"])

            if self.parameters:
                self.changed = True
                if not self.module.check_mode:
                    self._set_flow_parameters(
                        self.parameters,
                        existing["flowMetadata"]["agentClass"],
                        existing["parameterContexts"][0]["id"],
                    )

            if (
                self.changed
                or "versionInfo" not in existing
                or existing["versionInfo"]["dirty"]
            ):
                self.changed = True
                if not self.module.check_mode:
                    body = dict()
                    if self.comments:
                        body.update(comments=self.comments)

                    params = dict()
                    if self.force:
                        params.update(forcePublish=str(self.force).lower())

                    self.process_response(
                        self._isolated_request(
                            "POST",
                            "/efm/api/designer/flows/%s/publish"
                            % existing["flowMetadata"]["identifier"],
                            params=params,
                            json=body,
                        ),
                        [
                            CdpRestResponse(self.status_codes.ok),
                        ],
                        "Failed to publish flow for agent class '%s'."
                        % existing["flowMetadata"]["agentClass"],
                    )
                self.flow = self._get_designer_flow(
                    existing["flowMetadata"]["identifier"],
                )
        else:
            self.module.fail_json(
                msg="State, '%s', is not yet implemented" % self.state,
            )

    def _import_flow(self, agent_class: str, flow_body: dict):
        return self.process_response(
            self._isolated_request(
                "POST",
                "/efm/api/designer/%s/flows/import" % agent_class,
                json=flow_body,
            ),
            [CdpRestResponse(self.status_codes.ok)],
            "Failed to import flow for agent class '%s'." % agent_class,
        )

    def _set_flow_parameters(self, parameters: dict, agent_class: str, context_id: str):
        payload = [dict(name=k, value=v) for k, v in parameters.items()]
        return self.process_response(
            self._isolated_request(
                "PUT",
                "/efm/api/designer/parameter-contexts/%s" % context_id,
                json=dict(parameters=payload),
            ),
            [CdpRestResponse(self.status_codes.ok)],
            "Failed to update flow parameters for agent class '%s'." % agent_class,
        )


def main():
    module = AnsibleModule(
        **CdpEfmDesignerFlow.module_spec(
            argument_spec=dict(
                comments=dict(type="str"),
                id=dict(type="str", aliases=["flow", "flow_id"]),
                agent_class=dict(type="str", aliases=["agent_class_name"]),
                content=dict(type="dict", aliases=["flow_body", "body"]),
                parameters=dict(type="dict", aliases=["parameter_context"]),
                force=dict(type="bool", default=False, aliases=["skip_validation"]),
                state=dict(
                    type="str",
                    default="present",
                    choices=["present", "absent", "reverted", "published"],
                ),
            ),
            required_one_of=[
                ["id", "agent_class"],
            ],
            required_if=[
                ["state", "present", ["content"]],
            ],
            required_by={
                "content": "agent_class",
            },
            supports_check_mode=True,
        ),
    )

    result = CdpEfmDesignerFlow(module)
    result.process()

    output = dict(
        changed=result.changed,
        flow=result.flow,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

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

"""
Ansible Modules for shared functions of the Cloudera Edge Flow Manager (EFM) service
"""

from typing import Any

from ansible_collections.cloudera.services.plugins.module_utils.cdp_rest import (
    CdpRestModule,
    CdpRestResponse,
)

__maintainer__ = [
    "wmudge@cloudera.com",
]


class CdpEfmModule(CdpRestModule):
    """A base CDP module class for dealing with Cloudera Edge Flow Manager (EFM) REST APIs."""

    def __init__(self, module, name="efm") -> None:
        super(CdpEfmModule, self).__init__(module, name)

    def _get_designer_flow(self, id: str) -> Any:
        return self.process_response(
            self._get("/efm/api/designer/flows/%s" % id),
            [
                CdpRestResponse(self.status_codes.ok),
                CdpRestResponse(self.status_codes.not_found, return_value={}),
            ],
            'Failed to retrieve designer flow "%s".' % id,
        )

    def _get_designer_flows(self) -> Any:
        return self.process_response(
            self._get("/efm/api/designer/flows"),
            [CdpRestResponse(self.status_codes.ok, extract_field="elements")],
            "Failed to retrieve designer flows.",
        )

    def _get_agent_class(self, name: str) -> Any:
        return self.process_response(
            self._get("/efm/api/agent-classes/%s" % name),
            [
                CdpRestResponse(self.status_codes.ok),
                CdpRestResponse(self.status_codes.not_found, return_value={}),
            ],
            'Failed to retrieve agent class "%s".' % name,
        )

    def _get_agent_classes(self) -> Any:
        return self.process_response(
            self._get("/efm/api/agent-classes"),
            [CdpRestResponse(self.status_codes.ok)],
            "Failed to retrieve agent classes.",
        )


class CdpEfmFlowModule(CdpEfmModule):
    """A base CDP module class for Flow-specific functions with Cloudera Edge Flow Manager (EFM) REST APIs."""

    def __init__(self, module, name="efm-flow") -> None:
        super(CdpEfmFlowModule, self).__init__(module, name)

        self.flow_id = self._get_param("flow_id")

    @staticmethod
    def module_spec(**spec) -> dict:
        """Ansible Module spec values for Flow-specific modules"""
        return CdpEfmFlowModule.merge_specs(
            super(CdpEfmFlowModule, CdpEfmFlowModule).module_spec(),
            dict(
                argument_spec=dict(
                    flow_id=dict(
                        required=True,
                        type="str",
                        aliases=["flow", "flow_name"],
                    ),
                ),
            ),
            spec,
        )

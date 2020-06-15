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
Ansible Modules for shared functions of the Cloudera Streams Messaging Manager (SMM) service
"""

from typing import Any

from ansible_collections.cloudera.services.plugins.module_utils.cdp_rest import (
    CdpRestModule,
    CdpRestResponse,
)

__credits__ = ["araujo@cloudera.com"]
__maintainer__ = [
    "wmudge@cloudera.com",
]


class CdpSmmModule(CdpRestModule):
    """A base CDP module class for handling Cloudera Streams Messaging Manager (SMM) REST APIs."""

    def __init__(self, module, name="smm"):
        super(CdpSmmModule, self).__init__(module, name)

    # Not needed, as SMM modules share basic REST specs only
    # @staticmethod
    # def module_spec(**spec):
    #     """Ansible Module spec values for SMM-specific modules"""
    #     return CdpSmmModule.merge_specs(
    #         super(CdpSmmModule).module_spec(),
    #         dict(
    #             argument_spec=dict()
    #         ),
    #         spec
    #     )

    def _get_topics(self) -> Any:
        return self.process_response(
            self._get("/api/v1/admin/topics"),
            [CdpRestResponse(self.status_codes.ok)],
            "Failed to retrieve topics.",
        )

    def _get_topic(self, name: str) -> Any:
        topic = self.process_response(
            self._get("/api/v1/admin/topics/%s" % name),
            [
                CdpRestResponse(self.status_codes.ok),
                CdpRestResponse(self.status_codes.not_found, return_value=dict()),
            ],
            "Failed to retrieve topic '%s'" % name,
        )

        if topic:
            configs = {
                config["name"]: config["value"]
                for config in self.process_response(
                    self._get("/api/v1/admin/configs/topics/%s" % name),
                    [
                        CdpRestResponse(
                            self.status_codes.ok,
                            extract_field="resourceConfigs",
                        ),
                        CdpRestResponse(
                            self.status_codes.not_found,
                            return_value=dict(),
                        ),
                    ],
                    "Failed to retrieve configs for topic '%s'" % name,
                )
            }
            topic.update(configs=configs)

        return topic

    def _get_topic_default_config(self) -> Any:
        return self.process_response(
            self._get("/api/v1/admin/configs/default/topics"),
            [CdpRestResponse(self.status_codes.ok)],
            "Failed to retrieve default topic config",
        )


KAFKA_TOPIC_PARTITION_RETURN = r"""
partition:
    description: Partition identifier
    returned: always
    type: int
leader:
    description: Partition leader
    returned: always
    type: dict
    contains:
        host:
            description: Hostname for the leader broker
            returned: always
            type: str
        id:
            description: Broker identifier
            returned: always
            type: int
        isController:
            description: Flag indicating whether the broker is a controller
            returned: always
            type: bool
        port:
            description: Broker port
            returned: always
            type: int
        rack:
            description: Rack identifier for the broker host
            returned: when supported
            type: str
replicas:
    description: List of replica partitions
    returned: always
    type: list
    elements: dict
    contains:
        host:
            description: Hostname for the replica broker
            returned: always
            type: str
        id:
            description: Broker identifier
            returned: always
            type: int
        isController:
            description: Flag indicating whether the broker is a controller
            returned: always
            type: bool
        port:
            description: Broker port
            returned: always
            type: int
        rack:
            description: Rack identifier for the broker host
            returned: when supported
            type: str
isr:
    description: List of ISRs
    returned: always
    type: list
    elements: dict
    contains:
        host:
            description: Hostname for the ISR broker
            returned: always
            type: str
        id:
            description: Broker identifier
            returned: always
            type: int
        isController:
            description: Flag indicating whether the broker is a controller
            returned: always
            type: bool
        port:
            description: Broker port
            returned: always
            type: int
        rack:
            description: Rack identifier for the broker host
            returned: when supported
            type: str
"""

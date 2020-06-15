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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: smm_kafka_topic_info
short_description: Get details on Kafka topics
description:
  - Get the details for Kafka topics in Cloudera Streams Messaging Manager (SMM).
  - The module supports I(check_mode).
author:
  - "Andre Araujo (@asdaraujo)"
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  name:
    description:
      - Name of the Kafka topic
    required: False
    type: str
    aliases:
      - topic
extends_documentation_fragment:
  - cloudera.services.cdp_rest
"""

EXAMPLES = r"""
- name: Get the details for a named Kafka topic
  cloudera.services.smm_kafka_topic_info:
    endpoint: https://kafka.cloudera.site/kafka-cluster/cdp-proxy-api/smm-api/
    username: alice
    password: supersecret
    name: topic1

- name: Get details for all Kafka topics
  cloudera.services.smm_kafka_topic_info:
    endpoint: https://kafka.cloudera.site/kafka-cluster/cdp-proxy-api/smm-api/
    username: alice
    password: supersecret
"""

RETURN = r"""
---
topics:
    description: List of Kafka topics
    returned: always
    type: list
    elements: dict
    contains:
        configs:
            description: Dictionary of configuration parameters set on the topic
            returned: always
            type: dict
        internal:
            description: Flag indicating the Kafka topic is an internal resource
            returned: always
            type: bool
        name:
            description: Name of the Kafka topic
            returned: always
            type: str
        partitions:
            description: List of partitions of the Kafka topic
            returned: always
            type: list
            elements: dict
            contains:
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


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cloudera.services.plugins.module_utils.cdp_smm import (
    CdpSmmModule,
)
from ansible_collections.cloudera.services.plugins.module_utils.common import get_param


class SmmKafkaTopic(CdpSmmModule):
    def __init__(self, module):
        super(SmmKafkaTopic, self).__init__(
            module,
            "cloudera.services.smm_kafka_topic_info",
        )

        # Retrieve the module-specific parameters
        self.name = get_param(module, "name")

        # Initialize the return value
        self.topics = []

    @CdpSmmModule.process_debug
    def process(self):
        if self.name:
            topic = self._get_topic(self.name)
            if topic:
                self.topics.append(topic)
        else:
            self.topics = self._get_topics()


def main():
    module = AnsibleModule(
        **CdpSmmModule.module_spec(
            argument_spec=dict(
                name=dict(aliases=["topic"]),
            ),
            supports_check_mode=True,
        ),
    )

    result = SmmKafkaTopic(module)
    result.process()

    output = dict(changed=result.changed, topics=result.topics)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

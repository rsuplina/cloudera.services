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
module: smm_kafka_topic
short_description: Create and delete Kafka topics
description:
  - Create and delete Kafka topics in Cloudera Streams Messaging Manager (SMM).
  - The module supports I(check_mode).
author:
  - "Andre Araujo (@asdaraujo)"
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - requests
options:
  endpoint:
    description:
      - The Streams Messaging Manager (SMM) REST API endpoint.
    required: True
    type: str
    aliases:
      - url
  username:
    description:
      - Username for authentication with the REST API.
    required: True
    type: str
    aliases:
      - user
  password:
    description:
      - Password for authentication with the REST API.
    required: True
    type: str
  ssl_ca_cert:
    description:
      - Path of a file containing a TLS root certificate in PEM format.
      - If provided, the certificate will be used to validate SMM's certificate.
    required: False
    type: str
  name:
    description:
      - Name of the Kafka topic
    required: True
    type: str
    aliases:
      - topic
  num_partitions:
    description:
      - Number of partitions for the Kafka topic.
      - Only used for topic creation and ignored otherwise.
      - Required if I(state=present).
    required: False
    type: int
    default: 1
    aliases:
      - partitions
  replication_factor:
    description:
      - Replication factor for the Kafka topic.
      - Only used for topic creation and ignored otherwise.
      - Required if I(state=present).
    required: False
    type: int
    default: 3
    aliases:
      - replication
  reset:
    description:
      - Flag to reset any undeclared I(config) settings to the default settings for a topic.
    required: False
    type: bool
    default: False
    aliases:
      - reset_configs
  configs:
    description:
      - Properties set for the Kafka topic.
    required: False
    type: dict
    aliases:
      - config
      - configuration
  state:
    description:
      - The declarative state of Kafka topic
    type: str
    required: False
    default: present
    choices:
      - present
      - absent
  debug:
    description:
      - Flag to capture and return the debugging log of the underlying CDP SDK.
      - If set, the log level will be set from ERROR to DEBUG.
    default: False
    type: bool
"""

EXAMPLES = r"""
- name: Create a Kafka topic with default partitions and replicas
  cloudera.services.smm_kafka_topic:
    endpoint: https://kafka.cloudera.site/kafka-cluster/cdp-proxy-api/smm-api/
    username: alice
    password: supersecret
    name: topic1
    configs:
      cleanup.policy: delete

- name: Create a Kafka topic with replica assignments
  cloudera.services.smm_kafka_topic:
    endpoint: https://kafka.cloudera.site/kafka-cluster/cdp-proxy-api/smm-api/
    username: alice
    password: supersecret
    name: topic2
    num_partitions: 2
    replication_factor: 3
    configs:
      cleanup.policy: compact

- name: Reset the configuration for a Kafka topic
  cloudera.services.smm_kafka_topic:
    endpoint: https://kafka.cloudera.site/kafka-cluster/cdp-proxy-api/smm-api/
    username: alice
    password: supersecret
    name: topic3
    reset: yes
    configs:
      cleanup.policy: delete
"""

RETURN = r"""
---
topic:
    description: The Kafka topic in CDP Streams Messaging Manager
    returned: always
    type: dict
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
    CdpRestResponse,
)
from ansible_collections.cloudera.services.plugins.module_utils.common import get_param


class SmmKafkaTopic(CdpSmmModule):
    def __init__(self, module):
        super(SmmKafkaTopic, self).__init__(module, "cloudera.services.smm_kafka_topic")

        self.name = get_param(self.module, "name")
        self.num_partitions = get_param(self.module, "num_partitions")
        self.replication_factor = get_param(self.module, "replication_factor")
        self.configs = get_param(self.module, "configs")
        self.reset = get_param(self.module, "reset")
        self.state = get_param(self.module, "state")

        # Initialize the return values
        self.changed = False
        self.topic = {}

    @CdpSmmModule.process_debug
    def process(self):
        existing = self._get_topic(self.name)

        if self.state == "present":
            if existing:
                # Check the topic configs
                update_config = {}

                for incoming in self.configs:
                    if incoming in existing["configs"]:
                        if existing["configs"][incoming] != str(self.configs[incoming]):
                            self.changed = True
                            del existing["configs"][incoming]
                            update_config[incoming] = self.configs[incoming]
                    else:
                        self.changed = True
                        update_config[incoming] = self.configs[incoming]

                if not self.reset:
                    default_config = self._get_topic_default_config()
                    for e in existing["configs"]:
                        if (
                            e in default_config
                            and existing["configs"][e] != default_config[e]
                        ):
                            self.changed = True
                            update_config[e] = default_config[e]

                # Check the topic partitions
                update_partitions = False

                if self.num_partitions:
                    if len(existing["partitions"]) > self.num_partitions:
                        self.module.fail_json(
                            "Unable to reduce the number of partitions for topic '%s'. You may only increase the number of partitions"
                            % self.name,
                        )
                    elif len(existing["partitions"]) < self.num_partitions:
                        self.changed = True
                        update_partitions = True

                # Check the topic replication factor
                if self.replication_factor:
                    if True in (
                        len(part["replicas"]) != self.replication_factor
                        for part in existing["partitions"]
                    ):
                        self.module.warn(
                            "Cannot change the replication factor for the existing topic '%s'"
                            % self.name,
                        )

                # Execute the updates
                if not self.module.check_mode:
                    if update_config:
                        self._update_topic_config(update_config)

                    if update_partitions:
                        self._update_topic_partitions()

                # Refresh the topic details
                if self.changed:
                    self.topic = self._get_topic(self.name)
                else:
                    self.topic = existing

            elif not self.module.check_mode:
                # Check for missing parameters
                if not self.num_partitions:
                    self.num_partitions = 1
                if not self.replication_factor:
                    self.replication_factor = 3

                # Create the topic
                self.changed = True
                self._create_topic()

                # Refresh the topic details
                self.topic = self._get_topic(self.name)
        else:
            if existing and not self.module.check_mode:
                # Delete the topic
                self.changed = True
                self._delete_topic()

    def _create_topic(self):
        new_topic = dict(
            name=self.name,
            numPartitions=self.num_partitions,
            replicationFactor=self.replication_factor,
            configs=self.configs,
        )

        return self.process_response(
            self._post("/api/v1/admin/topics", json=dict(newTopics=[new_topic])),
            [
                CdpRestResponse(
                    self.status_codes.no_content,
                    return_value={},
                ),  # HTTP 204
            ],
            "Failed to create new topic '%s'" % self.name,
        )

    def _delete_topic(self):
        return self.process_response(
            self._delete("/api/v1/admin/topics", params=dict(topicName=[self.name])),
            [
                CdpRestResponse(
                    self.status_codes.no_content,
                    return_value={},
                ),  # HTTP 204
            ],
            "Failed to delete topic '%s'" % self.name,
        )

    def _update_topic_config(self, payload: dict):
        return self.process_response(
            self._put("/api/v1/admin/configs/topics/%s" % self.name, json=payload),
            [
                CdpRestResponse(
                    self.status_codes.no_content,
                    return_value={},
                ),  # HTTP 204
            ],
            "Failed to update config for topic '%s'" % self.name,
        )

    def _update_topic_partitions(self):
        partitions = dict()
        partitions[self.name] = dict(totalCount=self.num_partitions)
        return self.process_response(
            self._put(
                "/api/v1/admin/topics",
                json=dict(topicWithNewPartitions=partitions),
            ),
            [
                CdpRestResponse(
                    self.status_codes.no_content,
                    return_value={},
                ),  # HTTP 204
            ],
            "Failed to update partitions for topic '%s'" % self.name,
        )


def main():
    module = AnsibleModule(
        **CdpSmmModule.module_spec(
            argument_spec=dict(
                state=dict(
                    required=False,
                    choices=["present", "absent"],
                    default="present",
                ),
                name=dict(required=True, aliases=["topic"]),
                num_partitions=dict(type="int", aliases=["partitions"]),
                replication_factor=dict(type="int", aliases=["replication"]),
                configs=dict(
                    type="dict",
                    default=dict(),
                    aliases=["config", "configuration"],
                ),
                reset=dict(type="bool", default=False, aliases=["reset_configs"]),
            ),
            supports_check_mode=True,
        ),
    )

    result = SmmKafkaTopic(module)
    result.process()

    output = dict(changed=result.changed, topic=result.topic)

    if result.debug:
        output.update(sdk_out=result.log_out, sdk_out_lines=result.log_lines)

    module.exit_json(**output)


if __name__ == "__main__":
    main()

# replica_assignments:
#   description:
#     - Dictionary containing the assignment of the Kafka topic partitions.
#     - The C(key) of the dictionary is the partition id.
#     - The C(value) of the dictionary is a list of the IDs of the brokers to which the replicas should be assigned.
#   required: False
#   type: dict
#   aliases:
#     - assignments
#
# replica_assignment:
#   0: [101, 102, 103]
#   1: [102, 103, 101]

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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.cdp_ssb import (
    CdpSsbProjectEntityModule,
)

logging.basicConfig(level=logging.INFO)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: ranger
short_description: Create, update, and delete Apache Ranger services and policies
description:
  - Create, update, and delete Apache Ranger services and policies
author:
  - "Andre Araujo (@asdaraujo)"
version_added: "1.0.0"
requirements:
  - apache-ranger
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
account:
    description: Returns the authentication settings for the CDP Account
    returned: always
    type: dict
    contains:
        clouderaSSOLoginEnabled:
            description: Flag indicating whether interactive login using Cloudera SSO is enabled.
            returned: always
            type: bool
        workloadPasswordPolicy:
            description: Information about the workload password policy for an account.
            returned: always
            type: dict
            contains:
                maxPasswordLifetimeDays:
                    description: The max lifetime, in days, of the password. If '0', passwords never expire.
                    returned: always
                    type: int
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

CSRF_PATTERNS = [
    r'.*var csrf_token = "([^"]*)".*',
]


class SsbCatalog(CdpSsbProjectEntityModule):
    def __init__(self, module):
        super(SsbCatalog, self).__init__(module)

        self.type = self._get_param("type")
        self.state = self._get_param("state")

        # More complex checks
        if self.state == "present":
            if self.type == "kudu":
                required = ["kudu_masters"]
            elif self.type == "registry":
                required = ["kafka_provider_name", "registry_address"]
            elif self.type == "hive":
                required = ["default_database"]
            elif self.type == "custom":
                required = ["custom_properties"]
            missing = [r for r in required if not self._get_param(r)]
            if missing:
                self.module.fail_json(
                    "Type is [{}] but all of the following are missing: {}.".format(
                        self.type,
                        ", ".join(missing),
                    ),
                )

        self.name = self._get_param("name")
        self.table_filters = self._get_param("table_filters")
        # Kudu
        self.kudu_masters = self._get_param("kudu_masters")
        # Kudu
        self.default_database = self._get_param("default_database")
        # Schema Registry
        self.kafka_provider_name = self._get_param("kafka_provider_name")
        self.registry_address = self._get_param("registry_address")
        self.registry_ssl_enabled = self._get_param("registry_ssl_enabled")
        self.registry_truststore_location = self._get_param(
            "registry_truststore_location",
        )
        self.registry_truststore_password = self._get_param(
            "registry_truststore_password",
        )
        # Custom
        self.custom_properties = self._get_param("custom_properties") or {}

        self.logger = logging.getLogger("ssb_catalog_module")
        if self._get_param("debug"):
            self.logger.setLevel(logging.DEBUG)

        # Initialize the return values
        self.changed = False
        self.catalog = None

    def _create_catalog(self):
        properties = {
            "catalog_type": self.type,
            "table_filters": self.table_filters or [],
        }
        if self.type == "kudu":
            properties.update(
                {
                    "kudu.masters": self.kudu_masters,
                },
            )
        elif self.type == "hive":
            properties.update(
                {
                    "default-database": self.default_database,
                },
            )
        elif self.type == "registry":
            kafka_provider = self._get_data_sources(
                data_source_name=self.kafka_provider_name,
                data_source_type="kafka",
            )
            if not kafka_provider:
                raise RuntimeError(
                    "Kafka provider {} does not exist.".format(
                        self.kafka_provider_name,
                    ),
                )
            properties.update(
                {
                    "kafka.provider.id": kafka_provider[0]["id"],
                    "registry.address": self.registry_address,
                    "registry.ssl.enabled": self.registry_ssl_enabled,
                },
            )
            if self.registry_truststore_location:
                properties[
                    "registry.truststore.location"
                ]: self.registry_truststore_location
            if self.registry_truststore_password:
                properties[
                    "registry.truststore.password"
                ]: self.registry_truststore_password
        elif self.type == "custom":
            properties.update(self.custom_properties)

        data = {
            "name": self.name,
            "type": "catalog",
            "properties": properties,
        }
        return self._create_data_source(data)

    def _is_same_catalog(self, catalog):
        kafka_provider_id = None
        if self.type == "registry":
            kafka_provider = self._get_data_sources(
                self.kafka_provider_name,
                data_source_type="kafka",
            )
            kafka_provider_id = kafka_provider[0]["id"] if kafka_provider else None
        properties = self.custom_properties.copy()
        properties.update(
            {
                "catalog_type": self.type,
                "table_filters": self.table_filters or [],
            },
        )
        return (
            self.name == catalog["name"]
            and self.type == catalog.get("properties", {}).get("catalog_type", None)
            and self.table_filters
            == (catalog.get("properties", {}).get("table_filters", None) or None)
            and (
                self.type != "kudu"
                or (
                    self.kudu_masters
                    == catalog.get("properties", {}).get("kudu.masters", None)
                )
            )
            and (
                self.type != "hive"
                or (
                    self.default_database
                    == catalog.get("properties", {}).get("default-database", None)
                )
            )
            and (
                self.type != "registry"
                or (
                    kafka_provider_id
                    == catalog.get("properties", {}).get("kafka.provider.id", None)
                    and self.registry_address
                    == catalog.get("properties", {}).get("registry.address", None)
                    and self.registry_ssl_enabled
                    == catalog.get("properties", {}).get("registry.ssl.enabled", None)
                    and self.registry_truststore_location
                    == catalog.get("properties", {}).get(
                        "registry.truststore.location",
                        None,
                    )
                    and self.registry_truststore_password
                    == catalog.get("properties", {}).get(
                        "registry.truststore.password",
                        None,
                    )
                )
            )
            and (self.type != "custom" or (properties == catalog.get("properties", {})))
        )

    def process(self):
        existing_catalog = self._get_data_sources(self.name, data_source_type="catalog")
        if self.state == "present":
            if not existing_catalog or not self._is_same_catalog(existing_catalog[0]):
                self.changed = True
                if not self.module.check_mode:
                    if existing_catalog:
                        self._delete_data_source(
                            data_source_id=existing_catalog[0]["id"],
                        )
                    self.catalog = self._create_catalog()
            else:
                self.catalog = existing_catalog[0]
        else:  # state == absent
            if existing_catalog:
                self.changed = True
                if not self.module.check_mode:
                    self._delete_data_source(data_source_id=existing_catalog[0]["id"])


FILTER = dict(
    database_filter=dict(required=True, type="str"),
    table_filter=dict(required=True, type="str"),
)


def main():
    module = AnsibleModule(
        **SsbCatalog.module_spec(
            argument_spec=dict(
                name=dict(required=True, type="str"),
                type=dict(
                    required=True,
                    type="str",
                    choices=["kudu", "registry", "hive", "custom"],
                ),
                table_filters=dict(
                    required=False,
                    type="list",
                    elements="dict",
                    options=FILTER,
                ),
                # Kudu
                kudu_masters=dict(required=False, type="str"),
                # Hive
                default_database=dict(required=False, type="str"),
                # Schema Registry
                kafka_provider_name=dict(required=False, type="str"),
                registry_address=dict(required=False, type="str"),
                registry_ssl_enabled=dict(required=False, type="bool", default=False),
                registry_truststore_location=dict(required=False, type="str"),
                registry_truststore_password=dict(
                    required=False,
                    type="str",
                    no_log=True,
                ),
                # Custom
                custom_properties=dict(required=False, type="dict", no_log=True),
                state=dict(
                    required=False,
                    type="str",
                    choices=["present", "absent"],
                    default="present",
                ),
            ),
            mutually_exclusive=[
                ("kudu_masters", "default_database"),
                ("kudu_masters", "kafka_provider_name"),
                ("kudu_masters", "registry_address"),
                ("kudu_masters", "registry_ssl_enabled"),
                ("kudu_masters", "registry_truststore_location"),
                ("kudu_masters", "registry_truststore_password"),
                ("kudu_masters", "custom_properties"),
                ("default_database", "kafka_provider_name"),
                ("default_database", "registry_address"),
                ("default_database", "registry_ssl_enabled"),
                ("default_database", "registry_truststore_location"),
                ("default_database", "registry_truststore_password"),
                ("default_database", "custom_properties"),
                ("custom_properties", "kafka_provider_name"),
                ("custom_properties", "registry_address"),
                ("custom_properties", "registry_ssl_enabled"),
                ("custom_properties", "registry_truststore_location"),
                ("custom_properties", "registry_truststore_password"),
            ],
            supports_check_mode=True,
        ),
    )

    result = SsbCatalog(module)
    result.process()

    output = dict(
        changed=result.changed,
        function=result.catalog,
    )

    # if result.debug:
    #     output.update(
    #        sdk_out=result.log_out,
    #        sdk_out_lines=result.log_lines
    #     )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

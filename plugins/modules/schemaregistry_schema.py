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
import requests

from ansible.module_utils.basic import AnsibleModule

logging.basicConfig(level=logging.INFO)

DOCUMENTATION = r"""
module: schemaregistry_schema
short_description: Create and delete schemas in Schema Registry
description:
  - Create and delete schemas in Schema Registry
  - The module supports check_mode.
author:
  - "Andre Araujo (@asdaraujo)"
version_added: "1.0.0"
requirements:
  - requests
options:
  endpoint:
    description: Schema Registry REST API endpoint.
    required: True
    type: str
    aliases: url
  username:
    description: Username for authentication with the REST API.
    required: True
    type: str
    aliases: user
  password:
    description: Password for authentication with the REST API.
    required: True
    type: str
  ssl_ca_cert:
    description:
      - Path of a file containing a TLS root certificate in PEM format.
      - If provided, the certificate will be used to validate SMM's certificate.
    required: False
    type: str
  name:
    description: Name of the schema.
    required: True
    type: str
  description:
    description: Description of the schema.
    required: False
    type: str
    default: ""
    aliases: desc
  type:
    description:
      - Type of the schema.
      - The only type currently supported is V(avro).
    required: False
    type: str
    choices:
      - avro
    default: avro
  schema_group:
    description: Name of the schema's group.
    required: False
    type: str
    default: Kafka
    aliases: group
  compatibility:
    description: Type of compatibility to be enforced for the schema.
    required: False
    type: str
    choices: [BACKWARD, FORWARD, BOTH, NONE]
    default: BACKWARD
    aliases: compat
  evolve:
    description: Indicates whether the schema can evolve or not.
    required: False
    type: bool
    default: True
  schema_text:
    description:
      - String containing the content of the schema.
      - Mutually exclusive with schema_file.
    required: False
    type: str
  schema_file:
    description:
      - Path to the file containing the content of the schema.
      - Mutually exclusive with schema_text.
    required: False
    type: str
  state:
    description:
      - The declarative state of the CustomFlow
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
schemaregistry_schema:
  endpoint: https://kafka.cloudera.site/kafka-cluster/cdp-proxy-api/schema-registry/api/v1/
  username: alice
  password: supersecret
  name: Transaction
  description: Schema describing the transaction entity
  schema_file: /path/to/transaction.avsc
  state: present
"""

RETURN = r"""
---
"""


class SchemaRegistrySchema(AnsibleModule):
    def __init__(self, module):
        self.module = module

        self.endpoint = self._get_param("endpoint").rstrip(
            "/",
        )  # must not have the trailing slash
        self.username = self._get_param("username")
        self.password = self._get_param("password")
        self.ssl_ca_cert = self._get_param("ssl_ca_cert")

        self.name = self._get_param("name")
        self.description = self._get_param("description")
        self.type = self._get_param("type")
        self.schema_group = self._get_param("schema_group")
        self.compatibility = self._get_param("compatibility")
        self.evolve = self._get_param("evolve")
        self.schema_text = self._get_param("schema_text")
        self.schema_file = self._get_param("schema_file")

        self.state = self._get_param("state")

        self.logger = logging.getLogger("schemaregistry_schema_module")
        if self._get_param("debug"):
            self.logger.setLevel(logging.DEBUG)

        # Initialize the return values
        self.changed = False

    def _get_param(self, param, default=None):
        """Fetches an Ansible Input Parameter if it exists, else returns optional default or None"""
        if self.module is not None and self.module.params is not None:
            return self.module.params.get(param, default)
        return default

    def _schema_content(self):
        return self.schema_text or open(self.schema_file, "r").read()

    def _get_schema(self):
        url = "{}/schemaregistry/schemas/{}".format(self.endpoint, self.name)
        resp = requests.get(
            url,
            auth=(self.username, self.password),
            json={},
            verify=self.ssl_ca_cert,
        )
        if resp.status_code == requests.codes.not_found:
            return None
        elif resp.status_code != requests.codes.ok:
            self.module.fail_json(
                msg="Fail to retrieve schema [{}]. Error code: {}, Output: {}".format(
                    self.name,
                    resp.status_code,
                    resp.text,
                ),
            )
        return resp.json()

    def _get_latest_schema_version(self):
        url = "{}/schemaregistry/schemas/{}/versions/latest".format(
            self.endpoint,
            self.name,
        )
        resp = requests.get(
            url,
            auth=(self.username, self.password),
            json={},
            verify=self.ssl_ca_cert,
        )
        if resp.status_code == requests.codes.not_found:
            return None
        elif resp.status_code != requests.codes.ok:
            self.module.fail_json(
                msg="Fail to retrieve latest version of schema [{}]. Error code: {}, Output: {}".format(
                    self.name,
                    resp.status_code,
                    resp.text,
                ),
            )
        return resp.json()

    def _create_schema(self):
        url = "{}/schemaregistry/schemas".format(self.endpoint)
        payload = {
            "type": self.type,
            "schemaGroup": self.schema_group,
            "name": self.name,
            "description": self.description,
            "compatibility": self.compatibility,
            "validationLevel": "LATEST",
        }
        resp = requests.post(
            url,
            auth=(self.username, self.password),
            json=payload,
            verify=self.ssl_ca_cert,
        )
        if resp.status_code != requests.codes.created:
            self.module.fail_json(
                msg="Fail to create schema [{}]. Error code: {}, Output: {}".format(
                    self.name,
                    resp.status_code,
                    resp.text,
                ),
            )

    def _delete_schema(self):
        url = "{}/schemaregistry/schemas/{}".format(self.endpoint, self.name)
        resp = requests.delete(
            url,
            auth=(self.username, self.password),
            json={},
            verify=self.ssl_ca_cert,
        )
        if resp.status_code != requests.codes.ok:
            self.module.fail_json(
                msg="Fail to delete schema [{}]. Error code: {}, Output: {}".format(
                    self.name,
                    resp.status_code,
                    resp.text,
                ),
            )

    def _create_schema_version(self):
        url = "{}/schemaregistry/schemas/{}/versions".format(self.endpoint, self.name)
        payload = {
            "description": "",
            "schemaText": self._schema_content(),
        }
        resp = requests.post(
            url,
            auth=(self.username, self.password),
            json=payload,
            verify=self.ssl_ca_cert,
        )
        if resp.status_code != requests.codes.created:
            self.module.fail_json(
                msg="Fail to create version for schema [{}]. Error code: {}, Output: {}".format(
                    self.name,
                    resp.status_code,
                    resp.text,
                ),
            )

    def _is_new_schema(self):
        return self._get_schema() is None

    def _is_new_version(self):
        latest = self._get_latest_schema_version()
        return latest is None or latest["schemaText"] != self._schema_content()

    def process(self):
        if self.state == "present":
            if self._is_new_schema():
                self.changed = True
                if not self.module.check_mode:
                    self._create_schema()
            if self._is_new_version():
                self.changed = True
                if not self.module.check_mode:
                    self._create_schema_version()
        elif self.state == "absent":
            if not self._is_new_schema():
                self.changed = True
                if not self.module.check_mode:
                    self._delete_schema()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            endpoint=dict(required=True, type="str", aliases=["url"]),
            username=dict(required=True, type="str", aliases=["user"]),
            password=dict(required=True, type="str", no_log=True),
            ssl_ca_cert=dict(required=False, type="str"),
            name=dict(required=True, type="str"),
            description=dict(required=False, type="str", default="", aliases=["desc"]),
            type=dict(required=False, type="str", choices=["avro"], default="avro"),
            schema_group=dict(
                required=False,
                type="str",
                default="Kafka",
                aliases=["group"],
            ),
            compatibility=dict(
                required=False,
                type="str",
                choices=["BACKWARD", "FORWARD", "BOTH", "NONE"],
                default="BACKWARD",
                aliases=["compat"],
            ),
            evolve=dict(required=False, type="bool", default=True),
            schema_text=dict(required=False, type="str"),
            schema_file=dict(required=False, type="str"),
            debug=dict(required=False, type="bool", default=False),
        ),
        required_one_of=[
            ("schema_text", "schema_file"),
        ],
        mutually_exclusive=[
            ("schema_text", "schema_file"),
        ],
        supports_check_mode=True,
    )

    result = SchemaRegistrySchema(module)
    result.process()

    output = dict(
        changed=result.changed,
    )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

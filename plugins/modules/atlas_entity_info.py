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

import json
import logging
import re

from ansible.module_utils.basic import AnsibleModule
from apache_atlas.client.base_client import AtlasClient
from apache_atlas.model.instance import (
    AtlasEntity,
    AtlasEntityWithExtInfo,
    AtlasEntitiesWithExtInfo,
    AtlasRelatedObjectId,
)
from apache_atlas.model.enums import EntityOperation, TypeCategory
from apache_atlas.model.misc import SearchFilter
from apache_atlas.model.typedef import AtlasTypesDef
from apache_atlas.exceptions import AtlasServiceException
from apache_atlas.utils import PREFIX_ATTR

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: atlas_entity_info
short_description: Get details on individual Apache Atlas entities
description:
  - Get details on individual Apache Atlas entities.
  - The module supports check_mode.
author:
  - "Webster Mudge (@wmudge)"
version_added: "1.0.0"
requirements:
  - apache-atlas
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


class AtlasEntityInfo(AnsibleModule):
    def __init__(self, module):
        # Set parameters
        self.module = module
        self.endpoint = self._get_param("endpoint")
        self.username = self._get_param("username")
        self.password = self._get_param("password")
        self.attributes = self._get_param("attributes")
        self.type = self._get_param("type")
        self.id = self._get_param("id")
        self.debug = self._get_param("debug")

        # Set up the client
        self.atlas = AtlasClient(self.endpoint, (self.username, self.password))
        if self.debug:
            logging.getLogger("apache_atlas").setLevel(logging.DEBUG)

        # Initialize the return values
        self.changed = False
        self.entity = {}

        # Execute logic process
        self.process()

    def process(self):
        existing = self._get_entity()
        if existing is not None:
            self.entity = existing

    def _get_entity(self):
        try:
            if self.id:
                return self.atlas.entity.get_entity_by_guid(self.id)
            else:
                query_params = self._attributes_to_params(self.attributes)
                query_params["minExtInfo"] = False
                query_params["ignoreRelationships"] = False
                return self.atlas.call_api(
                    self.atlas.entity.GET_ENTITY_BY_UNIQUE_ATTRIBUTE.format_path_with_params(
                        self.type,
                    ),
                    AtlasEntityWithExtInfo,
                    query_params,
                )
        except AtlasServiceException as err:
            _CLIENT_ERROR_PATTERN = re.compile(
                r"(.*?) : failed with status (.*?) and Response Body is :(.*?)",
            )
            error = re.search(_CLIENT_ERROR_PATTERN, str(err))
            if error.group(2) == "404":
                return None
            else:
                self.module.fail_json("Unexpected error: %s" % err)

    def _get_param(self, param, default=None):
        """Fetches an Ansible Input Parameter if it exists, else returns optional default or None"""
        if self.module is not None:
            return self.module.params[param] if param in self.module.params else default
        return default

    def _attributes_to_params(self, attributes, query_params=None):
        if query_params is None:
            query_params = {}

        if attributes:
            for key, value in attributes.items():
                new_key = PREFIX_ATTR + key
                query_params[new_key] = value

        return query_params


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type="str", aliases=["url"]),
            username=dict(required=True, type="str", aliases=["user"]),
            password=dict(required=True, type="str", no_log=True),
            type=dict(required=False, type="str", aliases=["typeName"]),
            attributes=dict(required=False, type="dict"),
            id=dict(required=False, type="str", aliases=["guid"]),
            debug=dict(required=False, type="bool", default=False),
        ),
        # required_one_of=[ 'attributes', 'name', 'id' ],
        supports_check_mode=True,
    )

    result = AtlasEntityInfo(module)

    output = dict(
        changed=False,
        entity=result.entity,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

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

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: atlas_typedef
short_description: Create, update, and delete Apache Atlas type definitions
description:
  - Manage (create, update, delete) Apache Atlas type definitions (typedefs).
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


class AtlasTypedef(AnsibleModule):
    def __init__(self, module):
        # Set parameters
        self.module = module
        self.endpoint = self._get_param("endpoint")
        self.username = self._get_param("username")
        self.password = self._get_param("password")
        self.name = self._get_param("name")
        self.id = self._get_param("id")
        self.description = self._get_param("description")
        self.business_metadata = self._get_param("business_metadata")
        self.classification = self._get_param("classification")
        self.state = self._get_param("state")
        self.debug = self._get_param("debug")

        # Set up the client
        self.atlas = AtlasClient(self.endpoint, (self.username, self.password))
        if self.debug:
            logging.getLogger("apache_atlas").setLevel(logging.DEBUG)

        # Initialize the return values
        self.changed = False
        self.typedef = {}

        # Execute logic process
        self.process()

    def process(self):
        existing = self._get_typedef()

        if self.state == "present":
            payload = self._create_payload()

            if existing is None:
                self.changed = True
                self.typedef = self.atlas.typedef.create_atlas_typedefs(payload)
            else:
                # TODO: Compare incoming to existing (e.g. attributes can't be changed, so explicit delete and recreate?)
                if True:
                    self.changed = True
                    self.typedef = self.atlas.typedef.update_atlas_typedefs(payload)
                else:
                    self.typedef = existing
        else:
            if existing is not None:
                self.changed = True
                self.atlas.typedef.delete_type_by_name(self.name)

    def _create_payload(self):
        payload = AtlasTypesDef()

        if self.business_metadata:
            payload.businessMetadataDefs = self.business_metadata

        if self.classification is not None:
            obj = dict(
                category=TypeCategory.CLASSIFICATION.name,
                name=self.name,
                **self.classification,
            )
            if self.description:
                obj.update(description=self.description)
            payload.classificationDefs = [obj]

        return payload

    def _get_typedef(self):
        try:
            return self.atlas.call_api(
                self.atlas.typedef.GET_TYPEDEF_BY_NAME.format_path_with_params(
                    self.name,
                ),
                str,
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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            endpoint=dict(required=True, type="str", aliases=["url"]),
            username=dict(required=True, type="str", aliases=["user"]),
            password=dict(required=True, type="str", no_log=True),
            name=dict(required=False, type="str"),
            id=dict(required=False, type="int"),
            description=dict(required=False, type="str", aliases=["desc"]),
            business_metadata=dict(required=False, type="dict"),
            classification=dict(
                required=False,
                type="dict",
                contains=dict(
                    options=dict(required=False, type="dict"),
                    serviceType=dict(
                        required=False,
                        type="str",
                        aliases=["service_type"],
                    ),
                    entity_types=dict(
                        required=False,
                        type="list",
                        elements="str",
                        aliases=["entityTypes"],
                    ),
                    subtypes=dict(
                        required=False,
                        type="list",
                        elements="str",
                        aliases=["subTypes"],
                    ),
                    supertypes=dict(
                        required=False,
                        type="list",
                        elements="str",
                        aliases=["superTypes"],
                    ),
                    attributeDefs=dict(
                        required=False,
                        type="list",
                        aliases=["attributes"],
                        elements=dict(
                            name=dict(required=True, type="str"),
                            description=dict(
                                required=False,
                                type="str",
                                aliases=["desc"],
                            ),
                            isUnique=dict(
                                required=False,
                                type="bool",
                                aliases=["unique"],
                            ),
                        ),
                    ),
                ),
            ),
            state=dict(
                required=False,
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            debug=dict(required=False, type="bool", default=False),
        ),
        # required_one_of=[ 'name', 'id' ],
        supports_check_mode=True,
    )

    result = AtlasTypedef(module)

    output = dict(
        changed=result.changed,
        typedef=result.typedef,
    )

    if result.debug:
        output.update(
            sdk_out=result.log_out,
            sdk_out_lines=result.log_lines,
        )

    module.exit_json(**output)


if __name__ == "__main__":
    main()

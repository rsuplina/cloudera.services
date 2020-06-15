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

from apache_ranger.client.ranger_client import RangerClient
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning


def populate_role_payload(role):
    payload = {}

    if role.name is not None:
        payload["name"] = role.name
    if role.description is not None:
        payload["description"] = role.description
    if role.users is not None:
        payload["users"] = role.users
    if role.groups is not None:
        payload["groups"] = role.groups
    if role.roles is not None:
        payload["roles"] = role.roles
    return payload


def populate_service_payload(service):
    payload = {}

    if service.type is not None:
        payload["type"] = service.type
    if service.name is not None:
        payload["name"] = service.name
    if service.display_name is not None:
        payload["displayName"] = service.display_name
    if service.description is not None:
        payload["description"] = service.description
    if service.tag_service is not None:
        payload["tagService"] = service.tag_service
    if service.enabled is not None:
        payload["isEnabled"] = service.enabled
    if service.configs is not None:
        payload["configs"] = service.configs

    return payload


def populate_policy_payload(policy):
    payload = {}
    if policy.name is not None:
        payload["name"] = policy.name
    if policy.description is not None:
        payload["description"] = policy.description
    if policy.policy_labels is not None:
        payload["policyLabels"] = policy.policy_labels
    if policy.enable_audit is not None:
        payload["isAuditEnabled"] = policy.enable_audit
    if policy.enabled is not None:
        payload["isEnabled"] = policy.enabled
    if policy.policy_priority not in (None, 0):
        payload["policyPriority"] = policy.policy_priority
    if policy.service is not None:
        payload["service"] = policy.service
    if policy.service_type is not None:
        payload["serviceType"] = policy.service_type
    if policy.resource_signature is not None:
        payload["resourceSignature"] = policy.resource_signature
    if policy.options is not None:
        payload["options"] = policy.options
    if policy.resources is not None:
        payload["resources"] = policy.resources
    if policy.additional_resources is not None:
        payload["additionalResources"] = policy.additional_resources
    if policy.zone_name not in (None, ""):
        payload["zoneName"] = policy.zone_name
    if policy.deny_all_else is not None:
        payload["isDenyAllElse"] = policy.deny_all_else
    if policy.conditions is not None:
        payload["conditions"] = policy.conditions
    if policy.allow_exceptions is not None:
        payload["allowExceptions"] = policy.allow_exceptions
    if policy.deny_exceptions is not None:
        payload["denyExceptions"] = policy.deny_exceptions
    if policy.policy_type is not None:
        payload["policyType"] = policy.policy_type
    if policy.access_policies is not None:
        payload["policyItems"] = policy.access_policies
    if policy.deny_policies is not None:
        payload["denyPolicyItems"] = policy.deny_policies
    if policy.data_mask_policies is not None:
        payload["dataMaskPolicyItems"] = policy.data_mask_policies
    if policy.row_filter_policies is not None:
        payload["rowFilterPolicyItems"] = policy.row_filter_policies
    return payload


IGNORED_KEYS = {
    "id",
    "guid",
    "createTime",
    "updateTime",
    "createdBy",
    "updatedBy",
    "resourceSignature",
    "version",
}


def clean_dict(data, ignore_keys=IGNORED_KEYS):
    # Clean dicts
    if isinstance(data, dict):
        return {
            k: clean_dict(v, ignore_keys)
            for k, v in data.items()
            if k not in ignore_keys and not should_remove_value(k, v)
        }
    # Clean lists
    elif isinstance(data, list):
        # If list is empty or contains only None/empty dicts, remove it
        cleaned_list = [clean_dict(item, ignore_keys) for item in data]
        return [item for item in cleaned_list if item not in (None, [], {})]
    else:
        return data


def should_remove_value(key, value):
    # Check if the value should be removed for specific keys
    if key in ["zoneName", "policyPriority", "policyType"] and value in [0, ""]:
        return True
    # Check for general cases like None, empty lists, and empty dicts
    if value in [None, [], {}]:
        return True
    return False


class RangerModule(object):
    def get_param(self, param, default=None):
        """
        Fetches an Ansible input parameter if it exists, else returns optional
        default or None.
        """
        if self.module is not None:
            return self.module.params[param] if param in self.module.params else default
        return default

    @staticmethod
    def remove_nulls(a):
        if isinstance(a, list):
            return [RangerModule.remove_nulls(i) for i in a]
        elif isinstance(a, dict):
            output = {}
            for key, value in a.items():
                if value and value != []:
                    output[key] = RangerModule.remove_nulls(value)
            return output
        else:
            return a

    def __init__(self, module):
        # Set common parameters
        self.module = module

        self.endpoint = self.get_param("endpoint")
        self.username = self.get_param("username")
        self.password = self.get_param("password")
        self.verify_tls = self.get_param("verify_tls")
        self.ssl_ca_cert = self.get_param("ssl_ca_cert")

        # Initialize common return values
        self.changed = False

        self.ranger = RangerClient(self.endpoint, (self.username, self.password))
        if self.verify_tls:
            if self.ssl_ca_cert is None:
                self.ranger.session.verify = True
            else:
                self.ranger.session.verify = self.get_param("ssl_ca_cert")
        else:
            self.ranger.session.verify = False

        if self.verify_tls is False:
            disable_warnings(InsecureRequestWarning)

        self.logger = logging.getLogger("ranger_module")
        if self.get_param("debug"):
            self.logger.setLevel(logging.DEBUG)


class RangerMutableModule(RangerModule):
    def __init__(self, module):
        super(RangerMutableModule, self).__init__(module)
        self.message = self.get_param("message")

    @staticmethod
    def ansible_module(
        argument_spec={},
        bypass_checks=False,
        no_log=False,
        mutually_exclusive=[],
        required_together=[],
        required_one_of=[],
        add_file_common_args=False,
        supports_check_mode=False,
        required_if=None,
        required_by=None,
    ):
        return RangerModule.ansible_module(
            argument_spec=dict(
                **argument_spec,
                message=dict(default="Managed by Ansible", aliases=["msg"]),
            ),
            bypass_checks=bypass_checks,
            no_log=no_log,
            mutually_exclusive=mutually_exclusive,
            required_together=required_together,
            required_one_of=required_one_of,
            add_file_common_args=add_file_common_args,
            supports_check_mode=supports_check_mode,
            required_if=required_if,
            required_by=required_by,
        )

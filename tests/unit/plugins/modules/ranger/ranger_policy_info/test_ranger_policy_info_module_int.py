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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import pytest

from typing import Callable

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger_policy_info
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyResource,
)

REQUIRED_ENV_VARS = [
    "RANGER_ADMIN_URL",
    "RANGER_ADMIN_USERNAME",
    "RANGER_ADMIN_PASSWORD",
]


@pytest.fixture
def ranger_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to set common module args for Ranger tests."""

    def _ranger_module_args(overrides: dict = {}) -> None:
        args = {
            "url": env_context["RANGER_ADMIN_URL"],
            "url_username": env_context["RANGER_ADMIN_USERNAME"],
            "url_password": env_context["RANGER_ADMIN_PASSWORD"],
            "validate_certs": os.environ.get("RANGER_VALIDATE_CERTS", "false").lower()
            == "true",
            "force_basic_auth": True,
        }
        if overrides:
            args.update(overrides)
        module_args(args)

    return _ranger_module_args


def test_ranger_policy_info_module_list_all(ranger_module_args, existing_policy):
    """Test RangerPolicyInfoModule list all policies."""

    ranger_module_args({})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert isinstance(result["policies"], list)
    assert any(p["id"] == existing_policy.id for p in result["policies"])


def test_ranger_policy_info_module_by_id(ranger_module_args, existing_policy):
    """Test RangerPolicyInfoModule get policy by id."""

    ranger_module_args({"policy_id": existing_policy.id})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 1
    assert result["policies"][0]["id"] == existing_policy.id


def test_ranger_policy_info_module_by_name(ranger_module_args, existing_policy):
    """Test RangerPolicyInfoModule get policy by name."""

    ranger_module_args({"name": existing_policy.name})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 1
    assert result["policies"][0]["name"] == existing_policy.name


def test_ranger_policy_info_module_by_service(
    ranger_module_args,
    test_service,
    existing_policy,
):
    """Test RangerPolicyInfoModule get policies by service."""

    ranger_module_args({"service": test_service})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert isinstance(result["policies"], list)
    # Verify all returned policies belong to the specified service
    for policy in result["policies"]:
        assert policy["service"] == test_service


def test_ranger_policy_info_module_nonexistent_name(ranger_module_args):
    """Test RangerPolicyInfoModule with nonexistent policy name."""

    ranger_module_args({"name": "nonexistent-policy-name-12345"})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 0


def test_ranger_policy_info_module_check_mode(ranger_module_args):
    """Test RangerPolicyInfoModule in check mode."""

    ranger_module_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result

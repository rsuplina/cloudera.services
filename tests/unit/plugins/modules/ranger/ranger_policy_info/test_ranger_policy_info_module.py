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

import pytest

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.services.plugins.modules import ranger_policy_info
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyResource,
)

BASE_URL = "https://ranger.example.com"


def test_ranger_policy_info_module_list_all(module_args, mocker):
    """Test RangerPolicyInfoModule listing all policies."""
    policy1 = RangerPolicy(
        id=1,
        name="policy-1",
        service="hdfs",
        resources={"path": RangerPolicyResource(values=["/tmp/1"])},
    )
    policy2 = RangerPolicy(
        id=2,
        name="policy-2",
        service="hive",
        resources={"database": RangerPolicyResource(values=["default"])},
    )

    mock_list_policies = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.list_policies",
        return_value=[policy1, policy2],
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 2
    assert result["policies"][0]["id"] == 1
    assert result["policies"][0]["name"] == "policy-1"
    assert result["policies"][1]["id"] == 2
    assert result["policies"][1]["name"] == "policy-2"

    mock_list_policies.assert_called_once_with()


def test_ranger_policy_info_module_by_id(module_args, mocker):
    """Test RangerPolicyInfoModule getting policy by ID."""
    policy = RangerPolicy(
        id=1,
        name="test-policy",
        service="hdfs",
        resources={"path": RangerPolicyResource(values=["/tmp/test"])},
    )

    mock_get_policy_by_id = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.get_policy_by_id",
        return_value=policy,
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "policy_id": 1,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 1
    assert result["policies"][0]["id"] == 1
    assert result["policies"][0]["name"] == "test-policy"

    mock_get_policy_by_id.assert_called_once_with(policy_id=1)


def test_ranger_policy_info_module_by_name_with_service(module_args, mocker):
    """Test RangerPolicyInfoModule getting policy by name and service."""
    policy = RangerPolicy(
        id=1,
        name="test-policy",
        service="hdfs",
        resources={"path": RangerPolicyResource(values=["/tmp/test"])},
    )

    mock_get_policy_by_name = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.get_policy_by_name",
        return_value=policy,
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "name": "test-policy",
            "service": "hdfs",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 1
    assert result["policies"][0]["name"] == "test-policy"
    assert result["policies"][0]["service"] == "hdfs"

    mock_get_policy_by_name.assert_called_once_with(
        service_name="hdfs",
        policy_name="test-policy",
    )


def test_ranger_policy_info_module_by_name_without_service(module_args, mocker):
    """Test RangerPolicyInfoModule getting policy by name without service (list and filter)."""
    policy1 = RangerPolicy(
        id=1,
        name="test-policy",
        service="hdfs",
        resources={"path": RangerPolicyResource(values=["/tmp/test"])},
    )
    policy2 = RangerPolicy(
        id=2,
        name="other-policy",
        service="hive",
        resources={"database": RangerPolicyResource(values=["default"])},
    )

    mock_list_policies = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.list_policies",
        return_value=[policy1, policy2],
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "name": "test-policy",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 1
    assert result["policies"][0]["id"] == 1
    assert result["policies"][0]["name"] == "test-policy"
    assert result["policies"][0]["service"] == "hdfs"

    mock_list_policies.assert_called_once_with()


def test_ranger_policy_info_module_by_service(module_args, mocker):
    """Test RangerPolicyInfoModule getting policies by service."""
    policy1 = RangerPolicy(
        id=1,
        name="hdfs-policy-1",
        service="hdfs",
        resources={"path": RangerPolicyResource(values=["/tmp/1"])},
    )
    policy2 = RangerPolicy(
        id=2,
        name="hdfs-policy-2",
        service="hdfs",
        resources={"path": RangerPolicyResource(values=["/tmp/2"])},
    )

    mock_list_policies = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.list_policies",
        return_value=[policy1, policy2],
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "service": "hdfs",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 2
    assert all(p["service"] == "hdfs" for p in result["policies"])
    assert result["policies"][0]["name"] == "hdfs-policy-1"
    assert result["policies"][1]["name"] == "hdfs-policy-2"

    mock_list_policies.assert_called_once_with(service_name="hdfs")


def test_ranger_policy_info_module_nonexistent_id(module_args, mocker):
    """Test RangerPolicyInfoModule with nonexistent policy ID."""
    mock_get_policy_by_id = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.get_policy_by_id",
        return_value=None,
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "policy_id": 999,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 0

    mock_get_policy_by_id.assert_called_once_with(policy_id=999)


def test_ranger_policy_info_module_nonexistent_name(module_args, mocker):
    """Test RangerPolicyInfoModule with nonexistent policy name."""
    mock_list_policies = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.list_policies",
        return_value=[],
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "name": "nonexistent-policy",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 0

    mock_list_policies.assert_called_once_with()


def test_ranger_policy_info_module_check_mode(module_args, mocker):
    """Test RangerPolicyInfoModule in check mode."""
    policy = RangerPolicy(
        id=1,
        name="test-policy",
        service="hdfs",
        resources={"path": RangerPolicyResource(values=["/tmp/test"])},
    )

    mock_list_policies = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy_info.RangerPolicyClient.list_policies",
        return_value=[policy],
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy_info.main()

    result = e.value
    assert result["changed"] is False
    assert "policies" in result
    assert len(result["policies"]) == 1
    assert result["policies"][0]["id"] == 1
    assert result["policies"][0]["name"] == "test-policy"

    mock_list_policies.assert_called_once_with()

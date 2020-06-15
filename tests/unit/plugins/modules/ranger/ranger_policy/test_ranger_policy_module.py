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
    AnsibleFailJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger_policy
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyResource,
)

BASE_URL = "https://ranger.cloudera.internal"


def test_ranger_policy_module_create_minimal(module_args, mocker):
    """Test RangerPolicyModule creating a policy with minimal parameters."""
    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=None,
    )
    mock_create_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.create_policy",
        return_value=RangerPolicy(
            id=1,
            name="test-policy",
            service="test-service",
            resources={
                "path": RangerPolicyResource(values=["/tmp/test"]),
            },
        ),
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "test-policy",
            "service": "test-service",
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value

    assert result["changed"] is True
    assert result["policy"]["name"] == "test-policy"
    assert result["policy"]["service"] == "test-service"
    assert "id" in result["policy"]

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="test-policy",
    )
    mock_create_policy.assert_called_once()


def test_ranger_policy_module_create_with_description(module_args, mocker):
    """Test RangerPolicyModule creating a policy with description and policy items."""
    description = "Test policy with description"

    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=None,
    )
    mock_create_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.create_policy",
        return_value=RangerPolicy(
            id=1,
            name="test-policy-with-desc",
            service="test-service",
            description=description,
            resources={
                "path": RangerPolicyResource(values=["/tmp/test"]),
            },
        ),
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "test-policy-with-desc",
            "service": "test-service",
            "description": description,
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value

    assert result["changed"] is True
    assert result["policy"]["name"] == "test-policy-with-desc"
    assert result["policy"]["description"] == description

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="test-policy-with-desc",
    )
    mock_create_policy.assert_called_once()


def test_ranger_policy_module_update_description(module_args, mocker):
    """Test RangerPolicyModule updating policy description."""
    new_description = "Updated description for testing"

    existing_policy = RangerPolicy(
        id=1,
        name="policy-to-update",
        service="test-service",
        description="Old description",
        resources={
            "path": RangerPolicyResource(values=["/tmp/test"]),
        },
    )

    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=existing_policy,
    )
    mock_update_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.update_policy",
        return_value=RangerPolicy(
            id=1,
            name="policy-to-update",
            service="test-service",
            description=new_description,
            resources={
                "path": RangerPolicyResource(values=["/tmp/test"]),
            },
        ),
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "policy-to-update",
            "service": "test-service",
            "description": new_description,
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True
    assert result["policy"]["description"] == new_description

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="policy-to-update",
    )
    mock_update_policy.assert_called_once()


def test_ranger_policy_module_delete_policy(module_args, mocker):
    """Test RangerPolicyModule deleting a policy."""
    existing_policy = RangerPolicy(
        id=1,
        name="policy-to-delete",
        service="test-service",
        resources={
            "path": RangerPolicyResource(values=["/tmp/test"]),
        },
    )

    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=existing_policy,
    )
    mock_delete_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.delete_policy_by_id",
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "absent",
            "name": "policy-to-delete",
            "service": "test-service",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="policy-to-delete",
    )
    mock_delete_policy.assert_called_once_with(1)


def test_ranger_policy_module_delete_nonexistent_policy(module_args, mocker):
    """Test RangerPolicyModule deleting a nonexistent policy (idempotent)."""
    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=None,
    )
    mock_delete_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.delete_policy_by_id",
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "absent",
            "name": "nonexistent-policy-12345",
            "service": "test-service",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is False

    mock_get_policy.assert_called_once()
    mock_delete_policy.assert_not_called()


def test_ranger_policy_module_check_mode_create(module_args, mocker):
    """Test RangerPolicyModule in check mode for create."""
    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=None,
    )
    mock_create_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.create_policy",
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "check-mode-policy",
            "service": "test-service",
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    # In check mode, should report changed but not actually create
    assert result["changed"] is True

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="check-mode-policy",
    )
    mock_create_policy.assert_not_called()


def test_ranger_policy_module_check_mode_update(module_args, mocker):
    """Test RangerPolicyModule in check mode for update."""
    new_description = "Updated in check mode"

    existing_policy = RangerPolicy(
        id=1,
        name="existing-policy",
        service="test-service",
        description="Old description",
        resources={
            "path": RangerPolicyResource(values=["/tmp/test"]),
        },
    )

    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=existing_policy,
    )
    mock_update_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.update_policy",
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "existing-policy",
            "service": "test-service",
            "description": new_description,
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    # In check mode, should report changed but not actually update
    assert result["changed"] is True

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="existing-policy",
    )
    mock_update_policy.assert_not_called()


def test_ranger_policy_module_check_mode_delete(module_args, mocker):
    """Test RangerPolicyModule in check mode for delete."""
    existing_policy = RangerPolicy(
        id=1,
        name="policy-to-delete",
        service="test-service",
        resources={
            "path": RangerPolicyResource(values=["/tmp/test"]),
        },
    )

    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=existing_policy,
    )
    mock_delete_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.delete_policy_by_id",
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "absent",
            "name": "policy-to-delete",
            "service": "test-service",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    # In check mode, should report changed but not actually delete
    assert result["changed"] is True

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="policy-to-delete",
    )
    mock_delete_policy.assert_not_called()


def test_ranger_policy_module_with_policy_items(module_args, mocker):
    """Test RangerPolicyModule creating a policy with policy items."""
    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=None,
    )
    mock_create_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.create_policy",
        return_value=RangerPolicy(
            id=1,
            name="policy-with-items",
            service="test-service",
            resources={
                "path": RangerPolicyResource(values=["/tmp/test"]),
            },
            policy_items=[
                {
                    "accesses": [
                        {"type": "read", "is_allowed": True},
                        {"type": "write", "is_allowed": True},
                    ],
                    "users": ["test_user"],
                    "groups": ["test_group"],
                },
            ],
        ),
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "policy-with-items",
            "service": "test-service",
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
            "policy_items": [
                {
                    "accesses": [
                        {"type": "read", "is_allowed": True},
                        {"type": "write", "is_allowed": True},
                    ],
                    "users": ["test_user"],
                    "groups": ["test_group"],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value

    assert result["changed"] is True
    assert result["policy"]["name"] == "policy-with-items"
    assert len(result["policy"]["policy_items"]) > 0
    assert "test_user" in result["policy"]["policy_items"][0]["users"]

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="policy-with-items",
    )
    mock_create_policy.assert_called_once()


def test_ranger_policy_module_update_with_diff(module_args, mocker):
    """Test RangerPolicyModule updating policy with diff mode."""
    new_description = "Updated description with diff"

    existing_policy = RangerPolicy(
        id=1,
        name="policy-to-update",
        service="test-service",
        description="Old description",
        resources={
            "path": RangerPolicyResource(values=["/tmp/test"]),
        },
    )

    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=existing_policy,
    )
    mock_update_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.update_policy",
        return_value=RangerPolicy(
            id=1,
            name="policy-to-update",
            service="test-service",
            description=new_description,
            resources={
                "path": RangerPolicyResource(values=["/tmp/test"]),
            },
        ),
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "policy-to-update",
            "service": "test-service",
            "description": new_description,
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True
    assert "diff" in result
    assert "before" in result["diff"]
    assert "after" in result["diff"]

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="policy-to-update",
    )
    mock_update_policy.assert_called_once()


def test_ranger_policy_module_create_with_diff(module_args, mocker):
    """Test RangerPolicyModule creating policy with diff mode."""
    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=None,
    )
    mock_create_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.create_policy",
        return_value=RangerPolicy(
            id=1,
            name="new-policy-with-diff",
            service="test-service",
            description="Test policy",
            resources={
                "path": RangerPolicyResource(values=["/tmp/test"]),
            },
        ),
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "present",
            "name": "new-policy-with-diff",
            "service": "test-service",
            "description": "Test policy",
            "resources": {
                "path": {"values": ["/tmp/test"]},
            },
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value

    assert result["changed"] is True
    assert "diff" in result
    assert result["diff"]["before"] == {}
    assert "name" in result["diff"]["after"]

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="new-policy-with-diff",
    )
    mock_create_policy.assert_called_once()


def test_ranger_policy_module_delete_with_diff(module_args, mocker):
    """Test RangerPolicyModule deleting policy with diff mode."""
    existing_policy = RangerPolicy(
        id=1,
        name="policy-to-delete",
        service="test-service",
        resources={
            "path": RangerPolicyResource(values=["/tmp/test"]),
        },
    )

    mock_get_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.get_policy_by_name",
        return_value=existing_policy,
    )
    mock_delete_policy = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_policy.RangerPolicyClient.delete_policy_by_id",
    )

    module_args(
        {
            "url": BASE_URL,
            "url_username": "admin",
            "url_password": "admin",
            "state": "absent",
            "name": "policy-to-delete",
            "service": "test-service",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True
    assert "diff" in result
    assert "before" in result["diff"]
    assert result["diff"]["after"] == {}

    mock_get_policy.assert_called_once_with(
        service_name="test-service",
        policy_name="policy-to-delete",
    )
    mock_delete_policy.assert_called_once_with(1)

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
import random

from typing import Callable

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger_policy
from ansible_collections.cloudera.services.plugins.module_utils.common import from_dict
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyResource,
    RangerPolicyItem,
    RangerPolicyItemAccess,
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
            "validate_certs": env_context.get("RANGER_VALIDATE_CERTS", "false").lower()
            == "true",
            "force_basic_auth": True,
        }
        if overrides:
            args.update(overrides)
        module_args(args)

    return _ranger_module_args


@pytest.fixture
def create_test_policy(policy_client) -> Callable:
    """Fixture factory to create test policies with common configuration."""

    def _create_test_policy(
        name: str,
        service: str,
        random_suffix: int,
        description: str = None,
        policy_items: list = None,
    ) -> RangerPolicy:
        """Create a test policy and return it."""
        policy_config = {
            "name": name,
            "service": service,
            "resources": {
                "path": RangerPolicyResource(
                    values=[f"/tmp/test-{random_suffix}"],
                ),
            },
        }

        if description:
            policy_config["description"] = description

        if policy_items:
            policy_config["policy_items"] = policy_items

        initial_policy = RangerPolicy(**policy_config)
        created_policy = policy_client.create_policy(initial_policy)
        return created_policy

    return _create_test_policy


def test_ranger_policy_module_create_minimal_int(
    ranger_module_args,
    test_service,
    purge_policy,
    policy_client,
):
    """Test RangerPolicyModule creating a policy with minimal parameters (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "resources": {
                "path": {"values": [f"/tmp/test-{random_suffix}"]},
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    purge_policy(from_dict(RangerPolicy, result["policy"]))

    assert result["changed"] is True
    assert result["policy"]["name"] == policy_name
    assert result["policy"]["service"] == test_service
    assert "id" in result["policy"]
    assert result["policy"]["id"] is not None


def test_ranger_policy_module_create_with_description_int(
    ranger_module_args,
    test_service,
    purge_policy,
    policy_client,
):
    """Test RangerPolicyModule creating a policy with description (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"
    description = "Test policy with description from integration test"

    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "description": description,
            "resources": {
                "path": {"values": [f"/tmp/test-{random_suffix}"]},
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    purge_policy(from_dict(RangerPolicy, result["policy"]))

    assert result["changed"] is True
    assert result["policy"]["name"] == policy_name
    assert result["policy"]["description"] == description


def test_ranger_policy_module_present_idempotent_int(
    ranger_module_args,
    existing_policy,
):
    """Test RangerPolicyModule with existing policy is idempotent (integration)."""

    ranger_module_args(
        {
            "state": "present",
            "name": existing_policy.name,
            "service": existing_policy.service,
            "resources": existing_policy.resources,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is False
    assert result["policy"]["id"] == existing_policy.id
    assert result["policy"]["name"] == existing_policy.name


def test_ranger_policy_module_update_description_int(
    ranger_module_args,
    deletable_policy,
):
    """Test RangerPolicyModule updating policy description (integration)."""
    new_description = "Updated description for integration testing"

    ranger_module_args(
        {
            "state": "present",
            "name": deletable_policy.name,
            "service": deletable_policy.service,
            "description": new_description,
            "resources": deletable_policy.resources,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True
    assert result["policy"]["description"] == new_description


def test_ranger_policy_module_delete_policy_int(ranger_module_args, deletable_policy):
    """Test RangerPolicyModule deleting a policy (integration)."""

    ranger_module_args(
        {
            "state": "absent",
            "name": deletable_policy.name,
            "service": deletable_policy.service,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True


def test_ranger_policy_module_delete_nonexistent_policy_int(
    ranger_module_args,
    test_service,
):
    """Test RangerPolicyModule deleting a nonexistent policy is idempotent (integration)."""

    ranger_module_args(
        {
            "state": "absent",
            "name": "nonexistent-policy-12345",
            "service": test_service,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is False


def test_ranger_policy_module_with_policy_items_int(
    ranger_module_args,
    test_service,
    purge_policy,
):
    """Test RangerPolicyModule creating a policy with policy items (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "resources": {
                "path": {"values": [f"/tmp/test-{random_suffix}"]},
            },
            "policy_items": [
                {
                    "accesses": [
                        {"type": "read", "is_allowed": True},
                        {"type": "write", "is_allowed": True},
                    ],
                    "users": ["admin"],
                    "groups": ["public"],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    purge_policy(from_dict(RangerPolicy, result["policy"]))

    assert result["changed"] is True
    assert result["policy"]["name"] == policy_name
    assert len(result["policy"]["policy_items"]) > 0
    assert "admin" in result["policy"]["policy_items"][0]["users"]


def test_ranger_policy_module_update_with_diff_int(
    ranger_module_args,
    deletable_policy,
):
    """Test RangerPolicyModule updating policy with diff mode (integration)."""
    new_description = "Updated description with diff for integration"

    ranger_module_args(
        {
            "state": "present",
            "name": deletable_policy.name,
            "service": deletable_policy.service,
            "description": new_description,
            "resources": deletable_policy.resources,
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
    # Verify the description changed
    assert result["diff"]["after"]["description"] == new_description


def test_ranger_policy_module_create_with_diff_int(
    ranger_module_args,
    test_service,
    purge_policy,
):
    """Test RangerPolicyModule creating policy with diff mode (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "description": "Test policy for diff",
            "resources": {
                "path": {"values": [f"/tmp/test-{random_suffix}"]},
            },
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    purge_policy(from_dict(RangerPolicy, result["policy"]))

    assert result["changed"] is True
    assert "diff" in result
    assert result["diff"]["before"] == {}
    assert "name" in result["diff"]["after"]
    assert result["diff"]["after"]["name"] == policy_name


def test_ranger_policy_module_delete_with_diff_int(
    ranger_module_args,
    deletable_policy,
):
    """Test RangerPolicyModule deleting policy with diff mode (integration)."""

    ranger_module_args(
        {
            "state": "absent",
            "name": deletable_policy.name,
            "service": deletable_policy.service,
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
    assert result["diff"]["before"]["name"] == deletable_policy.name


def test_ranger_policy_module_check_mode_no_create_int(
    ranger_module_args,
    test_service,
    policy_client,
):
    """Test RangerPolicyModule in check mode doesn't actually create (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "resources": {
                "path": {"values": [f"/tmp/test-{random_suffix}"]},
            },
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True

    # Verify policy was NOT actually created
    created_policy = policy_client.get_policy_by_name(
        service_name=test_service,
        policy_name=policy_name,
    )
    assert created_policy is None


def test_ranger_policy_module_check_mode_no_delete_int(
    ranger_module_args,
    existing_policy,
    policy_client,
):
    """Test RangerPolicyModule in check mode doesn't actually delete (integration)."""

    ranger_module_args(
        {
            "state": "absent",
            "name": existing_policy.name,
            "service": existing_policy.service,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True

    # Verify policy was NOT actually deleted
    still_exists = policy_client.get_policy_by_id(existing_policy.id)
    assert still_exists is not None
    assert still_exists.id == existing_policy.id


def test_ranger_policy_module_complex_policy_int(
    ranger_module_args,
    test_service,
    purge_policy,
):
    """Test RangerPolicyModule with complex policy configuration (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "description": "Complex policy test",
            "is_enabled": True,
            "is_audit_enabled": True,
            "resources": {
                "path": {
                    "values": [
                        f"/tmp/test-{random_suffix}/dir1",
                        f"/tmp/test-{random_suffix}/dir2",
                    ],
                    "is_excludes": False,
                    "is_recursive": True,
                },
            },
            "policy_items": [
                {
                    "accesses": [
                        {"type": "read", "is_allowed": True},
                        {"type": "write", "is_allowed": True},
                        {"type": "execute", "is_allowed": True},
                    ],
                    "users": ["admin", "admin"],
                    "groups": ["public"],
                    "delegate_admin": False,
                },
            ],
            "deny_policy_items": [
                {
                    "accesses": [
                        {"type": "write", "is_allowed": True},
                    ],
                    "users": ["admin"],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    purge_policy(from_dict(RangerPolicy, result["policy"]))

    assert result["changed"] is True
    assert result["policy"]["name"] == policy_name
    assert result["policy"]["description"] == "Complex policy test"
    assert result["policy"]["is_enabled"] is True
    assert result["policy"]["is_audit_enabled"] is True
    assert len(result["policy"]["policy_items"]) > 0
    assert len(result["policy"]["deny_policy_items"]) > 0
    assert "admin" in result["policy"]["policy_items"][0]["users"]
    assert "admin" in result["policy"]["deny_policy_items"][0]["users"]


def test_ranger_policy_module_merged_add_user_int(
    ranger_module_args,
    test_service,
    purge_policy,
    create_test_policy,
):
    """Test RangerPolicyModule merged mode adding a user to existing policy (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    # Create initial policy with one user
    policy_items = [
        RangerPolicyItem(
            accesses=[
                RangerPolicyItemAccess(type="read", is_allowed=True),
            ],
            users=["kudu"],
        ),
    ]

    created_policy = create_test_policy(
        name=policy_name,
        service=test_service,
        random_suffix=random_suffix,
        policy_items=policy_items,
    )
    purge_policy(created_policy)

    # Use merged mode to add another user
    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "merged": True,
            "policy_items": [
                {
                    "users": ["kafka"],
                    "groups": ["public"],
                    "accesses": [
                        {"type": "read", "is_allowed": True},
                    ],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True

    # Verify both users are present in a single merged policy item
    assert (
        len(result["policy"]["policy_items"]) == 1
    ), f"Expected 1 policy item after merged, found {len(result['policy']['policy_items'])}"

    policy_item = result["policy"]["policy_items"][0]
    assert "users" in policy_item

    users = policy_item["users"]
    # Both original user (kudu) and new user (kafka) should be present in the same item
    assert "kudu" in users
    assert "kafka" in users


def test_ranger_policy_module_merged_idempotent_int(
    ranger_module_args,
    test_service,
    purge_policy,
    create_test_policy,
):
    """Test RangerPolicyModule merged mode is idempotent when no changes needed (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    # Create initial policy
    policy_items = [
        RangerPolicyItem(
            accesses=[
                RangerPolicyItemAccess(type="read", is_allowed=True),
            ],
            users=["admin"],
        ),
    ]

    created_policy = create_test_policy(
        name=policy_name,
        service=test_service,
        random_suffix=random_suffix,
        description="Test merged idempotent",
        policy_items=policy_items,
    )
    purge_policy(created_policy)

    # Run merged with same data (should be idempotent)
    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "merged": True,
            "description": "Test merged idempotent",
            "policy_items": [
                {
                    "users": ["admin"],
                    "accesses": [
                        {"type": "read", "is_allowed": True},
                    ],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    # Should not be changed since data is already present
    assert result["changed"] is False


def test_ranger_policy_module_replace_mode_overwrites_int(
    ranger_module_args,
    test_service,
    purge_policy,
    create_test_policy,
):
    """Test RangerPolicyModule replace mode (default) overwrites existing users (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    # Create initial policy with one user
    policy_items = [
        RangerPolicyItem(
            accesses=[
                RangerPolicyItemAccess(type="read", is_allowed=True),
            ],
            users=["kudu"],
        ),
    ]

    created_policy = create_test_policy(
        name=policy_name,
        service=test_service,
        random_suffix=random_suffix,
        policy_items=policy_items,
    )
    purge_policy(created_policy)

    # Use replace mode (default) to set different user
    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "merged": False,  # Explicitly set to false (default)
            "policy_items": [
                {
                    "users": ["kafka"],
                    "accesses": [
                        {"type": "write", "is_allowed": True},
                    ],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True

    # Verify only kafka is present (kudu was replaced)
    assert len(result["policy"]["policy_items"]) > 0
    all_users = []
    for item in result["policy"]["policy_items"]:
        if "users" in item and item["users"]:
            all_users.extend(item["users"])

    assert "kafka" in all_users
    assert "kudu" not in all_users  # Original user should be gone


def test_ranger_policy_module_merged_update_description_int(
    ranger_module_args,
    test_service,
    purge_policy,
    create_test_policy,
):
    """Test RangerPolicyModule merged mode updating description (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    # Create initial policy
    created_policy = create_test_policy(
        name=policy_name,
        service=test_service,
        random_suffix=random_suffix,
        description="Original description",
    )
    purge_policy(created_policy)

    # Use merged mode to update description
    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "merged": True,
            "description": "Updated description via merged",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True
    assert result["policy"]["description"] == "Updated description via merged"


def test_ranger_policy_module_merged_check_mode_int(
    ranger_module_args,
    test_service,
    purge_policy,
    policy_client,
    create_test_policy,
):
    """Test RangerPolicyModule merged mode in check mode doesn't actually update (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    # Create initial policy
    policy_items = [
        RangerPolicyItem(
            accesses=[
                RangerPolicyItemAccess(type="read", is_allowed=True),
            ],
            users=["admin"],
        ),
    ]

    created_policy = create_test_policy(
        name=policy_name,
        service=test_service,
        random_suffix=random_suffix,
        description="Original description",
        policy_items=policy_items,
    )
    purge_policy(created_policy)

    # Use merged mode in check mode
    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "merged": True,
            "description": "Updated description",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_policy.main()

    result = e.value
    assert result["changed"] is True

    # Verify policy was NOT actually updated
    fetched_policy = policy_client.get_policy_by_name(
        service_name=test_service,
        policy_name=policy_name,
    )
    assert fetched_policy.description == "Original description"


def test_ranger_policy_module_merged_with_diff_int(
    ranger_module_args,
    test_service,
    purge_policy,
    create_test_policy,
):
    """Test RangerPolicyModule merged mode with diff output (integration)."""
    random_suffix = random.randint(1000, 9999)
    policy_name = f"test-policy-{random_suffix}"

    # Create initial policy
    created_policy = create_test_policy(
        name=policy_name,
        service=test_service,
        random_suffix=random_suffix,
        description="Original",
    )
    purge_policy(created_policy)

    # Use merged mode with diff
    ranger_module_args(
        {
            "state": "present",
            "name": policy_name,
            "service": test_service,
            "merged": True,
            "description": "Updated",
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
    assert result["diff"]["after"]["description"] == "Updated"

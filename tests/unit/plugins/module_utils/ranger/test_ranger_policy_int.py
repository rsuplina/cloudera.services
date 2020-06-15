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

from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyItem,
    RangerPolicyItemAccess,
    RangerPolicyResource,
)
from ansible_collections.cloudera.services.tests.unit import (
    AnsibleFailJson,
)

REQUIRED_ENV_VARS = [
    "RANGER_ADMIN_URL",
    "RANGER_ADMIN_USERNAME",
    "RANGER_ADMIN_PASSWORD",
]


def test_list_policies(policy_client, existing_policy):
    """Test listing all policies."""
    response = policy_client.list_policies()

    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], RangerPolicy)
    assert any(policy.id == existing_policy.id for policy in response)


def test_list_policies_by_service(policy_client, existing_policy):
    """Test listing policies filtered by service name."""
    response = policy_client.list_policies(service_name=existing_policy.service)

    assert isinstance(response, list)
    assert len(response) > 0
    assert all(policy.service == existing_policy.service for policy in response)


def test_get_policy_by_id(policy_client, existing_policy):
    """Test getting a policy by ID."""
    response = policy_client.get_policy_by_id(policy_id=existing_policy.id)

    assert isinstance(response, RangerPolicy)
    assert response.id == existing_policy.id
    assert response.name == existing_policy.name
    assert response.service == existing_policy.service


def test_get_policy_by_id_not_found(policy_client):
    """Test getting a non-existent policy by ID."""
    response = policy_client.get_policy_by_id(policy_id=999999)

    assert response is None


def test_get_policy_by_name(policy_client, existing_policy):
    """Test getting a policy by service name and policy name."""
    response = policy_client.get_policy_by_name(
        service_name=existing_policy.service,
        policy_name=existing_policy.name,
    )

    assert isinstance(response, RangerPolicy)
    assert response.name == existing_policy.name
    assert response.service == existing_policy.service


def test_get_policy_by_name_not_found(policy_client):
    """Test getting a non-existent policy by name."""
    response = policy_client.get_policy_by_name(
        service_name="cm_hdfs",
        policy_name="non-existent-policy-12345",
    )

    assert response is None


def test_create_policy_minimal(policy_client, test_service, purge_policy):
    """Test creating a policy with minimal parameters."""
    policy_name = "ansible-test-minimal"

    # Create the policy
    policy = RangerPolicy(
        name=policy_name,
        service=test_service,
        resources={
            "path": RangerPolicyResource(
                values=["/tmp/ansible-test-minimal"],
            ),
        },
    )
    response = policy_client.create_policy(policy)

    # Set up for cleanup
    purge_policy(response)

    assert isinstance(response, RangerPolicy)
    assert response.name == policy_name
    assert response.service == test_service
    assert response.id is not None
    assert response.guid is not None


def test_create_policy_with_resources(policy_client, test_service, purge_policy):
    """Test creating a policy with resource definitions."""
    policy_name = "ansible-test-resources"

    # Create the policy
    policy = RangerPolicy(
        name=policy_name,
        service=test_service,
        description="Test policy with resources",
        resources={
            "path": RangerPolicyResource(
                values=["/tmp/ansible-test"],
                is_excludes=False,
                is_recursive=False,
            ),
        },
    )
    response = policy_client.create_policy(policy)

    # Set up for cleanup
    purge_policy(response)

    assert isinstance(response, RangerPolicy)
    assert response.name == policy_name
    assert response.description == "Test policy with resources"
    assert "path" in response.resources


def test_create_policy_with_access_items(policy_client, test_service, purge_policy):
    """Test creating a policy with access policy items."""
    policy_name = "ansible-test-access-items"

    # Create the policy
    policy = RangerPolicy(
        name=policy_name,
        service=test_service,
        resources={
            "path": RangerPolicyResource(
                values=["/tmp/ansible-test-access"],
            ),
        },
        policy_items=[
            RangerPolicyItem(
                accesses=[
                    RangerPolicyItemAccess(type="read", is_allowed=True),
                    RangerPolicyItemAccess(type="write", is_allowed=True),
                ],
                users=["admin"],
                groups=["public"],
            ),
        ],
    )
    response = policy_client.create_policy(policy)

    # Set up for cleanup
    purge_policy(response)

    assert isinstance(response, RangerPolicy)
    assert response.name == policy_name
    assert len(response.policy_items) > 0
    assert "admin" in response.policy_items[0]["users"]


def test_update_policy(policy_client, deletable_policy):
    """Test updating an existing policy."""

    # Update the policy description
    deletable_policy.description = "Updated description via integration test"
    response = policy_client.update_policy(deletable_policy)

    assert isinstance(response, RangerPolicy)
    assert response.id == deletable_policy.id
    assert response.description == "Updated description via integration test"

    # Verify by fetching the policy again
    fetched = policy_client.get_policy_by_id(response.id)
    assert fetched.description == "Updated description via integration test"


def test_update_policy_add_access_items(policy_client, deletable_policy):
    """Test updating a policy by adding access items."""

    # Add new access items
    deletable_policy.policy_items = [
        RangerPolicyItem(
            accesses=[
                RangerPolicyItemAccess(type="read", is_allowed=True),
            ],
            users=["admin"],
            groups=["public"],
        ),
    ]
    response = policy_client.update_policy(deletable_policy)

    assert isinstance(response, RangerPolicy)
    assert len(response.policy_items) > 0


def test_delete_policy_by_id(policy_client, deletable_policy):
    """Test deleting a policy by ID."""

    policy_id = deletable_policy.id

    # Delete the policy
    response = policy_client.delete_policy_by_id(policy_id)
    assert response is None

    # Verify the policy is deleted
    fetched = policy_client.get_policy_by_id(policy_id)
    assert fetched is None


def test_delete_policy_by_id_not_found(policy_client):
    """Test deleting a non-existent policy by ID."""

    # This should not raise an error (squelched 404)
    response = policy_client.delete_policy_by_id(policy_id=999999)
    assert response is None

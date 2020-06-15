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
)

REQUIRED_ENV_VARS = [
    "RANGER_ADMIN_URL",
    "RANGER_ADMIN_USERNAME",
    "RANGER_ADMIN_PASSWORD",
]


def test_list_all_policies(policy_client):
    """Test listing all policies without filters."""
    response = policy_client.list_policies()

    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], RangerPolicy)


def test_list_policies_by_service(policy_client, existing_policy):
    """Test listing policies filtered by service name."""
    response = policy_client.list_policies(service_name=existing_policy.service)

    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], RangerPolicy)

    # Verify all returned policies belong to the specified service
    assert all(p.service == existing_policy.service for p in response)

    # Verify that the existing policy is in the list
    policy_names = [p.name for p in response]
    assert existing_policy.name in policy_names


def test_list_policies_by_nonexistent_service(policy_client):
    """Test listing policies for a service that doesn't exist."""
    response = policy_client.list_policies(service_name="nonexistent-service-12345")

    # Should return an empty list, not raise an error
    assert isinstance(response, list)
    assert len(response) == 0


def test_get_policy_by_id_found(policy_client, existing_policy):
    """Test getting a specific policy by ID when it exists."""
    response = policy_client.get_policy_by_id(policy_id=existing_policy.id)

    assert isinstance(response, RangerPolicy)
    assert response.id == existing_policy.id
    assert response.name == existing_policy.name
    assert response.service == existing_policy.service
    assert response.guid is not None
    assert response.version is not None


def test_get_policy_by_id_not_found(policy_client):
    """Test getting a policy by ID when it doesn't exist."""
    response = policy_client.get_policy_by_id(policy_id=999999)

    # Should return None, not raise an error
    assert response is None


def test_get_policy_by_name_found(policy_client, existing_policy):
    """Test getting a policy by service name and policy name when it exists."""
    response = policy_client.get_policy_by_name(
        service_name=existing_policy.service,
        policy_name=existing_policy.name,
    )

    assert isinstance(response, RangerPolicy)
    assert response.name == existing_policy.name
    assert response.service == existing_policy.service
    assert response.id == existing_policy.id


def test_get_policy_by_name_not_found(policy_client):
    """Test getting a policy by name when it doesn't exist."""
    response = policy_client.get_policy_by_name(
        service_name="cm_hdfs",
        policy_name="nonexistent-policy-12345",
    )

    # Should return None, not raise an error
    assert response is None


def test_get_policy_by_name_wrong_service(policy_client, existing_policy):
    """Test getting a policy by name with wrong service."""
    response = policy_client.get_policy_by_name(
        service_name="wrong-service",
        policy_name=existing_policy.name,
    )

    # Should return None because the policy doesn't exist in that service
    assert response is None


def test_policy_has_all_attributes(policy_client, existing_policy):
    """Test that a retrieved policy has all expected attributes."""
    response = policy_client.get_policy_by_id(policy_id=existing_policy.id)

    assert response is not None

    # Check required attributes
    assert hasattr(response, "id")
    assert hasattr(response, "guid")
    assert hasattr(response, "name")
    assert hasattr(response, "service")
    assert hasattr(response, "service_type")
    assert hasattr(response, "is_enabled")
    assert hasattr(response, "is_audit_enabled")
    assert hasattr(response, "policy_type")
    assert hasattr(response, "resources")

    # Check that ID and GUID are not None
    assert response.id is not None
    assert response.guid is not None

    # Check metadata fields
    assert hasattr(response, "created_by")
    assert hasattr(response, "updated_by")
    assert hasattr(response, "create_time")
    assert hasattr(response, "update_time")
    assert hasattr(response, "version")


def test_list_multiple_services(policy_client, test_service):
    """Test listing policies from multiple services."""

    # List policies from the test service
    hdfs_policies = policy_client.list_policies(service_name=test_service)

    # List all policies
    all_policies = policy_client.list_policies()

    # Verify that all policies includes policies from the test service
    assert len(all_policies) >= len(hdfs_policies)

    # Verify that HDFS policies are a subset of all policies
    hdfs_policy_ids = {p.id for p in hdfs_policies}
    all_policy_ids = {p.id for p in all_policies}
    assert hdfs_policy_ids.issubset(all_policy_ids)


def test_policy_resources_structure(policy_client, existing_policy):
    """Test that policy resources have the correct structure."""
    response = policy_client.get_policy_by_id(policy_id=existing_policy.id)

    assert response is not None
    assert response.resources is not None

    # Resources should be a dictionary
    assert isinstance(response.resources, dict)

    # Each resource should have the expected structure
    for resource_name, resource in response.resources.items():
        # Resources can be either dicts or dataclass instances
        if isinstance(resource, dict):
            assert "values" in resource
            assert isinstance(resource["values"], list)
        else:
            assert hasattr(resource, "values")
            assert isinstance(resource.values, list)

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

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    from_dict,
    ServicesClient,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerPolicy,
    RangerPolicyItem,
    RangerPolicyItemAccess,
    RangerPolicyResource,
    RangerPolicyClient,
    merge_policies,
)

ENDPOINT_URL = "https://ranger.internal"

POLICY_RESOURCE = {
    "path": {
        "values": ["/tmp/test"],
        "is_excludes": False,
        "is_recursive": False,
    },
}

POLICY_ACCESS = {
    "type": "read",
    "is_allowed": True,
}

POLICY_ITEM = {
    "accesses": [POLICY_ACCESS],
    "users": ["admin", "test_user"],
    "groups": ["public"],
    "roles": [],
    "conditions": [],
    "delegate_admin": False,
}

POLICY_MINIMAL = {
    "id": 100,
    "guid": "policy-guid-100",
    "name": "test-policy",
    "service": "test-service",
    "service_type": "hdfs",
    "is_enabled": True,
    "is_audit_enabled": True,
    "policy_type": 0,
    "policy_priority": 0,
    "resources": POLICY_RESOURCE,
}

POLICY_FULL = {
    **POLICY_MINIMAL,
    "description": "Test policy description",
    "policy_items": [POLICY_ITEM],
    "deny_policy_items": [],
    "allow_exceptions": [],
    "deny_exceptions": [],
    "data_mask_policy_items": [],
    "row_filter_policy_items": [],
    "validity_schedules": [],
    "policy_labels": ["test"],
    "options": {},
    "zone_name": None,
    "is_deny_all_else": False,
    "version": 1,
    "create_time": 1234567890000,
    "update_time": 1234567890000,
    "created_by": "admin",
    "updated_by": "admin",
}

POLICIES_LIST = {
    "policies": [POLICY_MINIMAL, POLICY_FULL],
}


def test_list_policies_all(mocker):
    """Test listing all policies."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.list_policies()

    assert isinstance(response, list)
    assert len(response) == 2
    assert isinstance(response[0], RangerPolicy)
    assert response[0].name == "test-policy"

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params=None,
        squelch={404: {"policies": []}},
    )


def test_list_policies_by_service(mocker):
    """Test listing policies filtered by service name."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.list_policies(service_name="test-service")

    assert isinstance(response, list)
    assert len(response) == 2

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "test-service"},
        squelch={404: {"policies": []}},
    )


def test_get_policy_by_id(mocker):
    """Test getting a policy by ID."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICY_FULL

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_id(policy_id=100)

    assert isinstance(response, RangerPolicy)
    assert response.id == 100
    assert response.name == "test-policy"
    assert response.service == "test-service"

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies/100",
        passthru=[400],
    )


def test_get_policy_by_id_not_found(mocker):
    """Test getting a non-existent policy by ID."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = None

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_id(policy_id=999)

    assert response is None

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies/999",
        passthru=[400],
    )


def test_get_policy_by_name(mocker):
    """Test getting a policy by service name and policy name."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_name(
        service_name="test-service",
        policy_name="test-policy",
    )

    assert isinstance(response, RangerPolicy)
    assert response.name == "test-policy"
    assert response.service == "test-service"

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "test-service"},
        squelch={404: {"policies": []}},
    )


def test_get_policy_by_name_not_found(mocker):
    """Test getting a non-existent policy by name."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_name(
        service_name="test-service",
        policy_name="non-existent-policy",
    )

    assert response is None

    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "test-service"},
        squelch={404: {"policies": []}},
    )


def test_create_policy_minimal(mocker):
    """Test creating a policy with minimal parameters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = POLICY_MINIMAL

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    policy = RangerPolicy(
        name="test-policy",
        service="test-service",
    )

    response = client.create_policy(policy)

    # Verify response is correct type and has expected values
    assert isinstance(response, RangerPolicy)
    assert response.id == 100
    assert response.guid == "policy-guid-100"
    assert response.name == "test-policy"
    assert response.service == "test-service"
    assert response.service_type == "hdfs"
    assert response.is_enabled is True
    assert response.is_audit_enabled is True
    assert response.policy_type == 0
    assert response.policy_priority == 0

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once()
    call_args = api_client.post.call_args
    assert call_args[0][0] == "/service/plugins/policies"
    assert call_args[1]["data"]["name"] == "test-policy"
    assert call_args[1]["data"]["service"] == "test-service"


def test_create_policy_full(mocker):
    """Test creating a policy with full parameters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = POLICY_FULL

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    policy = RangerPolicy(
        name="test-policy",
        service="test-service",
        service_type="hdfs",
        description="Test policy description",
        policy_type=0,
        is_enabled=True,
        is_audit_enabled=True,
        resources={
            "path": RangerPolicyResource(
                values=["/tmp/test"],
                is_excludes=False,
                is_recursive=False,
            ),
        },
        policy_items=[
            RangerPolicyItem(
                accesses=[
                    RangerPolicyItemAccess(type="read", is_allowed=True),
                ],
                users=["admin", "test_user"],
                groups=["public"],
            ),
        ],
    )

    response = client.create_policy(policy)

    # Verify response has correct type and all expected attributes
    assert isinstance(response, RangerPolicy)
    assert response.id == 100
    assert response.guid == "policy-guid-100"
    assert response.name == "test-policy"
    assert response.service == "test-service"
    assert response.service_type == "hdfs"
    assert response.description == "Test policy description"

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once()
    call_args = api_client.post.call_args
    assert call_args[0][0] == "/service/plugins/policies"
    assert call_args[1]["data"]["name"] == "test-policy"
    assert call_args[1]["data"]["service"] == "test-service"
    assert call_args[1]["data"]["description"] == "Test policy description"
    assert call_args[1]["data"]["serviceType"] == "hdfs"
    assert call_args[1]["data"]["policyType"] == 0
    assert call_args[1]["data"]["isEnabled"] is True
    assert call_args[1]["data"]["isAuditEnabled"] is True


def test_update_policy(mocker):
    """Test updating an existing policy."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.put.return_value = POLICY_FULL

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    policy = from_dict(RangerPolicy, POLICY_FULL)
    policy.description = "Updated description"

    response = client.update_policy(policy)

    assert isinstance(response, RangerPolicy)
    assert response.id == 100

    # Verify that the put method was called with correct parameters
    api_client.put.assert_called_once()
    call_args = api_client.put.call_args
    assert call_args[0][0] == "/service/plugins/policies/100"


def test_update_policy_without_id(mocker):
    """Test updating a policy without an ID raises ValueError."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    policy = RangerPolicy(
        name="test-policy",
        service="test-service",
    )

    try:
        client.update_policy(policy)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "Cannot update a policy without an id" in str(e)


def test_delete_policy_by_id(mocker):
    """Test deleting a policy by ID."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = None

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.delete_policy_by_id(policy_id=100)

    assert response is None

    # Verify that the delete method was called with correct parameters
    api_client.delete.assert_called_once_with(
        "/service/plugins/policies/100",
        passthru=[400],
    )


def test_merge_policies_simple():
    """Test merging two policies with simple changes."""
    existing = RangerPolicy(
        id=100,
        name="test-policy",
        service="test-service",
        description="Original description",
        policy_items=[
            RangerPolicyItem(
                accesses=[RangerPolicyItemAccess(type="read", is_allowed=True)],
                users=["user1"],
                groups=["group1"],
            ),
        ],
    )

    incoming = RangerPolicy(
        name="test-policy",
        service="test-service",
        description="Updated description",
    )

    result = merge_policies(existing, incoming)

    assert result.description == "Updated description"
    # Check if policy_items[0] is a RangerPolicyItem object or dict
    if isinstance(result.policy_items[0], RangerPolicyItem):
        assert result.policy_items[0].users == ["user1"]
    else:
        assert result.policy_items[0]["users"] == ["user1"]


def test_merge_policies_add_users():
    """Test merging policies to add users to existing policy items."""
    existing = RangerPolicy(
        id=100,
        name="test-policy",
        service="test-service",
        policy_items=[
            RangerPolicyItem(
                accesses=[RangerPolicyItemAccess(type="read", is_allowed=True)],
                users=["user1"],
                groups=["group1"],
            ),
        ],
    )

    incoming = RangerPolicy(
        name="test-policy",
        service="test-service",
        policy_items=[
            RangerPolicyItem(
                accesses=[RangerPolicyItemAccess(type="read", is_allowed=True)],
                users=["user2"],
                groups=["group2"],
            ),
        ],
    )

    result = merge_policies(existing, incoming)

    # Should consolidate into one policy item with all users/groups
    assert len(result.policy_items) == 1
    # Check if policy_items[0] is a RangerPolicyItem object or dict
    if isinstance(result.policy_items[0], RangerPolicyItem):
        assert set(result.policy_items[0].users) == {"user1", "user2"}
        assert set(result.policy_items[0].groups) == {"group1", "group2"}
    else:
        assert set(result.policy_items[0]["users"]) == {"user1", "user2"}
        assert set(result.policy_items[0]["groups"]) == {"group1", "group2"}


def test_merge_policies_different_accesses():
    """Test merging policies with different access types."""
    existing = RangerPolicy(
        id=100,
        name="test-policy",
        service="test-service",
        policy_items=[
            RangerPolicyItem(
                accesses=[RangerPolicyItemAccess(type="read", is_allowed=True)],
                users=["user1"],
            ),
        ],
    )

    incoming = RangerPolicy(
        name="test-policy",
        service="test-service",
        policy_items=[
            RangerPolicyItem(
                accesses=[RangerPolicyItemAccess(type="write", is_allowed=True)],
                users=["user2"],
            ),
        ],
    )

    result = merge_policies(existing, incoming)

    # Should keep both policy items since accesses are different
    assert len(result.policy_items) == 2


def test_merge_policies_preserve_id():
    """Test that merge preserves read-only fields like id."""
    existing = RangerPolicy(
        id=100,
        guid="policy-guid-100",
        name="test-policy",
        service="test-service",
        version=5,
        resource_signature="sig123",
    )

    incoming = RangerPolicy(
        name="test-policy",
        service="test-service",
        description="New description",
    )

    result = merge_policies(existing, incoming)

    # Read-only fields should be preserved from existing
    assert result.id == 100
    assert result.guid == "policy-guid-100"
    assert result.version == 5
    assert result.resource_signature == "sig123"
    assert result.description == "New description"

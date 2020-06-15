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
    RangerPolicyClient,
)

ENDPOINT_URL = "https://ranger.internal"

POLICY_1 = {
    "id": 100,
    "guid": "policy-guid-100",
    "name": "test-policy-1",
    "service": "cm_hdfs",
    "service_type": "hdfs",
    "is_enabled": True,
    "is_audit_enabled": True,
    "policy_type": 0,
    "policy_priority": 0,
    "resources": {
        "path": {
            "values": ["/tmp/test1"],
            "is_excludes": False,
            "is_recursive": False,
        },
    },
}

POLICY_2 = {
    "id": 101,
    "guid": "policy-guid-101",
    "name": "test-policy-2",
    "service": "cm_hdfs",
    "service_type": "hdfs",
    "is_enabled": True,
    "is_audit_enabled": True,
    "policy_type": 0,
    "policy_priority": 0,
    "resources": {
        "path": {
            "values": ["/tmp/test2"],
            "is_excludes": False,
            "is_recursive": False,
        },
    },
}

POLICY_3 = {
    "id": 102,
    "guid": "policy-guid-102",
    "name": "test-policy-3",
    "service": "cm_hive",
    "service_type": "hive",
    "is_enabled": True,
    "is_audit_enabled": True,
    "policy_type": 0,
    "policy_priority": 0,
    "resources": {
        "database": {
            "values": ["default"],
            "is_excludes": False,
            "is_recursive": False,
        },
    },
}

POLICIES_LIST_ALL = {
    "policies": [POLICY_1, POLICY_2, POLICY_3],
}

POLICIES_LIST_HDFS = {
    "policies": [POLICY_1, POLICY_2],
}

POLICIES_LIST_HIVE = {
    "policies": [POLICY_3],
}


def test_list_all_policies(mocker):
    """Test listing all policies without filters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST_ALL

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.list_policies()

    assert isinstance(response, list)
    assert len(response) == 3
    assert isinstance(response[0], RangerPolicy)

    # Verify all policies are returned
    policy_names = [p.name for p in response]
    assert "test-policy-1" in policy_names
    assert "test-policy-2" in policy_names
    assert "test-policy-3" in policy_names

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
    api_client.get.return_value = POLICIES_LIST_HDFS

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.list_policies(service_name="cm_hdfs")

    assert isinstance(response, list)
    assert len(response) == 2
    assert all(p.service == "cm_hdfs" for p in response)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "cm_hdfs"},
        squelch={404: {"policies": []}},
    )


def test_get_policy_by_id_found(mocker):
    """Test getting a specific policy by ID when it exists."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICY_1

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_id(policy_id=100)

    assert isinstance(response, RangerPolicy)
    assert response.id == 100
    assert response.name == "test-policy-1"
    assert response.service == "cm_hdfs"

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies/100",
        passthru=[400],
    )


def test_get_policy_by_id_not_found(mocker):
    """Test getting a policy by ID when it doesn't exist."""

    # Mock the ServicesClient instance
    # Ranger returns HTTP 400 with "DATA_NOT_FOUND" error when policy doesn't exist
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = {
        "status": 400,
        "body": b'{"statusCode":1,"msgDesc":"Data Not Found for given Id","messageList":[{"name":"DATA_NOT_FOUND","rbKey":"xa.error.data_not_found","message":"Data not found","objectId":999}]}',
    }

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_id(policy_id=999)

    assert response is None

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies/999",
        passthru=[400],
    )


def test_get_policy_by_name_found(mocker):
    """Test getting a policy by service name and policy name when it exists."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST_HDFS

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_name(
        service_name="cm_hdfs",
        policy_name="test-policy-1",
    )

    assert isinstance(response, RangerPolicy)
    assert response.name == "test-policy-1"
    assert response.service == "cm_hdfs"

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "cm_hdfs"},
        squelch={404: {"policies": []}},
    )


def test_get_policy_by_name_not_found(mocker):
    """Test getting a policy by name when it doesn't exist."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST_HDFS

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_name(
        service_name="cm_hdfs",
        policy_name="non-existent-policy",
    )

    assert response is None

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "cm_hdfs"},
        squelch={404: {"policies": []}},
    )


def test_get_policy_by_name_different_service(mocker):
    """Test getting a policy by name from a different service."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = POLICIES_LIST_HIVE

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.get_policy_by_name(
        service_name="cm_hive",
        policy_name="test-policy-3",
    )

    assert isinstance(response, RangerPolicy)
    assert response.name == "test-policy-3"
    assert response.service == "cm_hive"

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "cm_hive"},
        squelch={404: {"policies": []}},
    )


def test_list_policies_empty_result(mocker):
    """Test listing policies when no policies exist."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = {"policies": []}

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.list_policies()

    assert isinstance(response, list)
    assert len(response) == 0

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params=None,
        squelch={404: {"policies": []}},
    )


def test_list_policies_404_squelched(mocker):
    """Test that 404 errors are properly squelched when listing policies."""

    # Mock the ServicesClient instance to return the squelched value
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = {"policies": []}

    # Create the RangerPolicyClient instance
    client = RangerPolicyClient(api_client=api_client)

    response = client.list_policies(service_name="non-existent-service")

    assert isinstance(response, list)
    assert len(response) == 0

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/policies",
        params={"serviceName": "non-existent-service"},
        squelch={404: {"policies": []}},
    )

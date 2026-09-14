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

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesClient,
    ServicesError,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerService,
    RangerServiceClient,
    _service_from_response,
    _service_to_payload,
)

ENDPOINT_URL = "https://ranger.example"

# The ``configs`` dictionary holds arbitrary connector property names (with
# dots) that must be sent to and received from Ranger verbatim.
SERVICE_CONFIGS = {
    "username": "hdfs",
    "password": "hdfs",
    "fs.default.name": "hdfs://namenode:8020",
    "hadoop.security.authentication": "simple",
    "hadoop.security.authorization": "true",
}

# Ranger returns service objects with camelCase keys.
SERVICE_RESPONSE = {
    "id": 5,
    "guid": "service-guid-5",
    "isEnabled": True,
    "createdBy": "Admin",
    "updatedBy": "Admin",
    "createTime": 1700000000000,
    "updateTime": 1700000000000,
    "version": 1,
    "type": "hdfs",
    "name": "test_service",
    "displayName": "Test Service",
    "description": "Test HDFS service",
    "tagService": "",
    "configs": SERVICE_CONFIGS,
    "policyVersion": 1,
    "policyUpdateTime": 1700000000000,
    "tagVersion": 1,
    "tagUpdateTime": 1700000000000,
}

# A Ranger 400 response with a DATA_NOT_FOUND body (Ranger's "not found" signal).
RANGER_NOT_FOUND_400 = {
    "status": 400,
    "body": {
        "statusCode": 1,
        "messageList": [{"name": "DATA_NOT_FOUND"}],
    },
}

# A Ranger 400 response for some other (non "not found") error.
RANGER_ERROR_400 = {
    "status": 400,
    "body": {
        "statusCode": 2,
        "messageList": [{"name": "VALIDATION_ERROR"}],
    },
}


def test_create_service(mocker):
    """Test creating a service serialises to a camelCase payload."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = SERVICE_RESPONSE

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.create_service(
        RangerService(
            name="test_service",
            type="hdfs",
            is_enabled=True,
            configs=SERVICE_CONFIGS,
        ),
    )

    assert response == _service_from_response(SERVICE_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/service/plugins/services",
        data={
            "name": "test_service",
            "type": "hdfs",
            "isEnabled": True,
            "configs": SERVICE_CONFIGS,
        },
    )


def test_create_service_minimal(mocker):
    """Test creating a service with only a name omits all NULLABLE fields."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = SERVICE_RESPONSE

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.create_service(RangerService(name="test_service"))

    assert isinstance(response, RangerService)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/service/plugins/services",
        data={"name": "test_service"},
    )


def test_create_service_configs_verbatim(mocker):
    """Test that dotted config keys are not camelCase-transformed on create."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = SERVICE_RESPONSE

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    client.create_service(
        RangerService(
            name="test_service",
            type="hdfs",
            configs=SERVICE_CONFIGS,
        ),
    )

    # The configs dict must be forwarded exactly, keys and all
    call_args = api_client.post.call_args
    assert call_args[1]["data"]["configs"] == SERVICE_CONFIGS
    assert "fs.default.name" in call_args[1]["data"]["configs"]


def test_update_service(mocker):
    """Test updating a service by its id."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.put.return_value = SERVICE_RESPONSE

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.update_service(
        RangerService(
            id=5,
            name="test_service",
            type="hdfs",
            is_enabled=False,
            configs=SERVICE_CONFIGS,
        ),
    )

    assert response == _service_from_response(SERVICE_RESPONSE)

    # Verify that the put method was called with correct parameters
    api_client.put.assert_called_once_with(
        "/service/plugins/services/5",
        data={
            "id": 5,
            "name": "test_service",
            "type": "hdfs",
            "isEnabled": False,
            "configs": SERVICE_CONFIGS,
        },
    )


def test_update_service_without_id(mocker):
    """Test updating a service without an id raises ValueError."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    with pytest.raises(ValueError, match="Cannot update a service without an id"):
        client.update_service(RangerService(name="test_service"))

    api_client.put.assert_not_called()


def test_delete_service_by_id(mocker):
    """Test deleting a service by id."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = None

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.delete_service_by_id(service_id=5)

    assert response is None

    # Verify that the delete method was called with correct parameters
    api_client.delete.assert_called_once_with(
        "/service/plugins/services/5",
        squelch={404: None},
        passthru=[400],
    )


def test_delete_service_by_id_not_found(mocker):
    """Test deleting a non-existent service (Ranger 400 DATA_NOT_FOUND) is a no-op."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = RANGER_NOT_FOUND_400

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.delete_service_by_id(service_id=999)

    assert response is None


def test_delete_service_by_id_error(mocker):
    """Test that a non "not found" Ranger 400 raises a ServicesError on delete."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = RANGER_ERROR_400

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    with pytest.raises(ServicesError):
        client.delete_service_by_id(service_id=5)


def test_service_to_payload_camelcase():
    """Test the payload serialisation maps snake_case fields to camelCase."""
    payload = _service_to_payload(
        RangerService(
            name="test_service",
            type="hdfs",
            display_name="Test Service",
            tag_service="cm_tag",
            is_enabled=True,
            configs=SERVICE_CONFIGS,
        ),
    )

    assert payload["name"] == "test_service"
    assert payload["type"] == "hdfs"
    assert payload["displayName"] == "Test Service"
    assert payload["tagService"] == "cm_tag"
    assert payload["isEnabled"] is True

    # Snake_case forms must not survive the transformation
    assert "display_name" not in payload
    assert "tag_service" not in payload
    assert "is_enabled" not in payload

    # Config keys must be preserved verbatim
    assert payload["configs"] == SERVICE_CONFIGS


def test_service_from_response_snakecase_and_configs_verbatim():
    """Test deserialisation maps camelCase to snake_case and keeps configs verbatim."""
    service = _service_from_response(SERVICE_RESPONSE)

    assert isinstance(service, RangerService)
    assert service.id == 5
    assert service.guid == "service-guid-5"
    assert service.name == "test_service"
    assert service.type == "hdfs"
    assert service.display_name == "Test Service"
    assert service.is_enabled is True
    assert service.created_by == "Admin"
    assert service.updated_by == "Admin"
    assert service.policy_version == 1

    # Config keys must be preserved verbatim
    assert service.configs == SERVICE_CONFIGS
    assert service.configs["fs.default.name"] == "hdfs://namenode:8020"

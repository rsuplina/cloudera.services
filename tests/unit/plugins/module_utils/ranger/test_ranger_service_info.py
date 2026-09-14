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
)

ENDPOINT_URL = "https://ranger.example"

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

SERVICES_LIST = {"services": [SERVICE_RESPONSE]}

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


def test_list_services(mocker):
    """Test listing all services."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = SERVICES_LIST

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.list_services()

    assert isinstance(response, list)
    assert len(response) == 1
    assert isinstance(response[0], RangerService)
    assert response[0] == _service_from_response(SERVICE_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/services",
        squelch={404: {"services": []}},
    )


def test_list_services_empty(mocker):
    """Test listing services when none exist."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = {"services": []}

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.list_services()

    assert response == []


def test_get_service_by_id(mocker):
    """Test getting a service by id."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = SERVICE_RESPONSE

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.get_service_by_id(service_id=5)

    assert isinstance(response, RangerService)
    assert response.id == 5
    assert response.name == "test_service"
    assert response.type == "hdfs"

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/services/5",
        squelch={404: None},
        passthru=[400],
    )


def test_get_service_by_id_not_found_squelched(mocker):
    """Test getting a non-existent service by id (squelched 404) returns None."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = None

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.get_service_by_id(service_id=999)

    assert response is None


def test_get_service_by_id_not_found_400(mocker):
    """Test getting a non-existent service by id (Ranger 400 DATA_NOT_FOUND) returns None."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = RANGER_NOT_FOUND_400

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.get_service_by_id(service_id=999)

    assert response is None


def test_get_service_by_id_error(mocker):
    """Test that a non "not found" Ranger 400 raises a ServicesError."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = RANGER_ERROR_400

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    with pytest.raises(ServicesError):
        client.get_service_by_id(service_id=5)


def test_get_service_by_name(mocker):
    """Test getting a service by name."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = SERVICE_RESPONSE

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.get_service_by_name(service_name="test_service")

    assert isinstance(response, RangerService)
    assert response.name == "test_service"
    assert response.id == 5

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/service/plugins/services/name/test_service",
        squelch={404: None},
        passthru=[400],
    )


def test_get_service_by_name_not_found_squelched(mocker):
    """Test getting a non-existent service by name (squelched 404) returns None."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = None

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.get_service_by_name(service_name="non-existent-service")

    assert response is None


def test_get_service_by_name_not_found_400(mocker):
    """Test getting a non-existent service by name (Ranger 400 DATA_NOT_FOUND) returns None."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = RANGER_NOT_FOUND_400

    # Create the RangerServiceClient instance
    client = RangerServiceClient(api_client=api_client)

    response = client.get_service_by_name(service_name="non-existent-service")

    assert response is None

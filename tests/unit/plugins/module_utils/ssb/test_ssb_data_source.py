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
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbDataSourceClient,
    SsbDataSource,
    SsbDataSourceSync,
    SsbDataSourceValidationResponse,
)

ENDPOINT_URL = "https://cloudera.internal"

DATA_SOURCE_RESPONSE = dict(
    id=123,
    name="test_data_source",
    type="KAFKA",
    properties={
        "bootstrap.servers": "localhost:9092",
        "topic": "test-topic",
    },
    created_at="2024-06-01T12:00:00Z",
    updated_at="2024-06-02T14:00:00Z",
    project_id="proj123",
)

PROJECT_ID = "proj123"


def test_create_data_source(mocker):
    """Test creating a data source with minimal parameters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = DATA_SOURCE_RESPONSE

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.create_data_source(
        project_id=PROJECT_ID,
        data_source=SsbDataSourceSync(
            name="test_data_source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "localhost:9092",
                "topic": "test-topic",
            },
        ),
    )

    assert response == from_dict(SsbDataSource, DATA_SOURCE_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources",
        data={
            "name": "test_data_source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
                "topic": "test-topic",
            },
        },
    )


def test_create_data_source_with_truststore(mocker):
    """Test creating a data source with custom truststore."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = DATA_SOURCE_RESPONSE

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.create_data_source(
        project_id=PROJECT_ID,
        data_source=SsbDataSourceSync(
            name="test_data_source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "localhost:9092",
                "topic": "test-topic",
            },
            custom_truststore="/path/to/truststore.jks",
        ),
    )

    assert response == from_dict(SsbDataSource, DATA_SOURCE_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources",
        data={
            "name": "test_data_source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
                "topic": "test-topic",
            },
            "custom_truststore": "/path/to/truststore.jks",
        },
    )


def test_describe_data_source(mocker):
    """Test describing a specific data source."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = DATA_SOURCE_RESPONSE

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.describe_data_source(project_id=PROJECT_ID, data_source_id=123)

    assert response == from_dict(SsbDataSource, DATA_SOURCE_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources/123",
        squelch={
            403: None,
            404: None,
        },
    )


def test_list_data_sources(mocker):
    """Test listing all data sources."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = [DATA_SOURCE_RESPONSE]

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.list_data_sources(project_id=PROJECT_ID)

    assert isinstance(response, list)
    assert isinstance(response[0], SsbDataSource)
    assert response[0] == from_dict(SsbDataSource, DATA_SOURCE_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources",
    )


def test_list_data_sources_kafka(mocker):
    """Test listing Kafka data sources."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = [DATA_SOURCE_RESPONSE]

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.list_data_sources(project_id=PROJECT_ID, kafka=True)

    assert isinstance(response, list)
    assert isinstance(response[0], SsbDataSource)
    assert response[0] == from_dict(SsbDataSource, DATA_SOURCE_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources/kafka",
    )


def test_update_data_source(mocker):
    """Test updating a data source."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.put.return_value = DATA_SOURCE_RESPONSE

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.update_data_source(
        project_id=PROJECT_ID,
        data_source=SsbDataSource(
            id=123,
            name="test_data_source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "localhost:9092",
                "topic": "updated-topic",
            },
        ),
    )

    assert response == from_dict(SsbDataSource, DATA_SOURCE_RESPONSE)

    # Verify that the put method was called with correct parameters
    api_client.put.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources/123",
        data={
            "id": 123,
            "name": "test_data_source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
                "topic": "updated-topic",
            },
        },
    )


def test_delete_data_source(mocker):
    """Test deleting a data source."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = None

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.delete_data_source(PROJECT_ID, 123)

    assert response is None

    # Verify that the delete method was called with correct parameters
    api_client.delete.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources/123",
        params={"delete_dependents": False},
        squelch={
            403: {},
            404: {},
        },
    )


def test_delete_data_source_with_dependents(mocker):
    """Test deleting a data source with dependents."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = None

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.delete_data_source(PROJECT_ID, 123, delete_dependents=True)

    assert response is None

    # Verify that the delete method was called with correct parameters
    api_client.delete.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources/123",
        params={"delete_dependents": True},
        squelch={
            403: {},
            404: {},
        },
    )


def test_validate_data_source(mocker):
    """Test validating a data source configuration."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = {
        "number_of_tables": 5,
    }

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.validate_data_source(
        project_id=PROJECT_ID,
        data_source=SsbDataSourceSync(
            name="test_data_source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "localhost:9092",
                "topic": "test-topic",
            },
        ),
    )

    assert isinstance(response, SsbDataSourceValidationResponse)
    assert response.number_of_tables == 5

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources/validate",
        data={
            "name": "test_data_source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
                "topic": "test-topic",
            },
        },
    )


def test_validate_data_source_with_error(mocker):
    """Test validating a data source configuration that has errors."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = {
        "error": "Connection failed: Invalid credentials",
    }

    # Create the SsbDataSourceClient instance
    client = SsbDataSourceClient(api_client=api_client)

    response = client.validate_data_source(
        project_id=PROJECT_ID,
        data_source=SsbDataSourceSync(
            name="test_data_source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "invalid:9092",
                "topic": "test-topic",
            },
        ),
    )

    assert isinstance(response, SsbDataSourceValidationResponse)
    assert response.error == "Connection failed: Invalid credentials"

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/data-sources/validate",
        data={
            "name": "test_data_source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "invalid:9092",
                "topic": "test-topic",
            },
        },
    )

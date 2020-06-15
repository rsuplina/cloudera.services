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
    SsbTableClient,
    SsbTable,
)

ENDPOINT_URL = "https://cloudera.internal"

TABLE_RESPONSE = dict(
    id=123,
    table_name="test_table",
    type="KAFKA",
    metadata={
        "connector": "kafka",
        "format": "json",
        "topic": "test-topic",
    },
    project_id="proj123",
    created_at="2024-06-01T12:00:00Z",
)

PROJECT_ID = "proj123"


def test_create_table(mocker):
    """Test creating a table with minimal parameters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = TABLE_RESPONSE

    # Create the SsbTableClient instance
    client = SsbTableClient(api_client=api_client)

    response = client.create_table(
        project_id=PROJECT_ID,
        table=SsbTable(
            table_name="test_table",
            type="KAFKA",
            metadata={
                "connector": "kafka",
                "format": "json",
                "topic": "test-topic",
            },
        ),
    )

    assert response == from_dict(SsbTable, TABLE_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/tables",
        data={
            "table_name": "test_table",
            "type": "KAFKA",
            "metadata": {
                "connector": "kafka",
                "format": "json",
                "topic": "test-topic",
            },
        },
    )


def test_create_table_with_transform(mocker):
    """Test creating a table with transform code."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = TABLE_RESPONSE

    # Create the SsbTableClient instance
    client = SsbTableClient(api_client=api_client)

    response = client.create_table(
        project_id=PROJECT_ID,
        table=SsbTable(
            table_name="test_table",
            type="KAFKA",
            metadata={
                "connector": "kafka",
                "format": "json",
                "topic": "test-topic",
            },
            transform_code="SELECT * FROM source",
            transform_code_b64_encoded=False,
        ),
    )

    assert response == from_dict(SsbTable, TABLE_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/tables",
        data={
            "table_name": "test_table",
            "type": "KAFKA",
            "metadata": {
                "connector": "kafka",
                "format": "json",
                "topic": "test-topic",
            },
            "transform_code": "SELECT * FROM source",
            "transform_code_b64_encoded": False,
        },
    )


def test_describe_table(mocker):
    """Test describing a specific table."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = TABLE_RESPONSE

    # Create the SsbTableClient instance
    client = SsbTableClient(api_client=api_client)

    response = client.describe_table(project_id=PROJECT_ID, table_id=123)

    assert response == from_dict(SsbTable, TABLE_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/tables/123",
        squelch={
            403: None,
            404: None,
        },
    )


def test_list_tables(mocker):
    """Test listing all tables."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = [TABLE_RESPONSE]

    # Create the SsbTableClient instance
    client = SsbTableClient(api_client=api_client)

    response = client.list_tables(project_id=PROJECT_ID)

    assert isinstance(response, list)
    assert isinstance(response[0], SsbTable)
    assert response[0] == from_dict(SsbTable, TABLE_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/tables",
    )


def test_delete_table(mocker):
    """Test deleting a table."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = None

    # Create the SsbTableClient instance
    client = SsbTableClient(api_client=api_client)

    response = client.delete_table(PROJECT_ID, 123)

    assert response is None

    # Verify that the delete method was called with correct parameters
    api_client.delete.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/tables/123",
    )

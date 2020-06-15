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
    from_dict,
    ServicesClient,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbEnvironmentClient,
    SsbEnvironment,
    SsbEnvironmentRequest,
    SsbEnvironmentSecuredProperty,
    SsbEnvironmentFile,
)

ENDPOINT_URL = "https://cloudera.internal"

ENVIRONMENT_RESPONSE = dict(
    id=123,
    name="test_environment",
    secured_props={
        "kafka.bootstrap.servers": {
            "value": "localhost:9092",
            "sensitive": False,
        },
        "kafka.password": {
            "value": "secret",
            "sensitive": True,
        },
    },
    project="proj123",
    created_at="2024-06-01T12:00:00Z",
    last_edited_at="2024-06-02T14:00:00Z",
    last_editor="testuser",
)

ENVIRONMENT_FILE_RESPONSE = dict(
    name="test_environment",
    properties={
        "kafka.bootstrap.servers": {
            "value": "localhost:9092",
            "sensitive": False,
        },
    },
    metadata={
        "project_name": "test_project",
        "checksum": "abc123",
        "exported_at": "2024-06-01T12:00:00Z",
        "last_edited_at": "2024-06-02T14:00:00Z",
        "exported_by": "testuser",
        "last_edited_by": "testuser",
        "csa_version": "1.0.0",
    },
)

PROJECT_ID = "proj123"


def test_create_environment(mocker):
    """Test creating an environment with minimal parameters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = ENVIRONMENT_RESPONSE

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.create_environment(
        project_id=PROJECT_ID,
        environment=SsbEnvironmentRequest(
            name="test_environment",
            properties={
                "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                    value="localhost:9092",
                    sensitive=False,
                ),
            },
        ),
    )

    assert response == from_dict(SsbEnvironment, ENVIRONMENT_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments",
        data={
            "name": "test_environment",
            "properties": {
                "kafka.bootstrap.servers": {
                    "value": "localhost:9092",
                    "sensitive": False,
                },
            },
        },
    )


def test_create_environment_with_sensitive_props(mocker):
    """Test creating an environment with sensitive properties."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = ENVIRONMENT_RESPONSE

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.create_environment(
        project_id=PROJECT_ID,
        environment=SsbEnvironmentRequest(
            name="test_environment",
            properties={
                "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                    value="localhost:9092",
                    sensitive=False,
                ),
                "kafka.password": SsbEnvironmentSecuredProperty(
                    value="secret",
                    sensitive=True,
                ),
            },
        ),
    )

    assert response == from_dict(SsbEnvironment, ENVIRONMENT_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments",
        data={
            "name": "test_environment",
            "properties": {
                "kafka.bootstrap.servers": {
                    "value": "localhost:9092",
                    "sensitive": False,
                },
                "kafka.password": {
                    "value": "secret",
                    "sensitive": True,
                },
            },
        },
    )


def test_describe_environment(mocker):
    """Test describing a specific environment."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = ENVIRONMENT_RESPONSE

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.describe_environment(project_id=PROJECT_ID, environment_id=123)

    assert response == from_dict(SsbEnvironment, ENVIRONMENT_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/123",
        squelch={
            403: None,
            404: None,
        },
    )


def test_list_environments(mocker):
    """Test listing all environments."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = [ENVIRONMENT_RESPONSE]

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.list_environments(project_id=PROJECT_ID)

    assert isinstance(response, list)
    assert isinstance(response[0], SsbEnvironment)
    assert response[0] == from_dict(SsbEnvironment, ENVIRONMENT_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments",
    )


def test_update_environment(mocker):
    """Test updating an environment."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.put.return_value = ENVIRONMENT_RESPONSE

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.update_environment(
        project_id=PROJECT_ID,
        environment_id=123,
        environment=SsbEnvironmentRequest(
            name="test_environment",
            properties={
                "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                    value="localhost:9093",
                    sensitive=False,
                ),
            },
        ),
    )

    assert response == from_dict(SsbEnvironment, ENVIRONMENT_RESPONSE)

    # Verify that the put method was called with correct parameters
    api_client.put.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/123",
        data={
            "name": "test_environment",
            "properties": {
                "kafka.bootstrap.servers": {
                    "value": "localhost:9093",
                    "sensitive": False,
                },
            },
        },
    )


def test_activate_environment(mocker):
    """Test activating an environment."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = None

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.activate_environment(PROJECT_ID, 123)

    assert response is None

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/123/activate",
    )


def test_deactivate_environment(mocker):
    """Test deactivating an environment."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = None

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.deactivate_environment(PROJECT_ID)

    assert response is None

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/deactivate",
    )


def test_import_environment_from_file(mocker):
    """Test importing an environment from a file path."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = ENVIRONMENT_RESPONSE

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.import_environment(
        project_id=PROJECT_ID,
        environment_file="/path/to/environment.json",
    )

    assert response == from_dict(SsbEnvironment, ENVIRONMENT_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/file",
        data={
            "file": {
                "filename": "/path/to/environment.json",
            },
        },
        format="multipart",
    )


def test_import_environment_from_data(mocker):
    """Test importing an environment from bytes data."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = ENVIRONMENT_RESPONSE

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    environment_data = b'{"name": "test_environment"}'

    response = client.import_environment(
        project_id=PROJECT_ID,
        environment_data=environment_data,
    )

    assert response == from_dict(SsbEnvironment, ENVIRONMENT_RESPONSE)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/file",
        data={
            "file": {
                "content": environment_data,
            },
        },
        format="multipart",
    )


def test_import_environment_invalid_params(mocker):
    """Test importing an environment with invalid parameters raises ValueError."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    # Test with both parameters provided
    with pytest.raises(ValueError) as excinfo:
        client.import_environment(
            project_id=PROJECT_ID,
            environment_file="/path/to/environment.json",
            environment_data=b'{"name": "test"}',
        )

    assert "Provide either environment_file or environment_data, not both" in str(
        excinfo.value,
    )

    # Test with neither parameter provided
    with pytest.raises(ValueError) as excinfo:
        client.import_environment(project_id=PROJECT_ID)

    assert "Provide either environment_file or environment_data, not both" in str(
        excinfo.value,
    )


def test_export_environment(mocker):
    """Test exporting an environment."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = ENVIRONMENT_FILE_RESPONSE

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.export_environment(project_id=PROJECT_ID, environment_id=123)

    assert isinstance(response, SsbEnvironmentFile)
    assert response == from_dict(SsbEnvironmentFile, ENVIRONMENT_FILE_RESPONSE)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/file/123",
    )


def test_delete_environment(mocker):
    """Test deleting an environment."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = None

    # Create the SsbEnvironmentClient instance
    client = SsbEnvironmentClient(api_client=api_client)

    response = client.delete_environment(PROJECT_ID, 123)

    assert response is None

    # Verify that the delete method was called with correct parameters
    api_client.delete.assert_called_once_with(
        f"/api/v2/projects/{PROJECT_ID}/environments/123",
    )

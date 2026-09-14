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

from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerService,
)

REQUIRED_ENV_VARS = [
    "RANGER_API_URL",
    "RANGER_API_USERNAME",
    "RANGER_API_PASSWORD",
]


def test_create_service(
    request,
    ranger_service_client,
    ranger_service_type,
    purge_ranger_service,
):
    """Test creating a service."""
    service_name = f"ansible-test-create-{request.node.name.lower()}"

    response = ranger_service_client.create_service(
        RangerService(
            name=service_name,
            type=ranger_service_type,
        ),
    )

    # Register the service for cleanup
    purge_ranger_service(response)

    assert isinstance(response, RangerService)
    assert response.name == service_name
    assert response.type == ranger_service_type
    assert response.id is not None
    assert response.guid is not None


def test_create_service_with_display_name(
    request,
    ranger_service_client,
    ranger_service_type,
    purge_ranger_service,
):
    """Test creating a service with a display name and description."""
    service_name = f"ansible-test-display-{request.node.name.lower()}"

    response = ranger_service_client.create_service(
        RangerService(
            name=service_name,
            type=ranger_service_type,
            display_name="Ansible Test Service",
            description="Created by an integration test",
        ),
    )

    # Register the service for cleanup
    purge_ranger_service(response)

    assert isinstance(response, RangerService)
    assert response.name == service_name
    assert response.description == "Created by an integration test"


def test_update_service(ranger_service_client, deletable_ranger_service):
    """Test updating an existing service."""

    # Update the service description
    deletable_ranger_service.description = "Updated description via integration test"
    response = ranger_service_client.update_service(deletable_ranger_service)

    assert isinstance(response, RangerService)
    assert response.id == deletable_ranger_service.id
    assert response.description == "Updated description via integration test"

    # Verify by fetching the service again
    fetched = ranger_service_client.get_service_by_id(response.id)
    assert fetched.description == "Updated description via integration test"


def test_delete_service_by_id(ranger_service_client, deletable_ranger_service):
    """Test deleting a service by id."""
    service_id = deletable_ranger_service.id

    # Delete the service
    response = ranger_service_client.delete_service_by_id(service_id)
    assert response is None

    # Verify the service no longer exists
    fetched = ranger_service_client.get_service_by_id(service_id)
    assert fetched is None


def test_delete_service_by_id_not_found(ranger_service_client):
    """Test deleting a non-existent service by id (idempotent)."""

    # This should not raise an error (Ranger 400 DATA_NOT_FOUND is squelched)
    response = ranger_service_client.delete_service_by_id(service_id=999999)
    assert response is None

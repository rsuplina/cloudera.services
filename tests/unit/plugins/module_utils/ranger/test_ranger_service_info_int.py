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


def test_list_services(ranger_service_client, existing_ranger_service):
    """Test listing all services."""
    response = ranger_service_client.list_services()

    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], RangerService)
    assert any(service.id == existing_ranger_service.id for service in response)


def test_get_service_by_id(ranger_service_client, existing_ranger_service):
    """Test getting a service by id."""
    response = ranger_service_client.get_service_by_id(
        service_id=existing_ranger_service.id,
    )

    assert isinstance(response, RangerService)
    assert response.id == existing_ranger_service.id
    assert response.name == existing_ranger_service.name


def test_get_service_by_id_not_found(ranger_service_client):
    """Test getting a non-existent service by id returns None."""
    response = ranger_service_client.get_service_by_id(service_id=999999)

    assert response is None


def test_get_service_by_name(ranger_service_client, existing_ranger_service):
    """Test getting a service by name."""
    response = ranger_service_client.get_service_by_name(
        service_name=existing_ranger_service.name,
    )

    assert isinstance(response, RangerService)
    assert response.name == existing_ranger_service.name
    assert response.id == existing_ranger_service.id


def test_get_service_by_name_not_found(ranger_service_client):
    """Test getting a non-existent service by name returns None."""
    response = ranger_service_client.get_service_by_name(
        service_name="non-existent-service-12345",
    )

    assert response is None

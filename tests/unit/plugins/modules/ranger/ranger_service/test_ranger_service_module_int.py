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

import os

from typing import Callable

import pytest

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.services.plugins.modules import ranger_service

REQUIRED_ENV_VARS = [
    "RANGER_API_URL",
    "RANGER_API_USERNAME",
    "RANGER_API_PASSWORD",
]


@pytest.fixture
def ranger_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to set common module args for Ranger service tests."""

    def _ranger_module_args(overrides: dict = {}) -> None:
        args = {
            "url": env_context["RANGER_API_URL"],
            "url_username": env_context["RANGER_API_USERNAME"],
            "url_password": env_context["RANGER_API_PASSWORD"],
            "force_basic_auth": True,
            "validate_certs": os.environ.get("RANGER_VALIDATE_CERTS", "false").lower()
            == "true",
        }
        if overrides:
            args.update(overrides)
        module_args(args)

    return _ranger_module_args


def test_ranger_service_module_create(
    request,
    ranger_module_args,
    ranger_service_client,
    ranger_service_type,
    purge_ranger_service,
):
    """Test RangerServiceModule creates a new service."""
    service_name = f"ansible-test-module-create-{request.node.name.lower()}"

    ranger_module_args(
        {
            "name": service_name,
            "type": ranger_service_type,
            "description": "Created by module integration test",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["name"] == service_name
    assert result["service"]["type"] == ranger_service_type
    assert result["service"]["id"] is not None

    # Register for cleanup
    created = ranger_service_client.get_service_by_name(service_name)
    purge_ranger_service(created)

    assert created is not None
    assert created.display_name == service_name


def test_ranger_service_module_create_check_mode(
    request,
    ranger_module_args,
    ranger_service_client,
    ranger_service_type,
):
    """Test RangerServiceModule create in check mode does not create a service."""
    service_name = f"ansible-test-module-checkmode-{request.node.name.lower()}"

    ranger_module_args(
        {
            "name": service_name,
            "type": ranger_service_type,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["name"] == service_name

    # The service must not actually exist remotely
    assert ranger_service_client.get_service_by_name(service_name) is None


def test_ranger_service_module_present_no_changes(
    ranger_module_args,
    existing_ranger_service,
):
    """Test RangerServiceModule present against an unchanged service is a no-op."""

    ranger_module_args(
        {
            "name": existing_ranger_service.name,
            "type": existing_ranger_service.type,
            "description": existing_ranger_service.description,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is False
    assert result["service"]["id"] == existing_ranger_service.id
    assert result["service"]["name"] == existing_ranger_service.name


def test_ranger_service_module_update_in_place(
    ranger_module_args,
    ranger_service_client,
    deletable_ranger_service,
):
    """Test RangerServiceModule updates an existing service in place."""

    ranger_module_args(
        {
            "name": deletable_ranger_service.name,
            "type": deletable_ranger_service.type,
            "description": "Updated by module integration test",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["id"] == deletable_ranger_service.id
    assert result["service"]["description"] == "Updated by module integration test"

    # The service id must be unchanged (updated in place, not recreated)
    fetched = ranger_service_client.get_service_by_id(deletable_ranger_service.id)
    assert fetched.id == deletable_ranger_service.id
    assert fetched.description == "Updated by module integration test"


def test_ranger_service_module_update_check_mode(
    ranger_module_args,
    ranger_service_client,
    deletable_ranger_service,
):
    """Test RangerServiceModule update in check mode does not modify the service."""

    ranger_module_args(
        {
            "name": deletable_ranger_service.name,
            "type": deletable_ranger_service.type,
            "description": "Should not be persisted",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True

    fetched = ranger_service_client.get_service_by_id(deletable_ranger_service.id)
    assert fetched.description != "Should not be persisted"


def test_ranger_service_module_delete_existing(
    ranger_module_args,
    ranger_service_client,
    deletable_ranger_service,
):
    """Test RangerServiceModule deletes an existing service."""

    ranger_module_args(
        {
            "name": deletable_ranger_service.name,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"] == {}

    assert ranger_service_client.get_service_by_id(deletable_ranger_service.id) is None


def test_ranger_service_module_delete_nonexistent(request, ranger_module_args):
    """Test RangerServiceModule delete of a nonexistent service is a no-op."""

    ranger_module_args(
        {
            "name": f"ansible-test-nonexistent-{request.node.name.lower()}",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is False
    assert result["service"] == {}


def test_ranger_service_module_delete_check_mode(
    ranger_module_args,
    ranger_service_client,
    deletable_ranger_service,
):
    """Test RangerServiceModule delete in check mode does not delete the service."""

    ranger_module_args(
        {
            "name": deletable_ranger_service.name,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True

    assert ranger_service_client.get_service_by_id(deletable_ranger_service.id) is not None

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

from ansible_collections.cloudera.services.plugins.modules import (
    ranger_service_info,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerService,
)

REQUIRED_ENV_VARS = [
    "RANGER_API_URL",
    "RANGER_API_USERNAME",
    "RANGER_API_PASSWORD",
]


@pytest.fixture
def ranger_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to set common module args for Ranger service info tests."""

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


def test_ranger_service_info_module_list_all(ranger_module_args, existing_ranger_service):
    """Test RangerServiceInfoModule listing all services."""

    ranger_module_args({})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert "services" in result
    assert isinstance(result["services"], list)
    assert any(service["id"] == existing_ranger_service.id for service in result["services"])


def test_ranger_service_info_module_by_name(ranger_module_args, existing_ranger_service):
    """Test RangerServiceInfoModule get service by name."""

    ranger_module_args({"name": existing_ranger_service.name})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 1
    assert result["services"][0]["id"] == existing_ranger_service.id
    assert result["services"][0]["name"] == existing_ranger_service.name


def test_ranger_service_info_module_by_id(ranger_module_args, existing_ranger_service):
    """Test RangerServiceInfoModule get service by id."""

    ranger_module_args({"id": existing_ranger_service.id})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 1
    assert result["services"][0]["id"] == existing_ranger_service.id
    assert result["services"][0]["name"] == existing_ranger_service.name


def test_ranger_service_info_module_nonexistent_name(request, ranger_module_args):
    """Test RangerServiceInfoModule with a nonexistent service name."""

    ranger_module_args(
        {"name": f"nonexistent-service-{request.node.name.lower()}"},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert result["services"] == []


def test_ranger_service_info_module_nonexistent_id(ranger_module_args):
    """Test RangerServiceInfoModule with a nonexistent service id."""

    ranger_module_args({"id": 999999})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert result["services"] == []


def test_ranger_service_info_module_check_mode(ranger_module_args, existing_ranger_service):
    """Test RangerServiceInfoModule in check mode."""

    ranger_module_args({"id": existing_ranger_service.id, "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 1
    assert result["services"][0]["id"] == existing_ranger_service.id


def test_ranger_service_info_module_with_configs(
    request,
    ranger_module_args,
    ranger_service_client,
    ranger_service_type,
    purge_ranger_service,
):
    """Test RangerServiceInfoModule returns service configs verbatim."""
    service_name = f"ansible-test-info-configs-{request.node.name.lower()}"

    created = ranger_service_client.create_service(
        RangerService(
            name=service_name,
            type=ranger_service_type,
            configs={"tag.download.auth.users": "hdfs"},
        ),
    )
    purge_ranger_service(created)

    ranger_module_args({"name": service_name})

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert len(result["services"]) == 1
    assert "configs" in result["services"][0]

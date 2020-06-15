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

from typing import Callable, Generator

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_environment_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbEnvironment,
    SsbEnvironmentRequest,
    SsbEnvironmentSecuredProperty,
    SsbEnvironmentClient,
)

REQUIRED_ENV_VARS = [
    "SSB_SSE_API_URL",
    "SSB_SSE_API_USERNAME",
    "SSB_SSE_API_PASSWORD",
]


@pytest.fixture
def ssb_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to set common module args for SSB tests."""

    def _ssb_module_args(overrides: dict = {}) -> None:
        args = {
            "url": env_context["SSB_SSE_API_URL"],
            "url_username": env_context["SSB_SSE_API_USERNAME"],
            "url_password": env_context["SSB_SSE_API_PASSWORD"],
            "force_basic_auth": True,
        }
        if overrides:
            args.update(overrides)
        module_args(args)

    return _ssb_module_args


@pytest.fixture
def existing_environment(
    request,
    ssb_rest_client,
    existing_project,
    purge_environment,
) -> Generator[SsbEnvironment, None, None]:
    """Fixture to create a test environment and clean it up after the test."""
    environment_name = request.node.name.lower() + "_env"
    environment_id = None

    client = SsbEnvironmentClient(api_client=ssb_rest_client)

    # Clean up any existing test environment
    environments = client.list_environments(existing_project.id)
    for environment in environments:
        if environment.name == environment_name and isinstance(environment.id, int):
            client.delete_environment(existing_project.id, environment.id)

    # Create the test environment
    environment = client.create_environment(
        project_id=existing_project.id,
        environment=SsbEnvironmentRequest(
            name=environment_name,
            properties={
                "test.property": SsbEnvironmentSecuredProperty(
                    value="test-value",
                    sensitive=False,
                ),
            },
        ),
    )

    purge_environment(existing_project.id, environment)

    yield environment


def test_ssb_environment_info_module_list_all(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentInfoModule list all environments."""

    ssb_module_args({"project_id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result
    assert isinstance(result["environments"], list)
    assert any(env["id"] == existing_environment.id for env in result["environments"])


def test_ssb_environment_info_module_by_name(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentInfoModule get environment by name."""

    ssb_module_args(
        {"project_id": existing_project.id, "name": existing_environment.name},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result
    assert len(result["environments"]) == 1
    assert result["environments"][0]["id"] == existing_environment.id
    assert result["environments"][0]["name"] == existing_environment.name


def test_ssb_environment_info_module_by_id(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentInfoModule get environment by id."""

    ssb_module_args({"project_id": existing_project.id, "id": existing_environment.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result
    assert len(result["environments"]) == 1
    assert result["environments"][0]["id"] == existing_environment.id
    assert result["environments"][0]["name"] == existing_environment.name


def test_ssb_environment_info_module_nonexistent_name(
    ssb_module_args,
    existing_project,
):
    """Test SsbEnvironmentInfoModule with nonexistent environment name."""

    ssb_module_args(
        {"project_id": existing_project.id, "name": "nonexistent-environment-12345"},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result
    assert len(result["environments"]) == 0


def test_ssb_environment_info_module_nonexistent_id(ssb_module_args, existing_project):
    """Test SsbEnvironmentInfoModule with nonexistent environment id."""

    ssb_module_args({"project_id": existing_project.id, "id": 999999})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result
    assert len(result["environments"]) == 0


def test_ssb_environment_info_module_check_mode(ssb_module_args, existing_project):
    """Test SsbEnvironmentInfoModule in check mode."""

    ssb_module_args({"project_id": existing_project.id, "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result


def test_ssb_environment_info_module_with_secured_properties(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentInfoModule returns secured properties."""

    ssb_module_args({"project_id": existing_project.id, "id": existing_environment.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result
    assert len(result["environments"]) == 1
    env = result["environments"][0]
    assert "secured_props" in env
    assert isinstance(env["secured_props"], dict)

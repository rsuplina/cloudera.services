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

from typing import Callable

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_environment
from ansible_collections.cloudera.services.plugins.module_utils.common import from_dict
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbEnvironment,
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


def test_ssb_environment_module_create_minimal(
    request,
    ssb_module_args,
    existing_project,
    purge_environment,
):
    """Test SsbEnvironmentModule creating an environment with minimal parameters."""
    environment_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": environment_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value

    purge_environment(
        existing_project.id,
        from_dict(SsbEnvironment, result["environment"]),
    )

    assert result["changed"] is True
    assert result["environment"]["name"] == environment_name
    assert "id" in result["environment"]


def test_ssb_environment_module_create_with_properties(
    request,
    ssb_module_args,
    existing_project,
    purge_environment,
):
    """Test SsbEnvironmentModule creating an environment with properties."""
    environment_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": environment_name,
            "properties": {
                "db_url": {
                    "value": "jdbc:postgresql://localhost:5432/db",
                    "sensitive": False,
                },
                "db_password": {
                    "value": "secret123",
                    "sensitive": True,
                },
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    purge_environment(
        existing_project.id,
        from_dict(SsbEnvironment, result["environment"]),
    )

    assert result["changed"] is True
    assert result["environment"]["name"] == environment_name
    assert "db_url" in result["environment"]["secured_props"]
    assert "db_password" in result["environment"]["secured_props"]


def test_ssb_environment_module_create_and_activate(
    request,
    ssb_module_args,
    existing_project,
    purge_environment,
):
    """Test SsbEnvironmentModule creating and activating an environment."""
    environment_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": environment_name,
            "properties": {
                "env_name": {
                    "value": environment_name,
                    "sensitive": False,
                },
            },
            "activated": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    purge_environment(
        existing_project.id,
        from_dict(SsbEnvironment, result["environment"]),
    )

    assert result["changed"] is True
    assert result["environment"]["name"] == environment_name


def test_ssb_environment_module_present_idempotent(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentModule with existing environment (idempotent)."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_environment.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False
    assert result["environment"]["id"] == existing_environment.id
    assert result["environment"]["name"] == existing_environment.name


def test_ssb_environment_module_by_id(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentModule retrieving environment by ID."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "id": existing_environment.id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False
    assert result["environment"]["id"] == existing_environment.id
    assert result["environment"]["name"] == existing_environment.name


def test_ssb_environment_module_activate_existing(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentModule activating an existing environment."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_environment.name,
            "activated": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert result["environment"]["id"] == existing_environment.id


def test_ssb_environment_module_activate_already_active(
    ssb_module_args,
    existing_project,
    activated_environment,
):
    """Test SsbEnvironmentModule with environment already active (idempotent)."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": activated_environment.name,
            "activated": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False  # No changes needed
    assert result["environment"]["id"] == activated_environment.id


def test_ssb_environment_module_update_properties_new(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentModule updating environment properties."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_environment.name,
            "properties": {
                "updated_key": {
                    "value": "updated_value",
                    "sensitive": False,
                },
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert "updated_key" in result["environment"]["secured_props"]


def test_ssb_environment_module_update_properties_existing(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentModule updating environment properties."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_environment.name,
            "properties": {
                "test_key": {
                    "value": "updated_value",
                    "sensitive": False,
                },
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert "test_key" in result["environment"]["secured_props"]
    assert (
        result["environment"]["secured_props"]["test_key"]["value"] == "updated_value"
    )


def test_ssb_environment_module_delete(
    ssb_module_args,
    existing_project,
    deletable_environment,
):
    """Test SsbEnvironmentModule deleting an environment."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": deletable_environment.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True


def test_ssb_environment_module_delete_active_environment(
    ssb_module_args,
    existing_project,
    activated_deletable_environment,
):
    """Test SsbEnvironmentModule deleting an active environment (deactivates first)."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": activated_deletable_environment.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True


def test_ssb_environment_module_delete_nonexistent(
    ssb_module_args,
    existing_project,
):
    """Test SsbEnvironmentModule deleting a non-existent environment."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": "nonexistent-environment-name-12345",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False


def test_ssb_environment_module_check_mode_create(
    ssb_module_args,
    existing_project,
):
    """Test SsbEnvironmentModule in check mode for creation."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": "ansible-test-check-mode",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert result["environment"] == {}  # No environment should be created in check mode


def test_ssb_environment_module_check_mode_delete(
    ssb_module_args,
    existing_project,
    existing_environment,
):
    """Test SsbEnvironmentModule in check mode for deletion."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": existing_environment.name,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert (
        result["environment"] == {}
    )  # Environment should not actually be deleted in check mode


def test_ssb_environment_module_with_diff_create(
    request,
    ssb_module_args,
    existing_project,
    purge_environment,
):
    """Test SsbEnvironmentModule with diff mode for creation."""
    environment_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": environment_name,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    purge_environment(
        existing_project.id,
        from_dict(SsbEnvironment, result["environment"]),
    )

    assert result["changed"] is True


def test_ssb_environment_module_with_diff_delete(
    ssb_module_args,
    existing_project,
    deletable_environment,
):
    """Test SsbEnvironmentModule with diff mode for deletion."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": deletable_environment.name,
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

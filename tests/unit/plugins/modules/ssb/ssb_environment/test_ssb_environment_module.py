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

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_environment
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbEnvironment,
    SsbEnvironmentSecuredProperty,
    SsbProject,
)

BASE_URL = "https://api.cloudera.internal"


def test_ssb_environment_module_create_minimal(module_args, mocker):
    """Test SsbEnvironmentModule creating an environment with minimal parameters."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )
    mock_create_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.create_environment",
        return_value=SsbEnvironment(
            id=1,
            name="test-environment",
            secured_props={},
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-environment",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert result["environment"]["id"] == 1
    assert result["environment"]["name"] == "test-environment"

    mock_list_environments.assert_called_once_with("12345")
    mock_create_environment.assert_called_once()


def test_ssb_environment_module_create_with_properties(module_args, mocker):
    """Test SsbEnvironmentModule creating an environment with properties."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )
    mock_create_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.create_environment",
        return_value=SsbEnvironment(
            id=1,
            name="test-environment",
            secured_props={
                "db_url": SsbEnvironmentSecuredProperty(
                    value="jdbc:postgresql://localhost:5432/db",
                    sensitive=False,
                ),
                "db_password": SsbEnvironmentSecuredProperty(
                    value="secret",
                    sensitive=True,
                ),
            },
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-environment",
            "properties": {
                "db_url": {
                    "value": "jdbc:postgresql://localhost:5432/db",
                    "sensitive": False,
                },
                "db_password": {
                    "value": "secret",
                    "sensitive": True,
                },
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert result["environment"]["name"] == "test-environment"
    assert "db_url" in result["environment"]["secured_props"]
    assert "db_password" in result["environment"]["secured_props"]

    mock_list_environments.assert_called_once_with("12345")
    mock_create_environment.assert_called_once()


def test_ssb_environment_module_create_and_activate(module_args, mocker):
    """Test SsbEnvironmentModule creating and activating an environment."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )
    mock_create_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.create_environment",
        return_value=SsbEnvironment(
            id=1,
            name="test-environment",
            secured_props={},
        ),
    )
    mock_activate_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.activate_environment",
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-environment",
            "activated": True,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert result["environment"]["id"] == 1

    mock_list_environments.assert_called_once_with("12345")
    mock_create_environment.assert_called_once()
    mock_describe_project.assert_called_once_with("12345")
    mock_activate_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_present_idempotent(module_args, mocker):
    """Test SsbEnvironmentModule with existing environment (idempotent)."""
    existing_environment = SsbEnvironment(
        id=1,
        name="existing-environment",
        secured_props={
            "setting": SsbEnvironmentSecuredProperty(value="value", sensitive=False),
        },
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-environment",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False
    assert result["environment"]["id"] == 1
    assert result["environment"]["name"] == "existing-environment"

    mock_list_environments.assert_called_once_with("12345")


def test_ssb_environment_module_update_properties(module_args, mocker):
    """Test SsbEnvironmentModule updating environment properties."""
    existing_environment = SsbEnvironment(
        id=1,
        name="existing-environment",
        secured_props={
            "old_setting": SsbEnvironmentSecuredProperty(
                value="old_value",
                sensitive=False,
            ),
        },
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_update_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.update_environment",
        return_value=SsbEnvironment(
            id=1,
            name="existing-environment",
            secured_props={
                "new_setting": SsbEnvironmentSecuredProperty(
                    value="new_value",
                    sensitive=False,
                ),
            },
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-environment",
            "properties": {
                "new_setting": {
                    "value": "new_value",
                    "sensitive": False,
                },
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_update_environment.assert_called_once()


def test_ssb_environment_module_update_and_activate(module_args, mocker):
    """Test SsbEnvironmentModule updating properties and activating."""
    existing_environment = SsbEnvironment(
        id=1,
        name="existing-environment",
        secured_props={
            "old_setting": SsbEnvironmentSecuredProperty(
                value="old_value",
                sensitive=False,
            ),
        },
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_update_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.update_environment",
        return_value=SsbEnvironment(
            id=1,
            name="existing-environment",
            secured_props={
                "new_setting": SsbEnvironmentSecuredProperty(
                    value="new_value",
                    sensitive=False,
                ),
            },
        ),
    )
    mock_activate_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.activate_environment",
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-environment",
            "properties": {
                "new_setting": {
                    "value": "new_value",
                    "sensitive": False,
                },
            },
            "activated": True,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_update_environment.assert_called_once()
    mock_describe_project.assert_called_once_with("12345")
    mock_activate_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_activate_existing(module_args, mocker):
    """Test SsbEnvironmentModule activating an existing environment."""
    existing_environment = SsbEnvironment(
        id=1,
        name="existing-environment",
        secured_props={},
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_update_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.update_environment",
    )
    mock_activate_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.activate_environment",
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-environment",
            "activated": True,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_update_environment.assert_not_called()
    mock_describe_project.assert_called_once_with("12345")
    mock_activate_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_activate_already_active(module_args, mocker):
    """Test SsbEnvironmentModule with environment already active (idempotent)."""
    existing_environment = SsbEnvironment(
        id=1,
        name="existing-environment",
        secured_props={},
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_update_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.update_environment",
    )
    mock_activate_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.activate_environment",
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=1,  # Environment is already active
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-environment",
            "activated": True,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False  # No changes needed

    mock_list_environments.assert_called_once_with("12345")
    mock_update_environment.assert_not_called()
    mock_describe_project.assert_called_once_with("12345")
    mock_activate_environment.assert_not_called()  # Should not activate again


def test_ssb_environment_module_by_id(module_args, mocker):
    """Test SsbEnvironmentModule retrieving environment by ID."""
    existing_environment = SsbEnvironment(
        id=1,
        name="existing-environment",
        secured_props={},
    )

    mock_describe_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.describe_environment",
        return_value=existing_environment,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "id": 1,
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False
    assert result["environment"]["id"] == 1
    assert result["environment"]["name"] == "existing-environment"

    mock_describe_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_delete_by_name(module_args, mocker):
    """Test SsbEnvironmentModule deleting an environment by name."""
    existing_environment = SsbEnvironment(
        id=1,
        name="environment-to-delete",
        secured_props={},
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,
        ),
    )
    mock_delete_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.delete_environment",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "environment-to-delete",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_describe_project.assert_called_once_with("12345")
    mock_delete_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_delete_by_id(module_args, mocker):
    """Test SsbEnvironmentModule deleting an environment by ID."""
    existing_environment = SsbEnvironment(
        id=1,
        name="environment-to-delete",
        secured_props={},
    )

    mock_describe_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.describe_environment",
        return_value=existing_environment,
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,
        ),
    )
    mock_delete_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.delete_environment",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "id": 1,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_describe_environment.assert_called_once_with("12345", 1)
    mock_describe_project.assert_called_once_with("12345")
    mock_delete_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_delete_active_environment(module_args, mocker):
    """Test SsbEnvironmentModule deleting an active environment (deactivates first)."""
    existing_environment = SsbEnvironment(
        id=1,
        name="active-environment",
        secured_props={},
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=1,  # Environment is active
        ),
    )
    mock_deactivate_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.deactivate_environment",
    )
    mock_delete_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.delete_environment",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "active-environment",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_describe_project.assert_called_once_with("12345")
    mock_deactivate_environment.assert_called_once_with("12345")
    mock_delete_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_delete_inactive_environment(module_args, mocker):
    """Test SsbEnvironmentModule deleting an inactive environment (no deactivation needed)."""
    existing_environment = SsbEnvironment(
        id=1,
        name="inactive-environment",
        secured_props={},
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,  # No active environment
        ),
    )
    mock_deactivate_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.deactivate_environment",
    )
    mock_delete_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.delete_environment",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "inactive-environment",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_describe_project.assert_called_once_with("12345")
    mock_deactivate_environment.assert_not_called()  # Should not deactivate
    mock_delete_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_delete_nonexistent(module_args, mocker):
    """Test SsbEnvironmentModule deleting a non-existent environment."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "nonexistent-environment",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is False

    mock_list_environments.assert_called_once_with("12345")


def test_ssb_environment_module_check_mode_create(module_args, mocker):
    """Test SsbEnvironmentModule in check mode for creation."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )
    mock_create_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.create_environment",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-environment",
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_create_environment.assert_not_called()


def test_ssb_environment_module_check_mode_delete(module_args, mocker):
    """Test SsbEnvironmentModule in check mode for deletion."""
    existing_environment = SsbEnvironment(
        id=1,
        name="existing-environment",
        secured_props={},
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,
        ),
    )
    mock_delete_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.delete_environment",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-environment",
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_describe_project.assert_called_once_with("12345")
    mock_delete_environment.assert_not_called()


def test_ssb_environment_module_create_requires_name(module_args, mocker):
    """Test SsbEnvironmentModule fails when name is not provided on creation."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Parameter 'name' is required when creating a new environment",
    ):
        ssb_environment.main()

    mock_list_environments.assert_called_once_with("12345")


def test_ssb_environment_module_mutually_exclusive(module_args):
    """Test SsbEnvironmentModule with mutually exclusive parameters."""
    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-environment",
            "id": 1,
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="parameters are mutually exclusive: name|id",
    ):
        ssb_environment.main()


def test_ssb_environment_module_with_diff_create(module_args, mocker):
    """Test SsbEnvironmentModule with diff mode for creation."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )
    mock_create_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.create_environment",
        return_value=SsbEnvironment(
            id=1,
            name="test-environment",
            secured_props={},
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-environment",
            "state": "present",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_create_environment.assert_called_once()


def test_ssb_environment_module_with_diff_delete(module_args, mocker):
    """Test SsbEnvironmentModule with diff mode for deletion."""
    existing_environment = SsbEnvironment(
        id=1,
        name="environment-to-delete",
        secured_props={},
    )

    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[existing_environment],
    )
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbProjectClient.describe_project",
        return_value=SsbProject(
            name="test-project",
            id="12345",
            active_environment=None,
        ),
    )
    mock_delete_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.delete_environment",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "environment-to-delete",
            "state": "absent",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True

    mock_list_environments.assert_called_once_with("12345")
    mock_describe_project.assert_called_once_with("12345")
    mock_delete_environment.assert_called_once_with("12345", 1)


def test_ssb_environment_module_properties_string_values(module_args, mocker):
    """Test SsbEnvironmentModule with properties as simple string values."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.list_environments",
        return_value=[],
    )
    mock_create_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment.SsbEnvironmentClient.create_environment",
        return_value=SsbEnvironment(
            id=1,
            name="test-environment",
            secured_props={
                "simple_key": SsbEnvironmentSecuredProperty(
                    value="simple_value",
                    sensitive=False,
                ),
            },
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-environment",
            "properties": {
                "simple_key": "simple_value",
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment.main()

    result = e.value
    assert result["changed"] is True
    assert result["environment"]["name"] == "test-environment"

    mock_list_environments.assert_called_once_with("12345")
    mock_create_environment.assert_called_once()

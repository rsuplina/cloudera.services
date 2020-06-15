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

from ansible_collections.cloudera.services.plugins.modules import ssb_project
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbProject,
    SsbSyncSourceConfig,
    SsbSyncSourceCredential,
)

BASE_URL = "https://api.cloudera.internal"


def test_ssb_project_module_create_minimal(module_args, mocker):
    """Test SsbProjectModule creating a project with minimal parameters."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )
    mock_create_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.create_project",
        return_value=SsbProject(
            id=1,
            name="test-project",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "test-project",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True
    assert result["project"]["id"] == 1
    assert result["project"]["name"] == "test-project"

    mock_list_projects.assert_called_once()
    mock_create_project.assert_called_once()


def test_ssb_project_module_create_with_description(module_args, mocker):
    """Test SsbProjectModule creating a project with description and mv_prefix."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )
    mock_create_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.create_project",
        return_value=SsbProject(
            id=1,
            name="test-project",
            description="Test description",
            mv_prefix="test_",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "test-project",
            "description": "Test description",
            "mv_prefix": "test_",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True
    assert result["project"]["name"] == "test-project"
    assert result["project"]["description"] == "Test description"
    assert result["project"]["mv_prefix"] == "test_"

    mock_list_projects.assert_called_once()
    mock_create_project.assert_called_once()


def test_ssb_project_module_create_with_sync_source(module_args, mocker):
    """Test SsbProjectModule creating a project with sync source configuration."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )
    mock_create_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.create_project",
        return_value=SsbProject(
            id=1,
            name="test-project",
            sync_source_config=SsbSyncSourceConfig(
                type="git",
                clone_url="https://github.com/example/repo.git",
                branch="main",
                allow_deletions=False,
                credential=SsbSyncSourceCredential(
                    type="basic",
                    username="git-user",
                    password="secret-password",
                ),
            ),
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "test-project",
            "sync_source_config": {
                "type": "git",
                "clone_url": "https://github.com/example/repo.git",
                "branch": "main",
                "allow_deletions": False,
                "credential": {
                    "type": "basic",
                    "username": "git-user",
                    "password": "secret-password",
                },
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True
    assert result["project"]["name"] == "test-project"
    assert result["project"]["sync_source_config"]["type"] == "git"
    assert (
        result["project"]["sync_source_config"]["clone_url"]
        == "https://github.com/example/repo.git"
    )

    mock_list_projects.assert_called_once()
    mock_create_project.assert_called_once()


def test_ssb_project_module_present_idempotent(module_args, mocker):
    """Test SsbProjectModule with existing project (idempotent)."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
        description="Existing description",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "existing-project",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is False
    assert result["project"]["id"] == 1
    assert result["project"]["name"] == "existing-project"

    mock_list_projects.assert_called_once()


def test_ssb_project_module_by_id(module_args, mocker):
    """Test SsbProjectModule retrieving project by ID."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
        description="Existing description",
    )

    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.describe_project",
        return_value=existing_project,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "id": "1",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is False
    assert result["project"]["id"] == 1
    assert result["project"]["name"] == "existing-project"

    mock_describe_project.assert_called_once_with("1")


def test_ssb_project_module_delete_by_name(module_args, mocker):
    """Test SsbProjectModule deleting a project by name."""
    existing_project = SsbProject(
        id=1,
        name="project-to-delete",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )
    mock_delete_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.delete_project",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "project-to-delete",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True

    mock_list_projects.assert_called_once()
    mock_delete_project.assert_called_once_with(existing_project)


def test_ssb_project_module_delete_by_id(module_args, mocker):
    """Test SsbProjectModule deleting a project by ID."""
    existing_project = SsbProject(
        id=1,
        name="project-to-delete",
    )

    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.describe_project",
        return_value=existing_project,
    )
    mock_delete_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.delete_project",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "id": "1",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True

    mock_describe_project.assert_called_once_with("1")
    mock_delete_project.assert_called_once_with(existing_project)


def test_ssb_project_module_delete_nonexistent(module_args, mocker):
    """Test SsbProjectModule deleting a non-existent project."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "nonexistent-project",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is False

    mock_list_projects.assert_called_once()


def test_ssb_project_module_immutable_description_change(module_args, mocker):
    """Test SsbProjectModule failing on immutable description change."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
        description="Original description",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "existing-project",
            "description": "Different description",
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Cannot update immutable project fields: description",
    ):
        ssb_project.main()

    mock_list_projects.assert_called_once()


def test_ssb_project_module_immutable_mv_prefix_change(module_args, mocker):
    """Test SsbProjectModule failing on immutable mv_prefix change."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
        mv_prefix="original_",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "existing-project",
            "mv_prefix": "different_",
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Cannot update immutable project fields: mv_prefix",
    ):
        ssb_project.main()

    mock_list_projects.assert_called_once()


def test_ssb_project_module_immutable_multiple_fields_change(module_args, mocker):
    """Test SsbProjectModule failing on multiple immutable field changes."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
        description="Original description",
        mv_prefix="original_",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "existing-project",
            "description": "Different description",
            "mv_prefix": "different_",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson, match="Cannot update immutable project fields"):
        ssb_project.main()

    mock_list_projects.assert_called_once()


def test_ssb_project_module_sync_source_config_update_not_implemented(
    module_args,
    mocker,
):
    """Test SsbProjectModule failing on sync_source_config update."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
        sync_source_config=SsbSyncSourceConfig(
            type="git",
            clone_url="https://github.com/example/repo.git",
            branch="main",
        ),
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "existing-project",
            "sync_source_config": {
                "type": "git",
                "clone_url": "https://github.com/example/repo.git",
                "branch": "develop",
            },
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Updating sync_source_config is not yet implemented",
    ):
        ssb_project.main()

    mock_list_projects.assert_called_once()


def test_ssb_project_module_sync_source_config_add_not_implemented(module_args, mocker):
    """Test SsbProjectModule failing when adding sync_source_config to existing project."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "existing-project",
            "sync_source_config": {
                "type": "git",
                "clone_url": "https://github.com/example/repo.git",
                "branch": "main",
            },
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Updating sync_source_config is not yet implemented",
    ):
        ssb_project.main()

    mock_list_projects.assert_called_once()


def test_ssb_project_module_check_mode_create(module_args, mocker):
    """Test SsbProjectModule in check mode for creation."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )
    mock_create_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.create_project",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "test-project",
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True

    mock_list_projects.assert_called_once()
    mock_create_project.assert_not_called()


def test_ssb_project_module_check_mode_delete(module_args, mocker):
    """Test SsbProjectModule in check mode for deletion."""
    existing_project = SsbProject(
        id=1,
        name="existing-project",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )
    mock_delete_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.delete_project",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "existing-project",
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True

    mock_list_projects.assert_called_once()
    mock_delete_project.assert_not_called()


def test_ssb_project_module_synced_not_implemented(module_args, mocker):
    """Test SsbProjectModule with 'synced' state (not implemented)."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "test-project",
            "state": "synced",
        },
    )

    with pytest.raises(AnsibleFailJson, match="State 'synced' is not yet implemented"):
        ssb_project.main()

    mock_list_projects.assert_called_once()


def test_ssb_project_module_create_requires_name(module_args, mocker):
    """Test SsbProjectModule fails when name is not provided on creation."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Parameter 'name' is required when creating a new project",
    ):
        ssb_project.main()

    mock_list_projects.assert_called_once()


def test_ssb_project_module_mutually_exclusive(module_args):
    """Test SsbProjectModule with mutually exclusive parameters."""
    module_args(
        {
            "endpoint": BASE_URL,
            "name": "test-project",
            "id": "1",
            "state": "present",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="parameters are mutually exclusive: name|id",
    ):
        ssb_project.main()


def test_ssb_project_module_with_diff_create(module_args, mocker):
    """Test SsbProjectModule with diff mode for creation."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[],
    )
    mock_create_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.create_project",
        return_value=SsbProject(
            id=1,
            name="test-project",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "test-project",
            "state": "present",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True
    # diff field would be populated in actual execution
    # but we can't easily test that with mocking

    mock_list_projects.assert_called_once()
    mock_create_project.assert_called_once()


def test_ssb_project_module_with_diff_delete(module_args, mocker):
    """Test SsbProjectModule with diff mode for deletion."""
    existing_project = SsbProject(
        id=1,
        name="project-to-delete",
    )

    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.list_projects",
        return_value=[existing_project],
    )
    mock_delete_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project.SsbProjectClient.delete_project",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "project-to-delete",
            "state": "absent",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True

    mock_list_projects.assert_called_once()
    mock_delete_project.assert_called_once_with(existing_project)

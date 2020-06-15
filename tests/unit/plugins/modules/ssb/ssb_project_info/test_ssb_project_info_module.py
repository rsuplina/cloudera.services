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

from ansible_collections.cloudera.services.plugins.modules import ssb_project_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbProject,
    SsbSyncSourceConfig,
    SsbSyncSourceCredential,
)

BASE_URL = "https://api.cloudera.internal"


def test_ssb_project_info_module_list_all(module_args, mocker):
    """Test SsbProjectInfoModule listing all projects."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.list_projects",
        return_value=[
            SsbProject(
                id=1,
                name="project-one",
                description="First project",
            ),
            SsbProject(
                id=2,
                name="project-two",
                description="Second project",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 2
    assert result["projects"][0]["id"] == 1
    assert result["projects"][0]["name"] == "project-one"
    assert result["projects"][1]["id"] == 2
    assert result["projects"][1]["name"] == "project-two"

    mock_list_projects.assert_called_once()


def test_ssb_project_info_module_filter_by_name(module_args, mocker):
    """Test SsbProjectInfoModule filtering by name."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.list_projects",
        return_value=[
            SsbProject(
                id=1,
                name="project-one",
                description="First project",
            ),
            SsbProject(
                id=2,
                name="project-two",
                description="Second project",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "project-one",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 1
    assert result["projects"][0]["id"] == 1
    assert result["projects"][0]["name"] == "project-one"

    mock_list_projects.assert_called_once()


def test_ssb_project_info_module_filter_by_name_not_found(module_args, mocker):
    """Test SsbProjectInfoModule filtering by name when project doesn't exist."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.list_projects",
        return_value=[
            SsbProject(
                id=1,
                name="project-one",
                description="First project",
            ),
            SsbProject(
                id=2,
                name="project-two",
                description="Second project",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "name": "nonexistent-project",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 0

    mock_list_projects.assert_called_once()


def test_ssb_project_info_module_by_id(module_args, mocker):
    """Test SsbProjectInfoModule retrieval by ID."""
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.describe_project",
        return_value=SsbProject(
            id=1,
            name="project-one",
            description="First project",
            mv_prefix="mv_",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "id": "1",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 1
    assert result["projects"][0]["id"] == 1
    assert result["projects"][0]["name"] == "project-one"
    assert result["projects"][0]["mv_prefix"] == "mv_"

    mock_describe_project.assert_called_once_with(project_id="1")


def test_ssb_project_info_module_by_id_not_found(module_args, mocker):
    """Test SsbProjectInfoModule retrieval by ID when project doesn't exist."""
    mock_describe_project = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.describe_project",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "id": "999",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 0

    mock_describe_project.assert_called_once_with(project_id="999")


def test_ssb_project_info_module_with_sync_source(module_args, mocker):
    """Test SsbProjectInfoModule with sync source configuration."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.list_projects",
        return_value=[
            SsbProject(
                id=1,
                name="project-with-sync",
                description="Project with sync source",
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
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 1
    assert result["projects"][0]["name"] == "project-with-sync"
    assert result["projects"][0]["sync_source_config"]["type"] == "git"
    assert (
        result["projects"][0]["sync_source_config"]["clone_url"]
        == "https://github.com/example/repo.git"
    )
    assert result["projects"][0]["sync_source_config"]["branch"] == "main"
    assert result["projects"][0]["sync_source_config"]["allow_deletions"] is False
    assert result["projects"][0]["sync_source_config"]["credential"]["type"] == "basic"
    assert (
        result["projects"][0]["sync_source_config"]["credential"]["username"]
        == "git-user"
    )

    mock_list_projects.assert_called_once()


def test_ssb_project_info_module_mutually_exclusive(module_args):
    """Test SsbProjectInfoModule with mutually exclusive parameters."""
    module_args(
        {
            "endpoint": BASE_URL,
            "name": "project-one",
            "id": "1",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="parameters are mutually exclusive: name|id",
    ):
        ssb_project_info.main()


def test_ssb_project_info_module_check_mode(module_args, mocker):
    """Test SsbProjectInfoModule in check mode."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.list_projects",
        return_value=[
            SsbProject(
                id=1,
                name="project-one",
                description="First project",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 1

    mock_list_projects.assert_called_once()


def test_ssb_project_info_module_empty_list(module_args, mocker):
    """Test SsbProjectInfoModule when no projects exist."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.list_projects",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 0

    mock_list_projects.assert_called_once()


def test_ssb_project_info_module_with_active_environment(module_args, mocker):
    """Test SsbProjectInfoModule with active environment."""
    mock_list_projects = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_project_info.SsbProjectClient.list_projects",
        return_value=[
            SsbProject(
                id=1,
                name="project-with-env",
                description="Project with active environment",
                active_environment=42,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["projects"]) == 1
    assert result["projects"][0]["active_environment"] == 42

    mock_list_projects.assert_called_once()

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

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    from_dict,
    ServicesClient,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbProject,
    SsbSyncSourceConfig,
    SsbSyncSourceCredential,
    SsbProjectClient,
)

ENDPOINT_URL = "https://cloudera.internal"

CREDENTIAL_BASIC = dict(
    type="basic",
    username="user",
    password="pass",
)

CREDENTIAL_SSH = dict(
    type="ssh",
    ssh_private_key="private_key_content",
    ssh_public_key="public_key_content",
    ssh_passphrase="passphrase",
)

SYNC_SOURCE = dict(
    type="git",
    clone_url="https://github.com/example/repo.git",
    branch="main",
    allow_deletions=True,
)

PROJECT = dict(
    id="proj123",
    name="test-project",
    description="Test project description",
    mv_prefix="test_mv",
)

PROJECT_SYNC = dict(
    **PROJECT,
    sync_source_config=SYNC_SOURCE,
)

PROJECT_SYNC_BASIC_AUTH = dict(
    **PROJECT,
    sync_source_config={
        **SYNC_SOURCE,
        "credential": CREDENTIAL_BASIC,
    },
)

PROJECT_SYNC_SSH_AUTH = dict(
    **PROJECT,
    sync_source_config={
        **SYNC_SOURCE,
        "credential": CREDENTIAL_SSH,
    },
)

PROJECTS_LIST = [PROJECT]


def test_list_projects(mocker):
    """Test listing all projects."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = PROJECTS_LIST

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.list_projects()

    assert isinstance(response, list)
    assert isinstance(response[0], SsbProject)
    assert response == [from_dict(SsbProject, project) for project in PROJECTS_LIST]

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with("/api/v2/projects")


def test_create_project_minimal(mocker):
    """Test creating a project with minimal parameters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = PROJECT

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.create_project(SsbProject(name="test-project"))

    assert isinstance(response, SsbProject)
    assert response == from_dict(SsbProject, PROJECT)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/projects",
        data={"name": "test-project"},
    )


def test_create_project_with_description(mocker):
    """Test creating a project with description and mv_prefix."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = PROJECT

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.create_project(
        SsbProject(
            name="test-project",
            description="Test project description",
            mv_prefix="test_mv",
        ),
    )

    assert isinstance(response, SsbProject)
    assert response == from_dict(SsbProject, PROJECT)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/projects",
        data={
            "name": "test-project",
            "description": "Test project description",
            "mv_prefix": "test_mv",
        },
    )


def test_create_project_with_git_basic_auth(mocker):
    """Test creating a project with Git sync and basic authentication."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = PROJECT_SYNC_BASIC_AUTH

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.create_project(
        SsbProject(
            name="test-project",
            sync_source_config=SsbSyncSourceConfig(
                type="git",
                clone_url="https://github.com/example/repo.git",
                branch="main",
                allow_deletions=True,
                credential=SsbSyncSourceCredential(
                    type="basic",
                    username="user",
                    password="pass",
                ),
            ),
        ),
    )

    assert isinstance(response, SsbProject)
    assert response == from_dict(SsbProject, PROJECT_SYNC_BASIC_AUTH)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/projects",
        data={
            "name": "test-project",
            "sync_source_config": {
                "type": "git",
                "clone_url": "https://github.com/example/repo.git",
                "branch": "main",
                "allow_deletions": True,
                "credential": {
                    "type": "basic",
                    "username": "user",
                    "password": "pass",
                },
            },
        },
    )


def test_create_project_with_git_ssh_auth(mocker):
    """Test creating a project with Git sync and SSH authentication."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = PROJECT_SYNC_SSH_AUTH

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.create_project(
        SsbProject(
            name="test-project",
            sync_source_config=SsbSyncSourceConfig(
                type="git",
                clone_url="git@github.com:example/repo.git",
                credential=SsbSyncSourceCredential(
                    type="ssh",
                    ssh_private_key="private_key_content",
                    ssh_public_key="public_key_content",
                    ssh_passphrase="passphrase",
                ),
            ),
        ),
    )

    assert isinstance(response, SsbProject)
    assert response == from_dict(SsbProject, PROJECT_SYNC_SSH_AUTH)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/projects",
        data={
            "name": "test-project",
            "sync_source_config": {
                "type": "git",
                "clone_url": "git@github.com:example/repo.git",
                "credential": {
                    "type": "ssh",
                    "ssh_private_key": "private_key_content",
                    "ssh_public_key": "public_key_content",
                    "ssh_passphrase": "passphrase",
                },
            },
        },
    )


def test_import_project_minimal(mocker):
    """Test importing a project with minimal parameters."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = PROJECT_SYNC

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.import_project(
        SsbProject(
            name="test-project",
            sync_source_config=SsbSyncSourceConfig(
                type="git",
                clone_url="https://github.com/example/repo.git",
            ),
        ),
    )

    assert isinstance(response, SsbProject)
    assert response == from_dict(SsbProject, PROJECT_SYNC)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/projects/import",
        data={
            "name": "test-project",
            "sync_source_config": {
                "type": "git",
                "clone_url": "https://github.com/example/repo.git",
            },
        },
    )


def test_import_project_with_all_options(mocker):
    """Test importing a project with all options."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = PROJECT_SYNC_BASIC_AUTH

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.import_project(
        SsbProject(
            name="test-project",
            mv_prefix="test_mv",
            sync_source_config=SsbSyncSourceConfig(
                type="git",
                clone_url="https://github.com/example/repo.git",
                branch="develop",
                allow_deletions=False,
                credential=SsbSyncSourceCredential(
                    type="basic",
                    username="user",
                    password="pass",
                ),
            ),
        ),
    )

    assert isinstance(response, SsbProject)
    assert response == from_dict(SsbProject, PROJECT_SYNC_BASIC_AUTH)

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/projects/import",
        data={
            "name": "test-project",
            "mv_prefix": "test_mv",
            "sync_source_config": {
                "type": "git",
                "clone_url": "https://github.com/example/repo.git",
                "branch": "develop",
                "allow_deletions": False,
                "credential": {
                    "type": "basic",
                    "username": "user",
                    "password": "pass",
                },
            },
        },
    )


def test_describe_project(mocker):
    """Test describing a specific project."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = PROJECT

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.describe_project("proj123")

    assert isinstance(response, SsbProject)
    assert response == from_dict(SsbProject, PROJECT)

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/api/v2/projects/proj123",
        squelch={
            404: None,
        },
    )


def test_delete_project(mocker):
    """Test deleting a specific project."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = {}

    # Create the SSBProjectClient instance
    client = SsbProjectClient(api_client=api_client)

    response = client.delete_project(SsbProject(id="proj123", name="test-project"))

    assert response == None

    # Verify that the delete method was called with correct parameters
    api_client.delete.assert_called_once_with("/api/v2/projects/proj123")

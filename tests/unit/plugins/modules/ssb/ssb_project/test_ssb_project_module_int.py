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
    AnsibleFailJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_project
from ansible_collections.cloudera.services.plugins.module_utils.common import from_dict
from ansible_collections.cloudera.services.plugins.module_utils.ssb import SsbProject

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


def test_ssb_project_module_create_minimal(request, ssb_module_args, purge_project):
    """Test SsbProjectModule creating a project with minimal parameters."""
    project_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "name": project_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value

    purge_project(from_dict(SsbProject, result["project"]))

    assert result["changed"] is True
    assert result["project"]["name"] == project_name
    assert "id" in result["project"]


def test_ssb_project_module_create_with_description(
    request,
    ssb_module_args,
    purge_project,
):
    """Test SsbProjectModule creating a project with description and mv_prefix."""
    project_name = request.node.name
    description = "Test project with description"
    mv_prefix = "test_mv"

    ssb_module_args(
        {
            "state": "present",
            "name": project_name,
            "description": description,
            "mv_prefix": mv_prefix,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    purge_project(from_dict(SsbProject, result["project"]))

    assert result["changed"] is True
    assert result["project"]["name"] == project_name
    assert result["project"]["description"] == description
    assert result["project"]["mv_prefix"] == mv_prefix


def test_ssb_project_module_present_idempotent(ssb_module_args, existing_project):
    """Test SsbProjectModule with existing project (idempotent)."""

    ssb_module_args(
        {
            "state": "present",
            "name": existing_project.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is False
    assert result["project"]["id"] == existing_project.id
    assert result["project"]["name"] == existing_project.name


def test_ssb_project_module_by_id(ssb_module_args, existing_project):
    """Test SsbProjectModule retrieving project by ID."""

    ssb_module_args(
        {
            "state": "present",
            "id": existing_project.id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is False
    assert result["project"]["id"] == existing_project.id
    assert result["project"]["name"] == existing_project.name


def test_ssb_project_module_delete(ssb_module_args, deletable_project):
    """Test SsbProjectModule deleting a project."""

    ssb_module_args(
        {
            "state": "absent",
            "name": deletable_project.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True


def test_ssb_project_module_delete_nonexistent(ssb_module_args):
    """Test SsbProjectModule deleting a non-existent project."""

    ssb_module_args(
        {
            "state": "absent",
            "name": "nonexistent-project-name-12345",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is False


def test_ssb_project_module_immutable_description_change(
    ssb_module_args,
    existing_project,
):
    """Test SsbProjectModule failing on immutable description change."""

    ssb_module_args(
        {
            "state": "present",
            "name": existing_project.name,
            "description": "Different description from existing",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Cannot update immutable project fields: description.",
    ):
        ssb_project.main()


def test_ssb_project_module_sync_config_change(ssb_module_args, existing_project):
    """Test SsbProjectModule failing on immutable sync_source_config change."""

    ssb_module_args(
        {
            "state": "present",
            "name": existing_project.name,
            "sync_source_config": {
                "type": "git",
                "clone_url": "https://example.com/repo.git",
            },
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="Updating sync_source_config is not yet implemented",
    ):
        ssb_project.main()


def test_ssb_project_module_check_mode_create(ssb_module_args):
    """Test SsbProjectModule in check mode for creation."""

    ssb_module_args(
        {
            "state": "present",
            "name": "ansible-test-check-mode",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True
    assert result["project"] == {}  # No project should be created in check mode


def test_ssb_project_module_check_mode_delete(ssb_module_args, existing_project):
    """Test SsbProjectModule in check mode for deletion."""

    ssb_module_args(
        {
            "state": "absent",
            "name": existing_project.name,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project.main()

    result = e.value
    assert result["changed"] is True
    assert (
        result["project"] == {}
    )  # Project should not actually be deleted in check mode


def test_ssb_project_module_synced_not_implemented(ssb_module_args):
    """Test SsbProjectModule with 'synced' state (not implemented)."""

    ssb_module_args(
        {
            "state": "synced",
            "name": "test-project",
        },
    )

    with pytest.raises(AnsibleFailJson, match="State 'synced' is not yet implemented"):
        ssb_project.main()

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

from ansible_collections.cloudera.services.plugins.modules import ssb_project_info

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


def test_ssb_project_info_module_list_all(ssb_module_args, existing_project):
    """Test SsbProjectInfoModule list all projects."""

    ssb_module_args({})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert "projects" in result
    assert isinstance(result["projects"], list)
    assert any(p["id"] == existing_project.id for p in result["projects"])


def test_ssb_project_info_module_by_name(ssb_module_args, existing_project):
    """Test SsbProjectInfoModule get project by name."""

    ssb_module_args({"name": existing_project.name})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert "projects" in result
    assert len(result["projects"]) == 1
    assert result["projects"][0]["id"] == existing_project.id


def test_ssb_project_info_module_by_id(ssb_module_args, existing_project):
    """Test SsbProjectInfoModule get project by id."""

    ssb_module_args({"id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert "projects" in result
    assert len(result["projects"]) == 1
    assert result["projects"][0]["id"] == existing_project.id


def test_ssb_project_info_module_nonexistent_name(ssb_module_args):
    """Test SsbProjectInfoModule with nonexistent project name."""

    ssb_module_args({"name": "nonexistent-project-name-12345"})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert "projects" in result
    assert len(result["projects"]) == 0


def test_ssb_project_info_module_check_mode(ssb_module_args):
    """Test SsbProjectInfoModule in check mode."""

    ssb_module_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_project_info.main()

    result = e.value
    assert result["changed"] is False
    assert "projects" in result

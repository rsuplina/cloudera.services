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

from ansible_collections.cloudera.services.plugins.modules import ssb_udf_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUdf,
    SsbUdfClient,
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


def test_ssb_udf_info_module_list_all(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfInfoModule list all UDFs."""

    ssb_module_args({"project_id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result
    assert isinstance(result["udfs"], list)
    assert any(udf["id"] == existing_udf.id for udf in result["udfs"])


def test_ssb_udf_info_module_by_name(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfInfoModule get UDF by name."""

    ssb_module_args(
        {"project_id": existing_project.id, "name": existing_udf.name},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result
    assert len(result["udfs"]) == 1
    assert result["udfs"][0]["id"] == existing_udf.id
    assert result["udfs"][0]["name"] == existing_udf.name


def test_ssb_udf_info_module_by_id(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfInfoModule get UDF by id."""

    ssb_module_args({"project_id": existing_project.id, "id": existing_udf.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result
    assert len(result["udfs"]) == 1
    assert result["udfs"][0]["id"] == existing_udf.id
    assert result["udfs"][0]["name"] == existing_udf.name


def test_ssb_udf_info_module_nonexistent_name(ssb_module_args, existing_project):
    """Test SsbUdfInfoModule with nonexistent UDF name."""

    ssb_module_args(
        {"project_id": existing_project.id, "name": "nonexistent-udf-12345"},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result
    assert len(result["udfs"]) == 0


def test_ssb_udf_info_module_nonexistent_id(ssb_module_args, existing_project):
    """Test SsbUdfInfoModule with nonexistent UDF id."""

    ssb_module_args({"project_id": existing_project.id, "id": 999999})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result
    assert len(result["udfs"]) == 0


def test_ssb_udf_info_module_check_mode(ssb_module_args, existing_project):
    """Test SsbUdfInfoModule in check mode."""

    ssb_module_args({"project_id": existing_project.id, "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result


def test_ssb_udf_info_module_with_code_and_types(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfInfoModule with UDF code and types."""

    ssb_module_args(
        {"project_id": existing_project.id, "name": existing_udf.name},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 1
    udf = result["udfs"][0]
    assert "code" in udf
    assert "language" in udf
    assert udf["language"] == "PYTHON"
    assert "input_types" in udf
    assert "output_type" in udf


def test_ssb_udf_info_module_multiple_udfs(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfInfoModule listing multiple UDFs."""

    ssb_module_args({"project_id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result
    assert isinstance(result["udfs"], list)
    # Should have at least the existing_udf
    assert len(result["udfs"]) >= 1
    udf_ids = [udf["id"] for udf in result["udfs"]]
    assert existing_udf.id in udf_ids

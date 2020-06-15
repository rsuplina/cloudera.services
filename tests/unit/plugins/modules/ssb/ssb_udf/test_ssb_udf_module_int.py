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

from ansible_collections.cloudera.services.plugins.modules import ssb_udf
from ansible_collections.cloudera.services.plugins.module_utils.common import from_dict
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUdf,
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


def test_ssb_udf_module_create_python_minimal(
    request,
    ssb_module_args,
    existing_project,
    purge_udf,
):
    """Test SsbUdfModule creating a Python UDF with minimal parameters."""
    udf_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": udf_name,
            "language": "PYTHON",
            "code": "def test_func(data):\n    return data.upper()",
            "output_type": "PYTHON_INFERRED",
            "input_types": ["STRING"],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value

    purge_udf(from_dict(SsbUdf, result["udf"]))

    assert result["changed"] is True
    assert result["udf"]["name"] == udf_name.upper()
    assert result["udf"]["language"] == "PYTHON"
    assert "id" in result["udf"]


@pytest.mark.skip(reason="Current Datahubs do not support Javascript UDFs")
def test_ssb_udf_module_create_javascript_minimal(
    request,
    ssb_module_args,
    existing_project,
    purge_udf,
):
    """Test SsbUdfModule creating a JavaScript UDF with minimal parameters."""
    udf_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": udf_name,
            "language": "JAVASCRIPT",
            "code": "function testFunc(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "input_types": ["STRING"],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value

    purge_udf(from_dict(SsbUdf, result["udf"]))

    assert result["changed"] is True
    assert result["udf"]["name"] == udf_name.upper()
    assert result["udf"]["language"] == "JAVASCRIPT"
    assert "id" in result["udf"]


def test_ssb_udf_module_create_with_description(
    request,
    ssb_module_args,
    existing_project,
    purge_udf,
):
    """Test SsbUdfModule creating a UDF with description."""
    udf_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": udf_name,
            "language": "PYTHON",
            "code": "def test_func(data):\n    return data.upper()",
            "output_type": "PYTHON_INFERRED",
            "input_types": ["STRING"],
            "description": "Test UDF with description",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value

    purge_udf(from_dict(SsbUdf, result["udf"]))

    assert result["changed"] is True
    assert result["udf"]["name"] == udf_name.upper()
    assert result["udf"]["description"] == "Test UDF with description"


def test_ssb_udf_module_present_idempotent(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfModule with existing UDF (idempotent)."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_udf.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is False
    assert result["udf"]["id"] == existing_udf.id
    assert result["udf"]["name"] == existing_udf.name.upper()


def test_ssb_udf_module_by_id(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfModule retrieving UDF by ID."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "id": existing_udf.id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is False
    assert result["udf"]["id"] == existing_udf.id
    assert result["udf"]["name"] == existing_udf.name


def test_ssb_udf_module_update_code(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfModule updating UDF code."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_udf.name,
            "code": "def test_func(str):\n    return str.lower()",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    assert "lower" in result["udf"]["code"]


def test_ssb_udf_module_update_description(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfModule updating UDF description."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_udf.name,
            "description": "Updated description for integration tests",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    assert result["udf"]["description"] == "Updated description for integration tests"


def test_ssb_udf_module_delete_by_name(
    request,
    ssb_module_args,
    existing_project,
    udf_client,
):
    """Test SsbUdfModule deleting a UDF by name."""
    udf_name = request.node.name

    # Create a UDF to delete
    created_udf = udf_client.create_udf(
        SsbUdf(
            name=udf_name,
            project_id=existing_project.id,
            language="PYTHON",
            code="def test_func(data):\n    return data.upper()",
            output_type="PYTHON_INFERRED",
            input_types=["STRING"],
        ),
    )

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": udf_name.upper(),
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    # Verify UDF was deleted
    remaining_udfs = udf_client.list_udfs(existing_project.id)
    assert not any(udf.id == created_udf.id for udf in remaining_udfs)


def test_ssb_udf_module_delete_by_id(
    request,
    ssb_module_args,
    existing_project,
    udf_client,
):
    """Test SsbUdfModule deleting a UDF by ID."""
    udf_name = request.node.name

    # Create a UDF to delete
    created_udf = udf_client.create_udf(
        SsbUdf(
            name=udf_name,
            project_id=existing_project.id,
            language="PYTHON",
            code="def test_func(data):\n    return data.upper()",
            output_type="PYTHON_INFERRED",
            input_types=["STRING"],
        ),
    )

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "id": created_udf.id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    # Verify UDF was deleted
    remaining_udfs = udf_client.list_udfs(existing_project.id)
    assert not any(udf.id == created_udf.id for udf in remaining_udfs)


def test_ssb_udf_module_delete_nonexistent(
    ssb_module_args,
    existing_project,
):
    """Test SsbUdfModule deleting a non-existent UDF."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": "nonexistent-udf-name-12345",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is False


def test_ssb_udf_module_check_mode_create(
    ssb_module_args,
    existing_project,
):
    """Test SsbUdfModule in check mode for creation."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": "check_mode_udf",
            "language": "PYTHON",
            "code": "def test_func(data):\n    return data.upper()",
            "output_type": "PYTHON_INFERRED",
            "input_types": ["STRING"],
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    # In check mode, no UDF should actually be created
    assert result["udf"] == {}


def test_ssb_udf_module_check_mode_delete(
    ssb_module_args,
    existing_project,
    existing_udf,
):
    """Test SsbUdfModule in check mode for deletion."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": existing_udf.name,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True


@pytest.mark.skip(reason="Current Datahubs do not support Javascript UDFs (Java 11)")
def test_ssb_udf_module_multiple_input_types(
    request,
    ssb_module_args,
    existing_project,
    purge_udf,
):
    """Test SsbUdfModule creating a UDF with multiple input types."""
    udf_name = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": udf_name,
            "language": "JAVASCRIPT",
            "code": "function concat(str1, str2) { return str1 + str2; }",
            "output_type": "STRING",
            "input_types": ["STRING", "STRING"],
            "description": "Concatenates two strings",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value

    purge_udf(from_dict(SsbUdf, result["udf"]))

    assert result["changed"] is True
    assert len(result["udf"]["input_types"]) == 2
    assert result["udf"]["input_types"] == ["STRING", "STRING"]

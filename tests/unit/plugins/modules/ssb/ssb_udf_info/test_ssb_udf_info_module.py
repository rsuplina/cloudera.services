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
)

from ansible_collections.cloudera.services.plugins.modules import ssb_udf_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUdf,
)

BASE_URL = "https://api.cloudera.internal"
PROJECT_ID = "proj123"


def test_ssb_udf_info_module_list_all(module_args, mocker):
    """Test SsbUdfInfoModule listing all UDFs."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[
            SsbUdf(
                id=1,
                name="uppercase",
                project_id=PROJECT_ID,
                output_type="STRING",
                language="JAVASCRIPT",
                code="function uppercase(str) { return str.toUpperCase(); }",
                input_types=["STRING"],
            ),
            SsbUdf(
                id=2,
                name="multiply",
                project_id=PROJECT_ID,
                output_type="INT",
                language="JAVASCRIPT",
                code="function multiply(a, b) { return a * b; }",
                input_types=["INT", "INT"],
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 2
    assert result["udfs"][0]["id"] == 1
    assert result["udfs"][0]["name"] == "uppercase"
    assert result["udfs"][1]["id"] == 2
    assert result["udfs"][1]["name"] == "multiply"

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_udf_info_module_filter_by_name(module_args, mocker):
    """Test SsbUdfInfoModule filtering by name."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[
            SsbUdf(
                id=1,
                name="uppercase",
                project_id=PROJECT_ID,
                output_type="STRING",
                language="JAVASCRIPT",
                code="function uppercase(str) { return str.toUpperCase(); }",
                input_types=["STRING"],
            ),
            SsbUdf(
                id=2,
                name="multiply",
                project_id=PROJECT_ID,
                output_type="INT",
                language="JAVASCRIPT",
                code="function multiply(a, b) { return a * b; }",
                input_types=["INT", "INT"],
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "uppercase",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 1
    assert result["udfs"][0]["id"] == 1
    assert result["udfs"][0]["name"] == "uppercase"

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_udf_info_module_filter_by_name_not_found(module_args, mocker):
    """Test SsbUdfInfoModule filtering by name when UDF doesn't exist."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[
            SsbUdf(
                id=1,
                name="uppercase",
                project_id=PROJECT_ID,
                output_type="STRING",
            ),
            SsbUdf(
                id=2,
                name="multiply",
                project_id=PROJECT_ID,
                output_type="INT",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "nonexistent-udf",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 0

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_udf_info_module_by_id(module_args, mocker):
    """Test SsbUdfInfoModule retrieval by ID."""
    mock_describe_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.describe_udf",
        return_value=SsbUdf(
            id=1,
            name="uppercase",
            project_id=PROJECT_ID,
            output_type="STRING",
            language="JAVASCRIPT",
            code="function uppercase(str) { return str.toUpperCase(); }",
            input_types=["STRING"],
            description="Converts string to uppercase",
            created_at="2024-06-01T12:00:00Z",
            updated_at="2024-06-02T14:00:00Z",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "id": 1,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 1
    assert result["udfs"][0]["id"] == 1
    assert result["udfs"][0]["name"] == "uppercase"
    assert result["udfs"][0]["language"] == "JAVASCRIPT"
    assert result["udfs"][0]["description"] == "Converts string to uppercase"

    mock_describe_udf.assert_called_once_with(
        project_id=PROJECT_ID,
        udf_id=1,
    )


def test_ssb_udf_info_module_by_id_not_found(module_args, mocker):
    """Test SsbUdfInfoModule retrieval by ID when UDF doesn't exist."""
    mock_describe_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.describe_udf",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "id": 999,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 0

    mock_describe_udf.assert_called_once_with(
        project_id=PROJECT_ID,
        udf_id=999,
    )


def test_ssb_udf_info_module_with_python_udf(module_args, mocker):
    """Test SsbUdfInfoModule with Python UDF."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[
            SsbUdf(
                id=1,
                name="python_transform",
                project_id=PROJECT_ID,
                output_type="PYTHON_INFERRED",
                language="PYTHON",
                code="def transform(x):\n    return x * 2",
                description="Python transformation function",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 1
    udf = result["udfs"][0]
    assert udf["language"] == "PYTHON"
    assert udf["output_type"] == "PYTHON_INFERRED"

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_udf_info_module_check_mode(module_args, mocker):
    """Test SsbUdfInfoModule in check mode."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_udf_info_module_empty_list(module_args, mocker):
    """Test SsbUdfInfoModule with no UDFs in project."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert "udfs" in result
    assert len(result["udfs"]) == 0

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_udf_info_module_with_multiple_input_types(module_args, mocker):
    """Test SsbUdfInfoModule with UDF having multiple input types."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[
            SsbUdf(
                id=1,
                name="complex_calc",
                project_id=PROJECT_ID,
                output_type="DECIMAL",
                language="JAVASCRIPT",
                code="function calc(a, b, c) { return (a + b) * c; }",
                input_types=["INT", "INT", "FLOAT"],
                description="Complex calculation with multiple inputs",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 1
    udf = result["udfs"][0]
    assert "input_types" in udf
    assert len(udf["input_types"]) == 3
    assert udf["input_types"] == ["INT", "INT", "FLOAT"]

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_udf_info_module_with_java_udf(module_args, mocker):
    """Test SsbUdfInfoModule with Java UDF."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf_info.SsbUdfClient.list_udfs",
        return_value=[
            SsbUdf(
                id=1,
                name="java_function",
                project_id=PROJECT_ID,
                output_type="STRING",
                java_class_name="com.example.MyUdf",
                file_name="my-udf.jar",
                description="Java-based UDF",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["udfs"]) == 1
    udf = result["udfs"][0]
    assert "java_class_name" in udf
    assert udf["java_class_name"] == "com.example.MyUdf"
    assert udf["file_name"] == "my-udf.jar"

    mock_list_udfs.assert_called_once_with(project_id=PROJECT_ID)

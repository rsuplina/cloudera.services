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

from ansible_collections.cloudera.services.plugins.modules import ssb_udf
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUdf,
)

BASE_URL = "https://api.cloudera.internal"


def test_ssb_udf_module_create_javascript_minimal(module_args, mocker):
    """Test SsbUdfModule creating a JavaScript UDF with minimal parameters."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )
    mock_create_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.create_udf",
        return_value=SsbUdf(
            id=1,
            name="test_udf",
            project_id="12345",
            language="JAVASCRIPT",
            code="function test_udf(str) { return str.toUpperCase(); }",
            output_type="STRING",
            input_types=["STRING"],
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "language": "JAVASCRIPT",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "input_types": ["STRING"],
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    assert result["udf"]["id"] == 1
    assert result["udf"]["name"] == "test_udf"
    assert result["udf"]["language"] == "JAVASCRIPT"

    mock_list_udfs.assert_called_once_with("12345")
    mock_create_udf.assert_called_once()


def test_ssb_udf_module_create_python_udf(module_args, mocker):
    """Test SsbUdfModule creating a Python UDF."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )
    mock_create_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.create_udf",
        return_value=SsbUdf(
            id=1,
            name="python_udf",
            project_id="12345",
            language="PYTHON",
            code="def python_udf(data):\n    return data.upper()",
            output_type="PYTHON_INFERRED",
            input_types=["STRING"],
            description="Python UDF",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "python_udf",
            "language": "PYTHON",
            "code": "def python_udf(data):\n    return data.upper()",
            "output_type": "PYTHON_INFERRED",
            "input_types": ["STRING"],
            "description": "Python UDF",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    assert result["udf"]["language"] == "PYTHON"
    assert result["udf"]["output_type"] == "PYTHON_INFERRED"

    mock_list_udfs.assert_called_once_with("12345")
    mock_create_udf.assert_called_once()


def test_ssb_udf_module_create_with_description(module_args, mocker):
    """Test SsbUdfModule creating a UDF with description."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )
    mock_create_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.create_udf",
        return_value=SsbUdf(
            id=1,
            name="test_udf",
            project_id="12345",
            language="JAVASCRIPT",
            code="function test_udf(str) { return str.toUpperCase(); }",
            output_type="STRING",
            input_types=["STRING"],
            description="Test UDF with description",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "language": "JAVASCRIPT",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "input_types": ["STRING"],
            "description": "Test UDF with description",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    assert result["udf"]["description"] == "Test UDF with description"

    mock_list_udfs.assert_called_once_with("12345")
    mock_create_udf.assert_called_once()


def test_ssb_udf_module_update_code(module_args, mocker):
    """Test SsbUdfModule updating UDF code."""
    existing_udf = SsbUdf(
        id=1,
        name="test_udf",
        project_id="12345",
        language="JAVASCRIPT",
        code="function test_udf(str) { return str.toUpperCase(); }",
        output_type="STRING",
        input_types=["STRING"],
    )

    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[existing_udf],
    )
    mock_update_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.update_udf",
        return_value=SsbUdf(
            id=1,
            name="test_udf",
            project_id="12345",
            language="JAVASCRIPT",
            code="function test_udf(str) { return str.toUpperCase() + '!'; }",
            output_type="STRING",
            input_types=["STRING"],
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "code": "function test_udf(str) { return str.toUpperCase() + '!'; }",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    assert "!" in result["udf"]["code"]

    mock_list_udfs.assert_called_once_with("12345")
    mock_update_udf.assert_called_once()


def test_ssb_udf_module_update_idempotent(module_args, mocker):
    """Test SsbUdfModule update with no changes (idempotent)."""
    existing_udf = SsbUdf(
        id=1,
        name="test_udf",
        project_id="12345",
        language="JAVASCRIPT",
        code="function test_udf(str) { return str.toUpperCase(); }",
        output_type="STRING",
        input_types=["STRING"],
    )

    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[existing_udf],
    )
    mock_update_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.update_udf",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is False

    mock_list_udfs.assert_called_once_with("12345")
    mock_update_udf.assert_not_called()


def test_ssb_udf_module_delete_by_name(module_args, mocker):
    """Test SsbUdfModule deleting a UDF by name."""
    existing_udf = SsbUdf(
        id=1,
        name="test_udf",
        project_id="12345",
        language="JAVASCRIPT",
        code="function test_udf(str) { return str.toUpperCase(); }",
        output_type="STRING",
        input_types=["STRING"],
    )

    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[existing_udf],
    )
    mock_delete_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.delete_udf",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    mock_list_udfs.assert_called_once_with("12345")
    mock_delete_udf.assert_called_once_with("12345", 1)


def test_ssb_udf_module_delete_by_id(module_args, mocker):
    """Test SsbUdfModule deleting a UDF by id."""
    existing_udf = SsbUdf(
        id=42,
        name="test_udf",
        project_id="12345",
        language="JAVASCRIPT",
        code="function test_udf(str) { return str.toUpperCase(); }",
        output_type="STRING",
        input_types=["STRING"],
    )

    mock_describe_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.describe_udf",
        return_value=existing_udf,
    )
    mock_delete_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.delete_udf",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "id": 42,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    mock_describe_udf.assert_called_once_with("12345", 42)
    mock_delete_udf.assert_called_once_with("12345", 42)


def test_ssb_udf_module_delete_nonexistent(module_args, mocker):
    """Test SsbUdfModule deleting a non-existent UDF (idempotent)."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )
    mock_delete_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.delete_udf",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "nonexistent_udf",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is False

    mock_list_udfs.assert_called_once_with("12345")
    mock_delete_udf.assert_not_called()


def test_ssb_udf_module_check_mode_create(module_args, mocker):
    """Test SsbUdfModule in check mode for create."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )
    mock_create_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.create_udf",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "language": "JAVASCRIPT",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "input_types": ["STRING"],
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    mock_list_udfs.assert_called_once_with("12345")
    mock_create_udf.assert_not_called()


def test_ssb_udf_module_check_mode_delete(module_args, mocker):
    """Test SsbUdfModule in check mode for delete."""
    existing_udf = SsbUdf(
        id=1,
        name="test_udf",
        project_id="12345",
        language="JAVASCRIPT",
        code="function test_udf(str) { return str.toUpperCase(); }",
        output_type="STRING",
        input_types=["STRING"],
    )

    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[existing_udf],
    )
    mock_delete_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.delete_udf",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    mock_list_udfs.assert_called_once_with("12345")
    mock_delete_udf.assert_not_called()


def test_ssb_udf_module_diff_mode_create(module_args, mocker):
    """Test SsbUdfModule in diff mode for create."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )
    mock_create_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.create_udf",
        return_value=SsbUdf(
            id=1,
            name="test_udf",
            project_id="12345",
            language="JAVASCRIPT",
            code="function test_udf(str) { return str.toUpperCase(); }",
            output_type="STRING",
            input_types=["STRING"],
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "language": "JAVASCRIPT",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "input_types": ["STRING"],
            "state": "present",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    # Note: diff is not exposed at module level in this implementation

    mock_list_udfs.assert_called_once_with("12345")
    mock_create_udf.assert_called_once()


def test_ssb_udf_module_diff_mode_update(module_args, mocker):
    """Test SsbUdfModule in diff mode for update."""
    existing_udf = SsbUdf(
        id=1,
        name="test_udf",
        project_id="12345",
        language="JAVASCRIPT",
        code="function test_udf(str) { return str.toUpperCase(); }",
        output_type="STRING",
        input_types=["STRING"],
    )

    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[existing_udf],
    )
    mock_update_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.update_udf",
        return_value=SsbUdf(
            id=1,
            name="test_udf",
            project_id="12345",
            language="JAVASCRIPT",
            code="function test_udf(str) { return str.toLowerCase(); }",
            output_type="STRING",
            input_types=["STRING"],
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "code": "function test_udf(str) { return str.toLowerCase(); }",
            "state": "present",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    mock_list_udfs.assert_called_once_with("12345")
    mock_update_udf.assert_called_once()


def test_ssb_udf_module_diff_mode_delete(module_args, mocker):
    """Test SsbUdfModule in diff mode for delete."""
    existing_udf = SsbUdf(
        id=1,
        name="test_udf",
        project_id="12345",
        language="JAVASCRIPT",
        code="function test_udf(str) { return str.toUpperCase(); }",
        output_type="STRING",
        input_types=["STRING"],
    )

    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[existing_udf],
    )
    mock_delete_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.delete_udf",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "state": "absent",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True

    mock_list_udfs.assert_called_once_with("12345")
    mock_delete_udf.assert_called_once_with("12345", 1)


def test_ssb_udf_module_missing_name(module_args, mocker):
    """Test SsbUdfModule with missing name parameter on create."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "language": "JAVASCRIPT",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "input_types": ["STRING"],
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_udf.main()

    result = e.value
    assert "name" in result["msg"].lower()

    mock_list_udfs.assert_called_once_with("12345")


def test_ssb_udf_module_missing_language(module_args, mocker):
    """Test SsbUdfModule with missing language parameter on create."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "input_types": ["STRING"],
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_udf.main()

    result = e.value
    assert "language" in result["msg"].lower()

    mock_list_udfs.assert_called_once_with("12345")


def test_ssb_udf_module_missing_code(module_args, mocker):
    """Test SsbUdfModule with missing code parameter on create."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "language": "JAVASCRIPT",
            "output_type": "STRING",
            "input_types": ["STRING"],
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_udf.main()

    result = e.value
    assert "code" in result["msg"].lower()

    mock_list_udfs.assert_called_once_with("12345")


def test_ssb_udf_module_missing_output_type(module_args, mocker):
    """Test SsbUdfModule with missing output_type parameter on create."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "language": "JAVASCRIPT",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "input_types": ["STRING"],
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_udf.main()

    result = e.value
    assert "output_type" in result["msg"].lower()

    mock_list_udfs.assert_called_once_with("12345")


def test_ssb_udf_module_missing_input_types(module_args, mocker):
    """Test SsbUdfModule with missing input_types parameter on create."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test_udf",
            "language": "JAVASCRIPT",
            "code": "function test_udf(str) { return str.toUpperCase(); }",
            "output_type": "STRING",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_udf.main()

    result = e.value
    assert "input_types" in result["msg"].lower()

    mock_list_udfs.assert_called_once_with("12345")


def test_ssb_udf_module_multiple_input_types(module_args, mocker):
    """Test SsbUdfModule creating a UDF with multiple input types."""
    mock_list_udfs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.list_udfs",
        return_value=[],
    )
    mock_create_udf = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_udf.SsbUdfClient.create_udf",
        return_value=SsbUdf(
            id=1,
            name="concat_udf",
            project_id="12345",
            language="JAVASCRIPT",
            code="function concat_udf(str1, str2) { return str1 + str2; }",
            output_type="STRING",
            input_types=["STRING", "STRING"],
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "concat_udf",
            "language": "JAVASCRIPT",
            "code": "function concat_udf(str1, str2) { return str1 + str2; }",
            "output_type": "STRING",
            "input_types": ["STRING", "STRING"],
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_udf.main()

    result = e.value
    assert result["changed"] is True
    assert len(result["udf"]["input_types"]) == 2

    mock_list_udfs.assert_called_once_with("12345")
    mock_create_udf.assert_called_once()

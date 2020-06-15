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

from ansible_collections.cloudera.services.plugins.modules import ssb_table_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbTable,
)

BASE_URL = "https://api.cloudera.internal"
PROJECT_ID = "proj123"


def test_ssb_table_info_module_list_all(module_args, mocker):
    """Test SsbTableInfoModule listing all tables."""
    mock_list_tables = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.list_tables",
        return_value=[
            SsbTable(
                id=1,
                table_name="orders",
                type="kafka",
                metadata={
                    "connector": "kafka",
                    "topic": "orders",
                },
                project_id=PROJECT_ID,
            ),
            SsbTable(
                id=2,
                table_name="customers",
                type="kafka",
                metadata={
                    "connector": "kafka",
                    "topic": "customers",
                },
                project_id=PROJECT_ID,
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
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 2
    assert result["tables"][0]["id"] == 1
    assert result["tables"][0]["table_name"] == "orders"
    assert result["tables"][1]["id"] == 2
    assert result["tables"][1]["table_name"] == "customers"

    mock_list_tables.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_table_info_module_filter_by_name(module_args, mocker):
    """Test SsbTableInfoModule filtering by table name."""
    mock_list_tables = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.list_tables",
        return_value=[
            SsbTable(
                id=1,
                table_name="orders",
                type="kafka",
                metadata={
                    "connector": "kafka",
                    "topic": "orders",
                },
                project_id=PROJECT_ID,
            ),
            SsbTable(
                id=2,
                table_name="customers",
                type="kafka",
                metadata={
                    "connector": "kafka",
                    "topic": "customers",
                },
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "table_name": "orders",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 1
    assert result["tables"][0]["id"] == 1
    assert result["tables"][0]["table_name"] == "orders"

    mock_list_tables.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_table_info_module_filter_by_name_not_found(module_args, mocker):
    """Test SsbTableInfoModule filtering by name when table doesn't exist."""
    mock_list_tables = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.list_tables",
        return_value=[
            SsbTable(
                id=1,
                table_name="orders",
                type="kafka",
                metadata={},
                project_id=PROJECT_ID,
            ),
            SsbTable(
                id=2,
                table_name="customers",
                type="kafka",
                metadata={},
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "table_name": "nonexistent-table",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 0

    mock_list_tables.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_table_info_module_by_id(module_args, mocker):
    """Test SsbTableInfoModule retrieval by ID."""
    mock_describe_table = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.describe_table",
        return_value=SsbTable(
            id=1,
            table_name="orders",
            type="kafka",
            metadata={
                "connector": "kafka",
                "topic": "orders",
                "properties": {
                    "bootstrap.servers": "localhost:9092",
                },
            },
            transform_code="SELECT * FROM raw_orders",
            transform_code_b64_encoded=False,
            project_id=PROJECT_ID,
            created_at="2024-06-01T12:00:00Z",
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
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 1
    assert result["tables"][0]["id"] == 1
    assert result["tables"][0]["table_name"] == "orders"
    assert "metadata" in result["tables"][0]
    assert result["tables"][0]["metadata"]["connector"] == "kafka"
    assert result["tables"][0]["transform_code"] == "SELECT * FROM raw_orders"

    mock_describe_table.assert_called_once_with(
        project_id=PROJECT_ID,
        table_id=1,
    )


def test_ssb_table_info_module_by_id_not_found(module_args, mocker):
    """Test SsbTableInfoModule retrieval by ID when table doesn't exist."""
    mock_describe_table = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.describe_table",
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
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 0

    mock_describe_table.assert_called_once_with(
        project_id=PROJECT_ID,
        table_id=999,
    )


def test_ssb_table_info_module_with_transform_code(module_args, mocker):
    """Test SsbTableInfoModule with transform code."""
    mock_list_tables = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.list_tables",
        return_value=[
            SsbTable(
                id=1,
                table_name="transformed_table",
                type="kafka",
                metadata={
                    "connector": "kafka",
                },
                transform_code="SELECT id, UPPER(name) as name FROM source_table",
                transform_code_b64_encoded=False,
                project_id=PROJECT_ID,
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
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 1
    table = result["tables"][0]
    assert table["transform_code"] == "SELECT id, UPPER(name) as name FROM source_table"
    assert table["transform_code_b64_encoded"] is False

    mock_list_tables.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_table_info_module_check_mode(module_args, mocker):
    """Test SsbTableInfoModule in check mode."""
    mock_list_tables = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.list_tables",
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
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result

    mock_list_tables.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_table_info_module_empty_list(module_args, mocker):
    """Test SsbTableInfoModule with no tables in project."""
    mock_list_tables = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.list_tables",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result
    assert len(result["tables"]) == 0

    mock_list_tables.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_table_info_module_with_complex_metadata(module_args, mocker):
    """Test SsbTableInfoModule with complex metadata structure."""
    mock_list_tables = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_table_info.SsbTableClient.list_tables",
        return_value=[
            SsbTable(
                id=1,
                table_name="complex_table",
                type="kafka",
                metadata={
                    "connector": "kafka",
                    "topic": "complex",
                    "properties": {
                        "bootstrap.servers": "kafka1:9092,kafka2:9092",
                        "group.id": "test-group",
                    },
                    "format": {
                        "type": "json",
                        "json.fail-on-missing-field": "false",
                    },
                    "schema": [
                        {"name": "id", "type": "INT"},
                        {"name": "name", "type": "STRING"},
                        {"name": "timestamp", "type": "TIMESTAMP(3)"},
                    ],
                },
                project_id=PROJECT_ID,
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
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 1
    table = result["tables"][0]
    assert "metadata" in table
    assert "properties" in table["metadata"]
    assert "format" in table["metadata"]
    assert "schema" in table["metadata"]

    mock_list_tables.assert_called_once_with(project_id=PROJECT_ID)

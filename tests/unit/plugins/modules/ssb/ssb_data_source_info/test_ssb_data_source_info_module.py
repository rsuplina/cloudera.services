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

from ansible_collections.cloudera.services.plugins.modules import ssb_data_source_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbDataSource,
)

BASE_URL = "https://api.cloudera.internal"
PROJECT_ID = "proj123"


def test_ssb_data_source_info_module_list_all(module_args, mocker):
    """Test SsbDataSourceInfoModule listing all data sources."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source_info.SsbDataSourceClient.list_data_sources",
        return_value=[
            SsbDataSource(
                id=1,
                name="kafka-source",
                type="KAFKA",
                properties={
                    "bootstrap.servers": "localhost:9092",
                },
                project_id=PROJECT_ID,
            ),
            SsbDataSource(
                id=2,
                name="postgres-source",
                type="POSTGRES",
                properties={
                    "hostname": "localhost",
                    "port": "5432",
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
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["data_sources"]) == 2
    assert result["data_sources"][0]["id"] == 1
    assert result["data_sources"][0]["name"] == "kafka-source"
    assert result["data_sources"][1]["id"] == 2
    assert result["data_sources"][1]["name"] == "postgres-source"

    mock_list_data_sources.assert_called_once_with(project_id=PROJECT_ID, kafka=False)


def test_ssb_data_source_info_module_filter_by_name(module_args, mocker):
    """Test SsbDataSourceInfoModule filtering by name."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source_info.SsbDataSourceClient.list_data_sources",
        return_value=[
            SsbDataSource(
                id=1,
                name="kafka-source",
                type="KAFKA",
                properties={
                    "bootstrap.servers": "localhost:9092",
                },
                project_id=PROJECT_ID,
            ),
            SsbDataSource(
                id=2,
                name="postgres-source",
                type="POSTGRES",
                properties={
                    "hostname": "localhost",
                },
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "kafka-source",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["data_sources"]) == 1
    assert result["data_sources"][0]["id"] == 1
    assert result["data_sources"][0]["name"] == "kafka-source"

    mock_list_data_sources.assert_called_once_with(project_id=PROJECT_ID, kafka=False)


def test_ssb_data_source_info_module_filter_by_name_not_found(module_args, mocker):
    """Test SsbDataSourceInfoModule filtering by name when data source doesn't exist."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source_info.SsbDataSourceClient.list_data_sources",
        return_value=[
            SsbDataSource(
                id=1,
                name="kafka-source",
                type="KAFKA",
                properties={},
                project_id=PROJECT_ID,
            ),
            SsbDataSource(
                id=2,
                name="postgres-source",
                type="POSTGRES",
                properties={},
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "nonexistent-data-source",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["data_sources"]) == 0

    mock_list_data_sources.assert_called_once_with(project_id=PROJECT_ID, kafka=False)


def test_ssb_data_source_info_module_by_id(module_args, mocker):
    """Test SsbDataSourceInfoModule retrieval by ID."""
    mock_describe_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source_info.SsbDataSourceClient.describe_data_source",
        return_value=SsbDataSource(
            id="abc123",
            name="kafka-source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "localhost:9092",
                "topic": "my-topic",
            },
            project_id=PROJECT_ID,
            created_at="2024-06-01T12:00:00Z",
            updated_at="2024-06-02T14:00:00Z",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "id": "abc123",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["data_sources"]) == 1
    assert result["data_sources"][0]["id"] == "abc123"
    assert result["data_sources"][0]["name"] == "kafka-source"
    assert "properties" in result["data_sources"][0]
    assert "bootstrap.servers" in result["data_sources"][0]["properties"]

    mock_describe_data_source.assert_called_once_with(
        project_id=PROJECT_ID,
        data_source_id="abc123",
    )


def test_ssb_data_source_info_module_by_id_not_found(module_args, mocker):
    """Test SsbDataSourceInfoModule retrieval by ID when data source doesn't exist."""
    mock_describe_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source_info.SsbDataSourceClient.describe_data_source",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "id": "abc123",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["data_sources"]) == 0

    mock_describe_data_source.assert_called_once_with(
        project_id=PROJECT_ID,
        data_source_id="abc123",
    )


def test_ssb_data_source_info_module_kafka_filter(module_args, mocker):
    """Test SsbDataSourceInfoModule with kafka filter."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source_info.SsbDataSourceClient.list_data_sources",
        return_value=[
            SsbDataSource(
                id=1,
                name="kafka-source-1",
                type="KAFKA",
                properties={
                    "bootstrap.servers": "localhost:9092",
                },
                project_id=PROJECT_ID,
            ),
            SsbDataSource(
                id=2,
                name="kafka-source-2",
                type="KAFKA",
                properties={
                    "bootstrap.servers": "kafka:9092",
                },
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "kafka": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["data_sources"]) == 2
    assert all(ds["type"] == "KAFKA" for ds in result["data_sources"])

    mock_list_data_sources.assert_called_once_with(project_id=PROJECT_ID, kafka=True)


def test_ssb_data_source_info_module_check_mode(module_args, mocker):
    """Test SsbDataSourceInfoModule in check mode."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source_info.SsbDataSourceClient.list_data_sources",
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
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result

    mock_list_data_sources.assert_called_once_with(project_id=PROJECT_ID, kafka=False)

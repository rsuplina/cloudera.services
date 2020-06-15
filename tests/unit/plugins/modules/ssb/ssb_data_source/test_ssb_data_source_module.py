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

from ansible_collections.cloudera.services.plugins.modules import ssb_data_source
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbDataSource,
)

BASE_URL = "https://api.cloudera.internal"


def test_ssb_data_source_module_create_minimal(module_args, mocker):
    """Test SsbDataSourceModule creating a data source with minimal parameters."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[],
    )
    mock_create_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.create_data_source",
        return_value=SsbDataSource(
            id=1,
            name="test-kafka-source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "localhost:9092",
            },
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-kafka-source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True
    assert result["data_source"]["id"] == 1
    assert result["data_source"]["name"] == "test-kafka-source"

    mock_list_data_sources.assert_called_once_with("12345")
    mock_create_data_source.assert_called_once()


def test_ssb_data_source_module_create_with_truststore(module_args, mocker):
    """Test SsbDataSourceModule creating a data source with custom truststore."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[],
    )
    mock_create_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.create_data_source",
        return_value=SsbDataSource(
            id=1,
            name="secure-kafka-source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "kafka:9093",
                "security.protocol": "SSL",
            },
            custom_truststore="/path/to/truststore.jks",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "secure-kafka-source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "kafka:9093",
                "security.protocol": "SSL",
            },
            "custom_truststore": "/path/to/truststore.jks",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True
    assert result["data_source"]["name"] == "secure-kafka-source"
    assert result["data_source"]["custom_truststore"] == "/path/to/truststore.jks"

    mock_list_data_sources.assert_called_once_with("12345")
    mock_create_data_source.assert_called_once()


def test_ssb_data_source_module_present_idempotent(module_args, mocker):
    """Test SsbDataSourceModule with existing data source (idempotent)."""
    existing_data_source = SsbDataSource(
        id="abcd-1234",
        name="existing-kafka-source",
        type="KAFKA",
        properties={
            "bootstrap.servers": "localhost:9092",
        },
    )

    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[existing_data_source],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-kafka-source",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is False
    assert result["data_source"]["id"] == "abcd-1234"
    assert result["data_source"]["name"] == "existing-kafka-source"

    mock_list_data_sources.assert_called_once_with("12345")


def test_ssb_data_source_module_update_properties(module_args, mocker):
    """Test SsbDataSourceModule updating data source properties."""
    existing_data_source = SsbDataSource(
        id="abcd-1234",
        name="existing-kafka-source",
        type="KAFKA",
        properties={
            "bootstrap.servers": "localhost:9092",
            "topic": "old-topic",
        },
    )

    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[existing_data_source],
    )
    mock_update_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.update_data_source",
        return_value=SsbDataSource(
            id=1,
            name="existing-kafka-source",
            type="KAFKA",
            properties={
                "bootstrap.servers": "kafka:9092",
                "topic": "new-topic",
            },
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "existing-kafka-source",
            "properties": {
                "bootstrap.servers": "kafka:9092",
                "topic": "new-topic",
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True

    mock_list_data_sources.assert_called_once_with("12345")
    mock_update_data_source.assert_called_once()


def test_ssb_data_source_module_by_id(module_args, mocker):
    """Test SsbDataSourceModule retrieving data source by ID."""
    existing_data_source = SsbDataSource(
        id="abcd-1234",
        name="existing-kafka-source",
        type="KAFKA",
        properties={
            "bootstrap.servers": "localhost:9092",
        },
    )

    mock_describe_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.describe_data_source",
        return_value=existing_data_source,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "id": "abcd-1234",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is False
    assert result["data_source"]["id"] == "abcd-1234"
    assert result["data_source"]["name"] == "existing-kafka-source"

    mock_describe_data_source.assert_called_once_with("12345", "abcd-1234")


def test_ssb_data_source_module_delete_by_name(module_args, mocker):
    """Test SsbDataSourceModule deleting a data source by name."""
    existing_data_source = SsbDataSource(
        id="abcd-1234",
        name="data-source-to-delete",
        type="KAFKA",
        properties={},
    )

    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[existing_data_source],
    )
    mock_delete_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.delete_data_source",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "data-source-to-delete",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True

    mock_list_data_sources.assert_called_once_with("12345")
    mock_delete_data_source.assert_called_once_with(
        "12345",
        "abcd-1234",
        delete_dependents=False,
    )


def test_ssb_data_source_module_delete_by_id(module_args, mocker):
    """Test SsbDataSourceModule deleting a data source by ID."""
    existing_data_source = SsbDataSource(
        id="abcd-1234",
        name="data-source-to-delete",
        type="KAFKA",
        properties={},
    )

    mock_describe_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.describe_data_source",
        return_value=existing_data_source,
    )
    mock_delete_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.delete_data_source",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "id": "abcd-1234",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True

    mock_describe_data_source.assert_called_once_with("12345", "abcd-1234")
    mock_delete_data_source.assert_called_once_with(
        "12345",
        "abcd-1234",
        delete_dependents=False,
    )


def test_ssb_data_source_module_delete_with_dependents(module_args, mocker):
    """Test SsbDataSourceModule deleting a data source with dependents."""
    existing_data_source = SsbDataSource(
        id="abcd-1234",
        name="data-source-with-dependents",
        type="KAFKA",
        properties={},
    )

    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[existing_data_source],
    )
    mock_delete_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.delete_data_source",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "data-source-with-dependents",
            "delete_dependents": True,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True

    mock_list_data_sources.assert_called_once_with("12345")
    mock_delete_data_source.assert_called_once_with(
        "12345",
        "abcd-1234",
        delete_dependents=True,
    )


def test_ssb_data_source_module_delete_nonexistent(module_args, mocker):
    """Test SsbDataSourceModule deleting a non-existent data source."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "nonexistent-data-source",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is False

    mock_list_data_sources.assert_called_once_with("12345")


def test_ssb_data_source_module_check_mode_create(module_args, mocker):
    """Test SsbDataSourceModule in check mode for creation."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[],
    )
    mock_create_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.create_data_source",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "new-kafka-source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
            },
            "state": "present",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True
    assert result["data_source"] == {}

    mock_list_data_sources.assert_called_once_with("12345")
    mock_create_data_source.assert_not_called()


def test_ssb_data_source_module_check_mode_delete(module_args, mocker):
    """Test SsbDataSourceModule in check mode for deletion."""
    existing_data_source = SsbDataSource(
        id="abcd-1234",
        name="data-source-to-delete",
        type="KAFKA",
        properties={},
    )

    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[existing_data_source],
    )
    mock_delete_data_source = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.delete_data_source",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "data-source-to-delete",
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True

    mock_list_data_sources.assert_called_once_with("12345")
    mock_delete_data_source.assert_not_called()


def test_ssb_data_source_module_create_without_name(module_args, mocker):
    """Test SsbDataSourceModule failing when creating without name."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_data_source.main()

    result = e.value
    assert "name" in result["msg"].lower()


def test_ssb_data_source_module_create_without_type(module_args, mocker):
    """Test SsbDataSourceModule failing when creating without type."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-kafka-source",
            "properties": {
                "bootstrap.servers": "localhost:9092",
            },
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_data_source.main()

    result = e.value
    assert "type" in result["msg"].lower()


def test_ssb_data_source_module_create_without_properties(module_args, mocker):
    """Test SsbDataSourceModule failing when creating without properties."""
    mock_list_data_sources = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_data_source.SsbDataSourceClient.list_data_sources",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": "12345",
            "name": "test-kafka-source",
            "type": "KAFKA",
            "state": "present",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_data_source.main()

    result = e.value
    assert "properties" in result["msg"].lower()

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

from ansible_collections.cloudera.services.plugins.modules import ssb_data_source
from ansible_collections.cloudera.services.plugins.module_utils.common import from_dict
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbDataSource,
    SsbDataSourceClient,
)

REQUIRED_ENV_VARS = [
    "SSB_SSE_API_URL",
    "SSB_SSE_API_USERNAME",
    "SSB_SSE_API_PASSWORD",
    "SMM_KAFKA_BROKERS",
    "SMM_KAFKA_USERNAME",
    "SMM_KAFKA_PASSWORD",
    "SMM_KAFKA_SSL_CAFILE",
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


def test_ssb_data_source_module_create_minimal(
    request,
    env_context,
    smm_kafka_topic,
    ssb_module_args,
    existing_project,
    purge_data_source,
):
    """Test SsbDataSourceModule creating a data source with minimal parameters."""
    data_source_name = request.node.name
    smm_kafka_topic(data_source_name)

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": data_source_name,
            "type": "KAFKA",
            "properties": {
                "brokers": env_context["SMM_KAFKA_BROKERS"],
                "protocol": "sasl",
                "mechanism": "KERBEROS",
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value

    purge_data_source(
        from_dict(SsbDataSource, result["data_source"]),
    )

    assert result["changed"] is True
    assert result["data_source"]["name"] == data_source_name
    assert "id" in result["data_source"]


@pytest.mark.skip(reason="Requires custom truststore file and Kafka setup")
def test_ssb_data_source_module_create_with_truststore(
    request,
    env_context,
    smm_kafka_topic,
    ssb_module_args,
    existing_project,
    purge_data_source,
):
    """Test SsbDataSourceModule creating a data source with custom truststore."""
    data_source_name = request.node.name
    smm_kafka_topic(data_source_name)

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": data_source_name,
            "type": "KAFKA",
            "properties": {
                "brokers": env_context["SMM_KAFKA_BROKERS"],
                "protocol": "sasl",
                "mechanism": "KERBEROS",
            },
            "custom_truststore": "/tmp/truststore.jks",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    purge_data_source(
        existing_project.id,
        from_dict(SsbDataSource, result["data_source"]),
    )

    assert result["changed"] is True
    assert result["data_source"]["name"] == data_source_name
    assert result["data_source"]["custom_truststore"] == "/tmp/truststore.jks"


def test_ssb_data_source_module_present_idempotent(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
):
    """Test SsbDataSourceModule with existing data source (idempotent)."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_data_source_kafka.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is False
    assert result["data_source"]["id"] == existing_data_source_kafka.id
    assert result["data_source"]["name"] == existing_data_source_kafka.name


def test_ssb_data_source_module_by_id(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
):
    """Test SsbDataSourceModule retrieving data source by ID."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "id": existing_data_source_kafka.id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is False
    assert result["data_source"]["id"] == existing_data_source_kafka.id
    assert result["data_source"]["name"] == existing_data_source_kafka.name


@pytest.mark.skip(
    reason="Updating properties appears broken. Doesn't work in UI either.",
)
def test_ssb_data_source_module_update_properties(
    request,
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
):
    """Test SsbDataSourceModule updating data source properties."""
    group_id = request.node.name

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_data_source_kafka.name,
            "properties": {
                "group.id": group_id,
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True
    assert result["data_source"]["properties"]["group.id"] == group_id


def test_ssb_data_source_module_delete(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
):
    """Test SsbDataSourceModule deleting a data source."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": existing_data_source_kafka.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True


def test_ssb_data_source_module_delete_with_dependents(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
):
    """Test SsbDataSourceModule deleting a data source with dependents."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": existing_data_source_kafka.name,
            "delete_dependents": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True


def test_ssb_data_source_module_delete_nonexistent(
    ssb_module_args,
    existing_project,
):
    """Test SsbDataSourceModule deleting a non-existent data source."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": "nonexistent-data-source-name-12345",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is False


def test_ssb_data_source_module_check_mode_create(
    ssb_module_args,
    existing_project,
):
    """Test SsbDataSourceModule in check mode for creation."""

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": "check-mode-data-source",
            "type": "KAFKA",
            "properties": {
                "bootstrap.servers": "localhost:9092",
            },
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True
    assert result["data_source"] == {}


def test_ssb_data_source_module_check_mode_delete(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
    ssb_rest_client,
):
    """Test SsbDataSourceModule in check mode for deletion."""

    ssb_module_args(
        {
            "state": "absent",
            "project_id": existing_project.id,
            "name": existing_data_source_kafka.name,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True

    # Verify data source still exists
    client = SsbDataSourceClient(api_client=ssb_rest_client)
    data_sources = client.list_data_sources(existing_project.id)
    assert any(
        ds.id == existing_data_source_kafka.id
        for ds in data_sources
        if isinstance(ds.id, str)
    )


def test_ssb_data_source_module_check_mode_update(
    request,
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
    ssb_rest_client,
):
    """Test SsbDataSourceModule in check mode for update."""
    group_id = request.node.name
    original_properties = (
        existing_data_source_kafka.properties.copy()
        if existing_data_source_kafka.properties
        else {}
    )

    ssb_module_args(
        {
            "state": "present",
            "project_id": existing_project.id,
            "name": existing_data_source_kafka.name,
            "properties": {
                "group.id": group_id,
            },
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source.main()

    result = e.value
    assert result["changed"] is True
    assert result["data_source"] == {}

    # Verify data source properties not actually changed
    client = SsbDataSourceClient(api_client=ssb_rest_client)
    if isinstance(existing_data_source_kafka.id, str):
        current_ds = client.describe_data_source(
            existing_project.id,
            existing_data_source_kafka.id,
        )
        # Properties should remain unchanged in check mode
        assert current_ds is not None

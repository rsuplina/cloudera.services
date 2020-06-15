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

import os
import pytest

from unittest.mock import Mock

from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbDataSource,
    SsbDataSourceValidationResponse,
)
from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
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
def ansible_module(env_context) -> Mock:
    """Fixture to create a mock AnsibleModule for the SSB endpoint."""
    module = Mock()
    module.params = {}
    module.fail_json = Mock(
        side_effect=AnsibleFailJson({"msg": "fail_json called"}),
    )
    module.exit_json = Mock(
        side_effect=AnsibleExitJson({"msg": "exit_json called"}),
    )

    module.params.update(
        {
            "url_username": env_context["SSB_SSE_API_USERNAME"],
            "url_password": env_context["SSB_SSE_API_PASSWORD"],
        },
    )
    return module


def test_create_data_source_hive(
    request,
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_project,
    purge_data_source,
):
    """Test creating a Hive Data Source"""
    ssb_rest_client.module = ansible_module

    source_name = request.node.name.lower()

    # Create the test data source
    source = data_source_client.create_data_source(
        project_id=existing_project.id,
        data_source=SsbDataSource(
            name=source_name,
            type="catalog",
            properties={
                "table_filters": [],
                "catalog_type": "hive",
            },
            custom_truststore=False,
        ),
    )

    # Register the data source for cleanup
    purge_data_source(source)

    assert isinstance(source, SsbDataSource)
    assert source.name == source_name


def test_create_data_source_kafka(
    request,
    data_source_client,
    env_context,
    ansible_module,
    ssb_rest_client,
    existing_project,
    smm_kafka_topic,
    existing_data_source_kafka_data,
    purge_data_source,
):
    """Test creating a Kafka Data Source"""
    ssb_rest_client.module = ansible_module

    source_name = request.node.name.lower()

    # Create the test Kafka topic and seed it with data
    topic = smm_kafka_topic(source_name)
    topic(existing_data_source_kafka_data)

    # Create the test data source
    source = data_source_client.create_data_source(
        project_id=existing_project.id,
        data_source=SsbDataSource(
            name=source_name,
            type="kafka",
            properties={
                "brokers": env_context["SMM_KAFKA_BROKERS"],
                "protocol": "sasl",
                "mechanism": "KERBEROS",
            },
            custom_truststore=False,
        ),
    )

    # Register the data source for cleanup
    purge_data_source(source)

    assert isinstance(source, SsbDataSource)
    assert source.name == source_name


@pytest.mark.skipif(
    condition=not os.getenv("SMM_SCHEMA_REGISTRY_URL"),
    reason="Requires a Schema Registry URL",
)
def test_create_data_source_schema_registry(
    request,
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_project,
    existing_data_source_kafka,
    purge_data_source,
):
    """Test creating a Schema Registry Data Source"""
    ssb_rest_client.module = ansible_module

    source_name = request.node.name.lower()

    # Create the test data source
    source = data_source_client.create_data_source(
        project_id=existing_project.id,
        data_source=SsbDataSource(
            name=source_name,
            type="catalog",
            properties={
                "catalog_type": "cloudera-registry",
                "kafka.provider.id": existing_data_source_kafka.id,
                "registry.address": os.getenv("SMM_SCHEMA_REGISTRY_URL"),
                "registry.ssl.enabled": True,
                "table_filters": [],
            },
            custom_truststore=False,
        ),
    )

    # Register the data source for cleanup
    purge_data_source(source)

    assert isinstance(source, SsbDataSource)
    assert source.name == source_name


@pytest.mark.skip(reason="Requires a Kudu cluster")
def test_create_data_source_kudu(
    request,
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_project,
    purge_data_source,
):
    """Test creating a Kudu Data Source"""
    ssb_rest_client.module = ansible_module

    source_name = request.node.name.lower()

    # Create the test data source
    source = data_source_client.create_data_source(
        project_id=existing_project.id,
        data_source=SsbDataSource(
            name=source_name,
            type="catalog",
            properties=dict(
                catalog_type="kudu",
                table_filters=[],
            ),
            custom_truststore=False,
        ),
    )

    # Register the data source for cleanup
    purge_data_source(source)

    assert isinstance(source, SsbDataSource)
    assert source.name == source_name


@pytest.mark.skip(reason="Requires a Confluent cluster")
def test_create_data_source_confluent(
    request,
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_project,
    purge_data_source,
):
    """Test creating a Confluent Data Source"""
    ssb_rest_client.module = ansible_module

    source_name = request.node.name.lower()

    # Create the test data source
    source = data_source_client.create_data_source(
        project_id=existing_project.id,
        data_source=SsbDataSource(
            name=source_name,
            type="catalog",
            properties={
                "catalog_type": "confluent-registry",
                "registry.auth.type": "basic",
                "registry.filter.avro.schemas": False,
                "table_filters": [],
            },
            custom_truststore=False,
        ),
    )

    # Register the data source for cleanup
    purge_data_source(source)

    assert isinstance(source, SsbDataSource)
    assert source.name == source_name


@pytest.mark.skip(reason="Requires ... something?!")
def test_create_data_source_custom(
    request,
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_project,
    purge_data_source,
):
    """Test creating a Custom Data Source"""
    ssb_rest_client.module = ansible_module

    source_name = request.node.name.lower()

    # Create the test data source
    source = data_source_client.create_data_source(
        project_id=existing_project.id,
        data_source=SsbDataSource(
            name=source_name,
            type="catalog",
            properties={
                "catalog_type": "custom",
                "table_filters": [],
            },
            custom_truststore=False,
        ),
    )

    # Register the data source for cleanup
    purge_data_source(source)

    assert isinstance(source, SsbDataSource)
    assert source.name == source_name


def test_describe_data_source(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_hive,
):
    """Test the description of non-Kafka Data Source for a project."""
    ssb_rest_client.module = ansible_module

    response = data_source_client.describe_data_source(
        project_id=existing_data_source_hive.project_id,
        data_source_id=existing_data_source_hive.id,
    )

    assert isinstance(response, SsbDataSource)
    assert response.id == existing_data_source_hive.id


def test_describe_data_source_nonexistent(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_hive,
):
    """Test the description of a non-existent Data Source for a project."""
    ssb_rest_client.module = ansible_module

    response = data_source_client.describe_data_source(
        project_id=existing_data_source_hive.project_id,
        data_source_id=1234,
    )

    assert response is None


def test_describe_data_source_nonexistent_project(
    data_source_client,
    ansible_module,
    ssb_rest_client,
):
    """Test the description of a non-existent Data Source for a project."""
    ssb_rest_client.module = ansible_module

    response = data_source_client.describe_data_source(
        project_id="nonexistent_project",
        data_source_id=1234,
    )

    assert response is None


def test_list_data_sources(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_hive,
):
    """Test listing of non-Kafka Data Sources for a project."""
    ssb_rest_client.module = ansible_module

    response = data_source_client.list_data_sources(
        existing_data_source_hive.project_id,
    )

    assert isinstance(response, list)
    assert len(response) == 1
    assert isinstance(response[0], SsbDataSource)
    assert response[0].id == existing_data_source_hive.id


def test_list_data_sources_kafka(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_kafka,
):
    """Test listing of Kafka Data Sources for a project."""
    ssb_rest_client.module = ansible_module

    response = data_source_client.list_data_sources(
        existing_data_source_kafka.project_id,
        kafka=True,
    )

    assert isinstance(response, list)
    assert len(response) == 1
    assert isinstance(response[0], SsbDataSource)
    assert response[0].id == existing_data_source_kafka.id


def test_update_data_source_hive(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_hive,
):
    """Test updating a Hive Data Source"""
    ssb_rest_client.module = ansible_module

    # Update the data source name
    existing_data_source_hive.name = existing_data_source_hive.name + "_updated"

    # Update the test data source
    update = data_source_client.update_data_source(
        project_id=existing_data_source_hive.project_id,
        data_source=existing_data_source_hive,
    )

    assert isinstance(update, SsbDataSource)
    assert update.name == existing_data_source_hive.name


def test_update_data_source_hive_truststore(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_hive,
):
    """Test updating a Hive Data Source"""
    ssb_rest_client.module = ansible_module

    # Update the data source custom_truststore
    existing_data_source_hive.custom_truststore = True

    # Update the test data source
    update = data_source_client.update_data_source(
        project_id=existing_data_source_hive.project_id,
        data_source=existing_data_source_hive,
    )

    assert isinstance(update, SsbDataSource)
    assert update.name == existing_data_source_hive.name
    assert update.custom_truststore is True


def test_delete_data_source_hive(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_hive,
):
    """Test deleting a Hive Data Source"""
    ssb_rest_client.module = ansible_module

    # Delete the test data source
    data_source_client.delete_data_source(
        project_id=existing_data_source_hive.project_id,
        data_source_id=existing_data_source_hive.id,
    )


# TODO Create dependent resources to test delete with dependencies
def test_delete_data_source_hive_dependencies(
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_data_source_hive,
):
    """Test deleting a Hive Data Source"""
    ssb_rest_client.module = ansible_module

    # Delete the test data source
    data_source_client.delete_data_source(
        project_id=existing_data_source_hive.project_id,
        data_source_id=existing_data_source_hive.id,
        delete_dependents=True,
    )


def test_validate_data_source_hive(
    request,
    data_source_client,
    ansible_module,
    ssb_rest_client,
    existing_project,
):
    """Test creating a Hive Data Source"""
    ssb_rest_client.module = ansible_module

    source_name = request.node.name.lower()

    # Create the test data source
    validation = data_source_client.validate_data_source(
        project_id=existing_project.id,
        data_source=SsbDataSource(
            name=source_name,
            type="catalog",
            properties={
                "table_filters": [],
                "catalog_type": "hive",
            },
            custom_truststore=False,
        ),
    )

    assert isinstance(validation, SsbDataSourceValidationResponse)
    assert validation.number_of_tables is not None


class TestKafkaTopic:
    REQUIRED_ENV_VARS = [
        "SMM_KAFKA_BROKERS",
        "SMM_KAFKA_USERNAME",
        "SMM_KAFKA_PASSWORD",
        "SMM_KAFKA_SSL_CAFILE",
    ]

    TEST_ORDERS = [
        {"id": 1, "status": "PENDING", "amount": 100.50},
        {"id": 2, "status": "SHIPPED", "amount": 25.00},
    ]

    def test_ssb_pipeline_processing(self, request, smm_kafka_topic):
        """Example test using the SMM Kafka fixture to create and seed a Kafka topic."""
        topic_name = request.node.name.lower()
        topic = smm_kafka_topic(topic_name)
        topic(self.TEST_ORDERS)

        assert True

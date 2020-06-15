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

from ansible_collections.cloudera.services.plugins.modules import ssb_data_source_info


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


def test_ssb_data_source_info_module_list_all(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
    existing_data_source_hive,
):
    """Test SsbDataSourceInfoModule list all data sources."""

    ssb_module_args({"project_id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result
    assert isinstance(result["data_sources"], list)
    assert any(
        ds["id"] == existing_data_source_kafka.id for ds in result["data_sources"]
    )
    assert any(
        ds["id"] == existing_data_source_hive.id for ds in result["data_sources"]
    )


def test_ssb_data_source_info_module_by_name(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
):
    """Test SsbDataSourceInfoModule get data source by name."""

    ssb_module_args(
        {"project_id": existing_project.id, "name": existing_data_source_kafka.name},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result
    assert len(result["data_sources"]) == 1
    assert result["data_sources"][0]["id"] == existing_data_source_kafka.id
    assert result["data_sources"][0]["name"] == existing_data_source_kafka.name


def test_ssb_data_source_info_module_by_id(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
):
    """Test SsbDataSourceInfoModule get data source by id."""

    ssb_module_args(
        {"project_id": existing_project.id, "id": existing_data_source_kafka.id},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result
    assert len(result["data_sources"]) == 1
    assert result["data_sources"][0]["id"] == existing_data_source_kafka.id
    assert result["data_sources"][0]["name"] == existing_data_source_kafka.name


def test_ssb_data_source_info_module_nonexistent_name(
    ssb_module_args,
    existing_project,
):
    """Test SsbDataSourceInfoModule with nonexistent data source name."""

    ssb_module_args(
        {"project_id": existing_project.id, "name": "nonexistent-data-source-12345"},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result
    assert len(result["data_sources"]) == 0


def test_ssb_data_source_info_module_nonexistent_id(ssb_module_args, existing_project):
    """Test SsbDataSourceInfoModule with nonexistent data source id."""

    ssb_module_args({"project_id": existing_project.id, "id": 999999})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result
    assert len(result["data_sources"]) == 0


def test_ssb_data_source_info_module_check_mode(ssb_module_args, existing_project):
    """Test SsbDataSourceInfoModule in check mode."""

    ssb_module_args({"project_id": existing_project.id, "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result


def test_ssb_data_source_info_module_kafka_filter(
    ssb_module_args,
    existing_project,
    existing_data_source_kafka,
    existing_data_source_hive,
):
    """Test SsbDataSourceInfoModule with kafka filter."""

    ssb_module_args({"project_id": existing_project.id, "kafka": True})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_data_source_info.main()

    result = e.value
    assert result["changed"] is False
    assert "data_sources" in result
    assert isinstance(result["data_sources"], list)
    # Verify that our test data source appears (it's a KAFKA type)
    assert any(
        ds["id"] == existing_data_source_kafka.id for ds in result["data_sources"]
    )
    # Verify that the non-KAFKA data source does not appear
    assert not any(
        ds["id"] == existing_data_source_hive.id for ds in result["data_sources"]
    )

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

from ansible_collections.cloudera.services.plugins.modules import ssb_table_info

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


def test_ssb_table_info_module_list_all(
    ssb_module_args,
    existing_project,
    existing_table_kafka,
):
    """Test SsbTableInfoModule list all tables."""

    ssb_module_args({"project_id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result
    assert isinstance(result["tables"], list)
    assert any(table["id"] == existing_table_kafka.id for table in result["tables"])


def test_ssb_table_info_module_by_name(
    ssb_module_args,
    existing_project,
    existing_table_kafka,
):
    """Test SsbTableInfoModule get table by name."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "table_name": existing_table_kafka.table_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result
    assert len(result["tables"]) == 1
    assert result["tables"][0]["id"] == existing_table_kafka.id
    assert result["tables"][0]["table_name"] == existing_table_kafka.table_name


def test_ssb_table_info_module_by_id(
    ssb_module_args,
    existing_project,
    existing_table_kafka,
):
    """Test SsbTableInfoModule get table by id."""

    ssb_module_args({"project_id": existing_project.id, "id": existing_table_kafka.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result
    assert len(result["tables"]) == 1
    assert result["tables"][0]["id"] == existing_table_kafka.id
    assert result["tables"][0]["table_name"] == existing_table_kafka.table_name


def test_ssb_table_info_module_nonexistent_name(ssb_module_args, existing_project):
    """Test SsbTableInfoModule with nonexistent table name."""

    ssb_module_args(
        {"project_id": existing_project.id, "table_name": "nonexistent-table-12345"},
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result
    assert len(result["tables"]) == 0


def test_ssb_table_info_module_nonexistent_id(ssb_module_args, existing_project):
    """Test SsbTableInfoModule with nonexistent table id."""

    ssb_module_args({"project_id": existing_project.id, "id": 999999})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result
    assert len(result["tables"]) == 0


def test_ssb_table_info_module_check_mode(ssb_module_args, existing_project):
    """Test SsbTableInfoModule in check mode."""

    ssb_module_args({"project_id": existing_project.id, "_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result


def test_ssb_table_info_module_with_metadata(
    ssb_module_args,
    existing_project,
    existing_table_kafka,
):
    """Test SsbTableInfoModule with table metadata."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "table_name": existing_table_kafka.table_name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["tables"]) == 1
    table = result["tables"][0]
    assert "metadata" in table
    assert (
        table["type"] == "ssb"
    )  # For some reason, the type is reported as "ssb" instead of "kafka" in the SSB API response


def test_ssb_table_info_module_multiple_tables(
    ssb_module_args,
    existing_project,
    existing_table_kafka,
):
    """Test SsbTableInfoModule listing multiple tables."""

    ssb_module_args({"project_id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_table_info.main()

    result = e.value
    assert result["changed"] is False
    assert "tables" in result
    assert isinstance(result["tables"], list)
    # Should have at least the existing_table_kafka
    assert len(result["tables"]) >= 1
    table_ids = [table["id"] for table in result["tables"]]
    assert existing_table_kafka.id in table_ids

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

from ansible_collections.cloudera.services.plugins.modules import (
    ranger_service_info,
)
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerService,
)

BASE_URL = "https://ranger.example"

SERVICE_ONE = RangerService(
    id=1,
    guid="service-guid-1",
    name="hdfs_service",
    type="hdfs",
    display_name="HDFS Service",
    is_enabled=True,
)

SERVICE_TWO = RangerService(
    id=2,
    guid="service-guid-2",
    name="hive_service",
    type="hive",
    display_name="Hive Service",
    is_enabled=True,
)


def test_ranger_service_info_module_list_all(module_args, mocker):
    """Test RangerServiceInfoModule listing all services."""
    mock_list_services = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.list_services",
        return_value=[SERVICE_ONE, SERVICE_TWO],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 2
    assert result["services"][0]["id"] == 1
    assert result["services"][0]["name"] == "hdfs_service"
    assert result["services"][1]["id"] == 2
    assert result["services"][1]["name"] == "hive_service"

    mock_list_services.assert_called_once_with()


def test_ranger_service_info_module_by_id(module_args, mocker):
    """Test RangerServiceInfoModule retrieval by id."""
    mock_get_by_id = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.get_service_by_id",
        return_value=SERVICE_ONE,
    )
    mock_list_services = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.list_services",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "id": 1,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 1
    assert result["services"][0]["id"] == 1
    assert result["services"][0]["name"] == "hdfs_service"

    mock_get_by_id.assert_called_once_with(service_id=1)
    mock_list_services.assert_not_called()


def test_ranger_service_info_module_by_id_not_found(module_args, mocker):
    """Test RangerServiceInfoModule retrieval by id when the service doesn't exist."""
    mock_get_by_id = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.get_service_by_id",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "id": 999,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 0

    mock_get_by_id.assert_called_once_with(service_id=999)


def test_ranger_service_info_module_by_name(module_args, mocker):
    """Test RangerServiceInfoModule retrieval by name."""
    mock_get_by_name = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.get_service_by_name",
        return_value=SERVICE_TWO,
    )
    mock_list_services = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.list_services",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": "hive_service",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 1
    assert result["services"][0]["id"] == 2
    assert result["services"][0]["name"] == "hive_service"

    mock_get_by_name.assert_called_once_with(service_name="hive_service")
    mock_list_services.assert_not_called()


def test_ranger_service_info_module_by_name_not_found(module_args, mocker):
    """Test RangerServiceInfoModule retrieval by name when the service doesn't exist."""
    mock_get_by_name = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.get_service_by_name",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": "nonexistent_service",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 0

    mock_get_by_name.assert_called_once_with(service_name="nonexistent_service")


def test_ranger_service_info_module_empty_list(module_args, mocker):
    """Test RangerServiceInfoModule with no services present."""
    mock_list_services = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.list_services",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert result["services"] == []

    mock_list_services.assert_called_once_with()


def test_ranger_service_info_module_check_mode(module_args, mocker):
    """Test RangerServiceInfoModule in check mode still returns data (read-only)."""
    mock_list_services = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service_info.RangerServiceClient.list_services",
        return_value=[SERVICE_ONE],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["services"]) == 1

    mock_list_services.assert_called_once_with()

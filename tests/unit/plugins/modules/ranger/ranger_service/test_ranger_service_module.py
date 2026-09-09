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

from ansible_collections.cloudera.services.plugins.modules import ranger_service
from ansible_collections.cloudera.services.plugins.module_utils.ranger import (
    RangerService,
)

BASE_URL = "https://ranger.example"

EXISTING_SERVICE = RangerService(
    id=5,
    guid="service-guid-5",
    name="test_service",
    type="hdfs",
    display_name="Test Service",
    description="An existing HDFS service",
    tag_service="",
    is_enabled=True,
    configs={"username": "hdfs"},
    version=1,
)


def test_ranger_service_module_create_minimal(module_args, mocker):
    """Test RangerServiceModule creating a new service with only a name."""
    mock_get_by_name = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=None,
    )
    mock_create = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.create_service",
        return_value=RangerService(
            id=1,
            guid="new-service-guid",
            name="test02",
            is_enabled=True,
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": "test02",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["id"] == 1
    assert result["service"]["name"] == "test02"
    assert "diff" not in result

    mock_get_by_name.assert_called_once_with("test02")
    mock_create.assert_called_once()


def test_ranger_service_module_create_full(module_args, mocker):
    """Test RangerServiceModule creating a new service with all fields set."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=None,
    )
    mock_create = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.create_service",
        return_value=RangerService(
            id=2,
            guid="hdfs-service-guid",
            name="test_hdfs",
            type="hdfs",
            display_name="HDFS Service",
            description="Created by unit test",
            tag_service="cm_tag",
            is_enabled=True,
            configs={
                "username": "hdfs",
                "password": "hdfs",
                "fs.default.name": "hdfs://namenode:8020",
            },
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": "test_hdfs",
            "type": "hdfs",
            "display_name": "HDFS Service",
            "description": "Created by unit test",
            "tag_service": "cm_tag",
            "configs": {
                "username": "hdfs",
                "password": "hdfs",
                "fs.default.name": "hdfs://namenode:8020",
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["name"] == "test_hdfs"
    assert result["service"]["type"] == "hdfs"
    assert result["service"]["configs"]["fs.default.name"] == "hdfs://namenode:8020"

    call_kwargs = mock_create.call_args[0][0]
    assert call_kwargs.name == "test_hdfs"
    assert call_kwargs.type == "hdfs"
    assert call_kwargs.display_name == "HDFS Service"
    assert call_kwargs.tag_service == "cm_tag"
    assert call_kwargs.is_enabled is True


def test_ranger_service_module_create_check_mode(module_args, mocker):
    """Test RangerServiceModule create in check mode does not call the API."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=None,
    )
    mock_create = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.create_service",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": "test02",
            "type": "hdfs",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["name"] == "test02"
    assert result["service"]["type"] == "hdfs"

    mock_create.assert_not_called()


def test_ranger_service_module_create_diff_mode(module_args, mocker):
    """Test RangerServiceModule create in diff mode reports before/after."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=None,
    )
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.create_service",
        return_value=RangerService(id=1, name="test02", type="hdfs", is_enabled=True),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": "test02",
            "type": "hdfs",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert "diff" in result
    assert result["diff"]["before"] == {}
    assert result["diff"]["after"]["name"] == "test02"
    assert result["diff"]["after"]["type"] == "hdfs"


def test_ranger_service_module_present_no_changes(module_args, mocker):
    """Test RangerServiceModule present with no drift is a no-op."""
    mock_get_by_name = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=EXISTING_SERVICE,
    )
    mock_update = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.update_service",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": EXISTING_SERVICE.name,
            "type": EXISTING_SERVICE.type,
            "display_name": EXISTING_SERVICE.display_name,
            "description": EXISTING_SERVICE.description,
            "configs": EXISTING_SERVICE.configs,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is False
    assert result["service"]["id"] == EXISTING_SERVICE.id
    assert result["service"]["name"] == EXISTING_SERVICE.name

    mock_get_by_name.assert_called_once_with(EXISTING_SERVICE.name)
    mock_update.assert_not_called()


def test_ranger_service_module_update_in_place(module_args, mocker):
    """Test RangerServiceModule updates an existing service in place (no delete/recreate)."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=EXISTING_SERVICE,
    )
    mock_delete = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.delete_service_by_id",
    )
    mock_update = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.update_service",
        return_value=RangerService(
            id=EXISTING_SERVICE.id,
            name=EXISTING_SERVICE.name,
            type=EXISTING_SERVICE.type,
            description="Updated description",
            is_enabled=True,
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": EXISTING_SERVICE.name,
            "type": EXISTING_SERVICE.type,
            "description": "Updated description",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["description"] == "Updated description"

    mock_update.assert_called_once()
    updated_service = mock_update.call_args[0][0]
    assert updated_service.id == EXISTING_SERVICE.id
    assert updated_service.description == "Updated description"

    # The module replaces the service in place; it must never delete it.
    mock_delete.assert_not_called()


def test_ranger_service_module_update_check_mode(module_args, mocker):
    """Test RangerServiceModule update in check mode does not call the API."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=EXISTING_SERVICE,
    )
    mock_update = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.update_service",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": EXISTING_SERVICE.name,
            "description": "Updated in check mode",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"]["description"] == "Updated in check mode"

    mock_update.assert_not_called()


def test_ranger_service_module_update_diff_mode(module_args, mocker):
    """Test RangerServiceModule update in diff mode reports before/after."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=EXISTING_SERVICE,
    )
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.update_service",
        return_value=RangerService(
            id=EXISTING_SERVICE.id,
            name=EXISTING_SERVICE.name,
            description="Updated description",
            is_enabled=True,
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": EXISTING_SERVICE.name,
            "description": "Updated description",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert "diff" in result
    assert result["diff"]["before"]["description"] == EXISTING_SERVICE.description
    assert result["diff"]["after"]["description"] == "Updated description"


def test_ranger_service_module_delete_existing(module_args, mocker):
    """Test RangerServiceModule deletes an existing service."""
    mock_get_by_name = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=EXISTING_SERVICE,
    )
    mock_delete = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.delete_service_by_id",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": EXISTING_SERVICE.name,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["service"] == {}

    mock_get_by_name.assert_called_once_with(EXISTING_SERVICE.name)
    mock_delete.assert_called_once_with(EXISTING_SERVICE.id)


def test_ranger_service_module_delete_nonexistent(module_args, mocker):
    """Test RangerServiceModule delete of a nonexistent service is a no-op."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=None,
    )
    mock_delete = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.delete_service_by_id",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": "nonexistent_service",
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is False
    assert result["service"] == {}

    mock_delete.assert_not_called()


def test_ranger_service_module_delete_check_mode(module_args, mocker):
    """Test RangerServiceModule delete in check mode does not call the API."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=EXISTING_SERVICE,
    )
    mock_delete = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.delete_service_by_id",
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": EXISTING_SERVICE.name,
            "state": "absent",
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True

    mock_delete.assert_not_called()


def test_ranger_service_module_delete_diff_mode(module_args, mocker):
    """Test RangerServiceModule delete in diff mode reports before/after."""
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.get_service_by_name",
        return_value=EXISTING_SERVICE,
    )
    mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ranger_service.RangerServiceClient.delete_service_by_id",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
            "name": EXISTING_SERVICE.name,
            "state": "absent",
            "_ansible_diff": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()

    result = e.value
    assert result["changed"] is True
    assert result["diff"]["before"]["name"] == EXISTING_SERVICE.name
    assert result["diff"]["after"] == {}


def test_ranger_service_module_missing_name_fails(module_args, mocker):
    """Test RangerServiceModule fails fast when name is not provided."""
    module_args(
        {
            "endpoint": BASE_URL,
            "url_username": "admin",
            "url_password": "changeme",
        },
    )

    with pytest.raises(AnsibleFailJson):
        ranger_service.main()

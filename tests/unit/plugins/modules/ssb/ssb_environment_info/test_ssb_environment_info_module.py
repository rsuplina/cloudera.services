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

from ansible_collections.cloudera.services.plugins.modules import ssb_environment_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbEnvironment,
    SsbEnvironmentSecuredProperty,
)

BASE_URL = "https://api.cloudera.internal"
PROJECT_ID = "proj123"


def test_ssb_environment_info_module_list_all(module_args, mocker):
    """Test SsbEnvironmentInfoModule listing all environments."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment_info.SsbEnvironmentClient.list_environments",
        return_value=[
            SsbEnvironment(
                id=1,
                name="dev",
                secured_props={
                    "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                        value="localhost:9092",
                        sensitive=False,
                    ),
                },
                project=PROJECT_ID,
            ),
            SsbEnvironment(
                id=2,
                name="prod",
                secured_props={
                    "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                        value="kafka:9092",
                        sensitive=False,
                    ),
                },
                project=PROJECT_ID,
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
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["environments"]) == 2
    assert result["environments"][0]["id"] == 1
    assert result["environments"][0]["name"] == "dev"
    assert result["environments"][1]["id"] == 2
    assert result["environments"][1]["name"] == "prod"

    mock_list_environments.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_environment_info_module_filter_by_name(module_args, mocker):
    """Test SsbEnvironmentInfoModule filtering by name."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment_info.SsbEnvironmentClient.list_environments",
        return_value=[
            SsbEnvironment(
                id=1,
                name="dev",
                secured_props={
                    "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                        value="localhost:9092",
                        sensitive=False,
                    ),
                },
                project=PROJECT_ID,
            ),
            SsbEnvironment(
                id=2,
                name="prod",
                secured_props={
                    "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                        value="kafka:9092",
                        sensitive=False,
                    ),
                },
                project=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "dev",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["environments"]) == 1
    assert result["environments"][0]["id"] == 1
    assert result["environments"][0]["name"] == "dev"

    mock_list_environments.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_environment_info_module_filter_by_name_not_found(module_args, mocker):
    """Test SsbEnvironmentInfoModule filtering by name when environment doesn't exist."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment_info.SsbEnvironmentClient.list_environments",
        return_value=[
            SsbEnvironment(
                id=1,
                name="dev",
                secured_props={},
                project=PROJECT_ID,
            ),
            SsbEnvironment(
                id=2,
                name="prod",
                secured_props={},
                project=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "nonexistent-environment",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["environments"]) == 0

    mock_list_environments.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_environment_info_module_by_id(module_args, mocker):
    """Test SsbEnvironmentInfoModule retrieval by ID."""
    mock_describe_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment_info.SsbEnvironmentClient.describe_environment",
        return_value=SsbEnvironment(
            id=1,
            name="dev",
            secured_props={
                "kafka.bootstrap.servers": SsbEnvironmentSecuredProperty(
                    value="localhost:9092",
                    sensitive=False,
                ),
                "kafka.password": SsbEnvironmentSecuredProperty(
                    value="secret",
                    sensitive=True,
                ),
            },
            project=PROJECT_ID,
            created_at="2024-06-01T12:00:00Z",
            last_edited_at="2024-06-02T14:00:00Z",
            last_editor="testuser",
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
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["environments"]) == 1
    assert result["environments"][0]["id"] == 1
    assert result["environments"][0]["name"] == "dev"
    assert "secured_props" in result["environments"][0]
    assert "kafka.bootstrap.servers" in result["environments"][0]["secured_props"]
    assert "kafka.password" in result["environments"][0]["secured_props"]

    mock_describe_environment.assert_called_once_with(
        project_id=PROJECT_ID,
        environment_id=1,
    )


def test_ssb_environment_info_module_by_id_not_found(module_args, mocker):
    """Test SsbEnvironmentInfoModule retrieval by ID when environment doesn't exist."""
    mock_describe_environment = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment_info.SsbEnvironmentClient.describe_environment",
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
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["environments"]) == 0

    mock_describe_environment.assert_called_once_with(
        project_id=PROJECT_ID,
        environment_id=999,
    )


def test_ssb_environment_info_module_with_sensitive_properties(module_args, mocker):
    """Test SsbEnvironmentInfoModule with sensitive properties."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment_info.SsbEnvironmentClient.list_environments",
        return_value=[
            SsbEnvironment(
                id=1,
                name="secure-env",
                secured_props={
                    "api.key": SsbEnvironmentSecuredProperty(
                        value="secret-key",
                        sensitive=True,
                    ),
                    "api.endpoint": SsbEnvironmentSecuredProperty(
                        value="https://api.example.com",
                        sensitive=False,
                    ),
                },
                project=PROJECT_ID,
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
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["environments"]) == 1
    env = result["environments"][0]
    assert env["secured_props"]["api.key"]["sensitive"] is True
    assert env["secured_props"]["api.key"]["value"] == "secret-key"
    assert env["secured_props"]["api.endpoint"]["sensitive"] is False

    mock_list_environments.assert_called_once_with(project_id=PROJECT_ID)


def test_ssb_environment_info_module_check_mode(module_args, mocker):
    """Test SsbEnvironmentInfoModule in check mode."""
    mock_list_environments = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_environment_info.SsbEnvironmentClient.list_environments",
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
        ssb_environment_info.main()

    result = e.value
    assert result["changed"] is False
    assert "environments" in result

    mock_list_environments.assert_called_once_with(project_id=PROJECT_ID)

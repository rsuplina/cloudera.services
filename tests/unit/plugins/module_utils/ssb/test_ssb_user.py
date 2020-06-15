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

from ansible_collections.cloudera.services.tests.unit import AnsibleFailJson

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesClient,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUser,
    SsbUserClient,
)

ENDPOINT_URL = "https://cloudera.internal"

USER = SsbUser(
    id="user123",
    username="jdoe",
    first_name="John",
    last_name="Doe",
    is_active=True,
    primary_project_id="proj1",
    project_id="proj1",
    keytab="keytabdata",
    keytab_principal="user_principal",
    keytab_last_modified="2024-06-01T12:00:00Z",
    granted_authorities=["authority1", "authority2"],
)


def test_get_current_user(mocker):
    """Test retrieving the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.get.return_value = USER

    # Create the SSBUserClient instance
    client = SsbUserClient(api_client=api_client)

    response: SsbUser = client.get_current_user()

    assert response == USER

    # Verify that the get method was called with correct parameters
    api_client.get.assert_called_once_with(
        "/api/v2/user",
    )


def test_set_current_user_project(mocker):
    """Test setting the active project for the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.patch.return_value = USER

    # Create the SSBUserClient instance
    client = SsbUserClient(api_client=api_client)

    response = client.set_current_user_project("proj1")

    assert response == USER

    # Verify that the patch method was called with correct parameters
    api_client.patch.assert_called_once_with(
        "/api/v2/user/project",
        data={"project_id": "proj1"},
    )


def test_set_current_user_password(mocker):
    """Test setting the password for the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.patch.return_value = USER

    # Create the SSBUserClient instance
    client = SsbUserClient(api_client=api_client)

    response = client.set_current_user_password(
        current_password="CURRENT",
        new_password="NEW",
    )
    assert response == USER

    # Verify that the patch method was called with correct parameters
    api_client.patch.assert_called_once_with(
        "/api/v2/user/password",
        data={"current_password": "CURRENT", "new_password": "NEW"},
    )

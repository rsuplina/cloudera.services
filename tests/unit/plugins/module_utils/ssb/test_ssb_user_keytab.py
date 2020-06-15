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

import pytest

__metaclass__ = type

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ServicesClient,
)
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUserKeytab,
    SsbUserKeytabClient,
)

ENDPOINT_URL = "https://cloudera.internal"

USER = dict(
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


def test_generate_keytab(mocker):
    """Test generating a keytab for the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = None

    # Create the SSBUserKeytabClient instance
    client = SsbUserKeytabClient(api_client=api_client)

    response = client.generate_keytab("principal", "password")

    assert isinstance(response, SsbUserKeytab)
    assert response.principal == "principal"

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/user/keytab/generate",
        data={
            "principal": "principal",
            "password": "password",
        },
        squelch={
            200: None,
            400: {},
        },
    )


def test_upload_keytab_file(mocker):
    """Test uploading a keytab file for the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = None

    # Create the SSBUserKeytabClient instance
    client = SsbUserKeytabClient(api_client=api_client)

    response = client.upload_keytab(
        principal="principal",
        keytab_file="keytabfile.keytab",
    )

    assert isinstance(response, SsbUserKeytab)
    assert response.principal == "principal"

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/user/keytab/upload",
        data={
            "principal": "principal",
            "file": {
                "filename": "keytabfile.keytab",
            },
        },
        format="multipart",
        squelch={
            200: None,
            400: {},
        },
    )


def test_upload_keytab_data(mocker):
    """Test uploading a keytab data for the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = None

    # Create the SSBUserKeytabClient instance
    client = SsbUserKeytabClient(api_client=api_client)

    response = client.upload_keytab(
        principal="principal",
        keytab_data=b"keytabdata",
    )

    assert isinstance(response, SsbUserKeytab)
    assert response.principal == "principal"

    # Verify that the post method was called with correct parameters
    api_client.post.assert_called_once_with(
        "/api/v2/user/keytab/upload",
        data={
            "principal": "principal",
            "file": {
                "content": b"keytabdata",
            },
        },
        format="multipart",
        squelch={
            200: None,
            400: {},
        },
    )


def test_upload_keytab_invalid_parameters(mocker):
    """Test invalid keytab parameters when uploading for the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.post.return_value = None

    # Create the SSBUserKeytabClient instance
    client = SsbUserKeytabClient(api_client=api_client)

    with pytest.raises(ValueError) as excinfo:
        client.upload_keytab(
            principal="principal",
            keytab_data=b"keytabdata",
            keytab_file="keytabfile.keytab",
        )


def test_delete_keytab(mocker):
    """Test generating a keytab for the current user."""

    # Mock the ServicesClient instance
    api_client = mocker.create_autospec(ServicesClient, instance=True)
    api_client.delete.return_value = {}

    # Create the SSBUserClient instance
    client = SsbUserKeytabClient(api_client=api_client)

    response = client.delete_keytab()

    assert response == None

    # Verify that the post method was called with correct parameters
    api_client.delete.assert_called_once_with(
        "/api/v2/user/keytab",
    )

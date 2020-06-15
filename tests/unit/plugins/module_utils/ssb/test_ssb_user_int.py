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

from ansible_collections.cloudera.services.plugins.module_utils.ssb import SsbUser

REQUIRED_ENV_VARS = [
    "SSB_SSE_API_URL",
    "SSB_SSE_API_USERNAME",
    "SSB_SSE_API_PASSWORD",
]


def test_get_current_user(user_client):
    """Test retrieving the current user."""
    response = user_client.get_current_user()

    assert isinstance(response, SsbUser)


def test_set_current_user_project(user_client, existing_project):
    """Test setting the active project for the current user."""
    response = user_client.set_current_user_project(existing_project.id)

    assert isinstance(response, SsbUser)
    assert response.project_id == existing_project.id


@pytest.mark.skip(reason="Needs a user factory to create a test user.")
def test_set_current_user_password(user_client):
    """Test setting the password for the current user."""
    response = user_client.set_current_user_password(
        current_password="CURRENT",
        new_password="NEW",
    )

    assert response

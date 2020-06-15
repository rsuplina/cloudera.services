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

from ansible_collections.cloudera.services.plugins.modules import ssb_user_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUser,
)

BASE_URL = "https://api.cloudera.internal"


def test_ssb_user_info_module_full_user_details(module_args, mocker):
    """Test SsbUserInfoModule with complete user information."""
    mock_get_current_user = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_info.SsbUserClient.get_current_user",
        return_value=SsbUser(
            id="user-123",
            username="fulluser",
            email="fulluser@example.com",
            first_name="Full",
            last_name="User",
            is_active=True,
            primary_project_id="primary-project-123",
            project_id="current-project-456",
            keytab="YmFzZTY0ZW5jb2RlZGtleXRhYg==",
            keytab_principal="fulluser@EXAMPLE.COM",
            keytab_last_modified="2026-02-06T12:00:00Z",
            granted_authorities=["ROLE_USER", "ROLE_DEVELOPER"],
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_info.main()

    result = e.value
    assert result["changed"] is False
    assert result["user"]["id"] == "user-123"
    assert result["user"]["username"] == "fulluser"
    assert result["user"]["email"] == "fulluser@example.com"
    assert result["user"]["first_name"] == "Full"
    assert result["user"]["last_name"] == "User"
    assert result["user"]["is_active"] is True
    assert result["user"]["primary_project_id"] == "primary-project-123"
    assert result["user"]["project_id"] == "current-project-456"
    assert result["user"]["keytab"] == "YmFzZTY0ZW5jb2RlZGtleXRhYg=="
    assert result["user"]["keytab_principal"] == "fulluser@EXAMPLE.COM"
    assert result["user"]["keytab_last_modified"] == "2026-02-06T12:00:00Z"
    assert len(result["user"]["granted_authorities"]) == 2

    mock_get_current_user.assert_called_once()

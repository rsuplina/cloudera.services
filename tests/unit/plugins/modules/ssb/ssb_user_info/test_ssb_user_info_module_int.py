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

from ansible_collections.cloudera.services.plugins.modules import ssb_user_info

REQUIRED_ENV_VARS = [
    "SSB_SSE_API_URL",
    "SSB_SSE_API_USERNAME",
    "SSB_SSE_API_PASSWORD",
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


def test_ssb_user_info_module_get_current_user(ssb_module_args):
    """Test SsbUserInfoModule get current authenticated user information."""

    ssb_module_args({})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_info.main()

    result = e.value
    assert result["changed"] is False
    assert "user" in result
    assert isinstance(result["user"], dict)
    assert "id" in result["user"]
    assert "username" in result["user"]
    # The username should match the authenticated user
    assert result["user"]["username"] is not None


def test_ssb_user_info_module_check_mode(ssb_module_args):
    """Test SsbUserInfoModule in check mode."""

    ssb_module_args({"_ansible_check_mode": True})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_info.main()

    result = e.value
    assert result["changed"] is False
    assert "user" in result
    assert isinstance(result["user"], dict)
    assert "id" in result["user"]
    assert "username" in result["user"]

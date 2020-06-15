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

from base64 import standard_b64encode
from typing import Callable

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_user_keytab

REQUIRED_ENV_VARS = [
    "SSB_SSE_API_URL",
    "SSB_SSE_API_USERNAME",
    "SSB_SSE_API_PASSWORD",
    "SSB_SSE_API_KEYTAB_FILE",
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


def test_ssb_user_keytab_module_present_password(env_context, ssb_module_args):
    """Test SsbUserKeytabModule present state with password."""

    ssb_module_args(
        {
            "state": "present",
            "principal": env_context["SSB_SSE_API_USERNAME"],
            "keytab_password": env_context["SSB_SSE_API_PASSWORD"],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_keytab.main()

    result = e.value
    assert result["changed"] is True
    assert result["principal"] == env_context["SSB_SSE_API_USERNAME"]


def test_ssb_user_keytab_module_present_file(env_context, ssb_module_args):
    """Test SsbUserKeytabModule present state with file."""

    ssb_module_args(
        {
            "state": "present",
            "principal": env_context["SSB_SSE_API_USERNAME"],
            "keytab_file": env_context["SSB_SSE_API_KEYTAB_FILE"],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_keytab.main()

    result = e.value
    assert result["changed"] is True
    assert result["principal"] == env_context["SSB_SSE_API_USERNAME"]


def test_ssb_user_keytab_module_present_base64(env_context, ssb_module_args):
    """Test SsbUserKeytabModule present state with data."""

    keytab_data = open(env_context["SSB_SSE_API_KEYTAB_FILE"], "rb").read()

    ssb_module_args(
        {
            "state": "present",
            "principal": env_context["SSB_SSE_API_USERNAME"],
            "keytab_base64": standard_b64encode(keytab_data).decode("utf-8"),
            "debug": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_keytab.main()

    result = e.value
    assert result["changed"] is True
    assert result["principal"] == env_context["SSB_SSE_API_USERNAME"]

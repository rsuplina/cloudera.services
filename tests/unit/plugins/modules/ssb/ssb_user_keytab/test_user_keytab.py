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

import base64
import pytest

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_user_keytab

BASE_URL = "https://api.cloudera.internal"


def test_ssb_user_keytab_module_missing_principal(module_args):
    """Test SsbUserKeytabModule initialization with no principal."""

    module_args(
        {
            "endpoint": BASE_URL,
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="state is present but all of the following are missing: principal",
    ):
        ssb_user_keytab.main()


def test_ssb_user_keytab_module_missing_exclusives(module_args):
    """Test SsbUserKeytabModule initialization with missing exclusive parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "principal": "user_principal",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="state is present but any of the following are missing: keytab_file, keytab_base64, keytab_password",
    ):
        ssb_user_keytab.main()


def test_ssb_user_keytab_module_multiple_exclusives(module_args):
    """Test SsbUserKeytabModule initialization with multiple exclusive parameters."""

    module_args(
        {
            "endpoint": BASE_URL,
            "principal": "user_principal",
            "keytab_file": "/path/to/keytab",
            "keytab_password": "password",
        },
    )

    with pytest.raises(
        AnsibleFailJson,
        match="parameters are mutually exclusive: keytab_password|keytab_file|keytab_base64",
    ):
        ssb_user_keytab.main()


def test_ssb_user_keytab_module_present_password(module_args, mocker):
    """Test SsbUserKeytabModule deletion."""
    mock_delete_keytab = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_keytab.SsbUserKeytabClient.delete_keytab",
        return_value=None,
    )
    mock_generate_keytab = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_keytab.SsbUserKeytabClient.generate_keytab",
        return_value=ssb_user_keytab.SsbUserKeytab(
            principal="user_principal",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "state": "present",
            "principal": "user_principal",
            "keytab_password": "password",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_keytab.main()

    result = e.value
    assert result["changed"] is True
    assert result["principal"] == "user_principal"

    mock_delete_keytab.assert_called_once()
    mock_delete_keytab.assert_called_with()

    mock_generate_keytab.assert_called_once()
    mock_generate_keytab.assert_called_with(
        principal="user_principal",
        password="password",
    )


def test_ssb_user_keytab_module_present_file(module_args, mocker):
    """Test SsbUserKeytabModule deletion."""
    mock_delete_keytab = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_keytab.SsbUserKeytabClient.delete_keytab",
        return_value=None,
    )
    mock_upload_keytab = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_keytab.SsbUserKeytabClient.upload_keytab",
        return_value=ssb_user_keytab.SsbUserKeytab(
            principal="user_principal",
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "state": "present",
            "principal": "user_principal",
            "keytab_file": "/path/to/user.keytab",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_keytab.main()

    result = e.value
    assert result["changed"] is True
    assert result["principal"] == "user_principal"

    mock_delete_keytab.assert_called_once()
    mock_delete_keytab.assert_called_with()

    mock_upload_keytab.assert_called_once()
    mock_upload_keytab.assert_called_with(
        principal="user_principal",
        keytab_file="/path/to/user.keytab",
    )


def test_ssb_user_keytab_module_present_base64(module_args, mocker):
    """Test SsbUserKeytabModule deletion."""
    mock_delete_keytab = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_keytab.SsbUserKeytabClient.delete_keytab",
        return_value=None,
    )
    mock_upload_keytab = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_keytab.SsbUserKeytabClient.upload_keytab",
        return_value=ssb_user_keytab.SsbUserKeytab(
            principal="user_principal",
        ),
    )

    data_bytes = b"dummy keytab data"

    module_args(
        {
            "endpoint": BASE_URL,
            "state": "present",
            "principal": "user_principal",
            "keytab_base64": base64.standard_b64encode(data_bytes).decode("utf-8"),
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_keytab.main()

    result = e.value
    assert result["changed"] is True
    assert result["principal"] == "user_principal"

    mock_delete_keytab.assert_called_once()
    mock_delete_keytab.assert_called_with()

    mock_upload_keytab.assert_called_once()
    mock_upload_keytab.assert_called_with(
        principal="user_principal",
        keytab_data=data_bytes,
    )


def test_ssb_user_keytab_module_absent(module_args, mocker):
    """Test SsbUserKeytabModule deletion."""
    mock_delete_keytab = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_user_keytab.SsbUserKeytabClient.delete_keytab",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_user_keytab.main()

    result = e.value
    assert result["changed"] is True
    assert result["principal"] == ""

    mock_delete_keytab.assert_called_once()
    mock_delete_keytab.assert_called_with()

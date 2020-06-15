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

from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbUserKeytab,
)

REQUIRED_ENV_VARS = [
    "SSB_SSE_API_URL",
    "SSB_SSE_API_USERNAME",
    "SSB_SSE_API_PASSWORD",
    "SSB_SSE_API_KEYTAB_FILE",
]


def test_generate_keytab(user_keytab_client, env_context, clear_keytab):
    """Test generating a keytab for the current user."""
    response = user_keytab_client.generate_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        password=env_context["SSB_SSE_API_PASSWORD"],
    )
    assert isinstance(response, SsbUserKeytab)  # HTTP 204 (emulated)

    # Verify that the keytab exists now
    generate = user_keytab_client.generate_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        password=env_context["SSB_SSE_API_PASSWORD"],
    )
    assert isinstance(generate, SsbUserKeytab)

    upload = user_keytab_client.upload_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        keytab_file=env_context["SSB_SSE_API_KEYTAB_FILE"],
    )
    assert isinstance(upload, SsbUserKeytab)


def test_upload_keytab_file(user_keytab_client, env_context, clear_keytab):
    """Test uploading a keytab file for the current user."""
    response = user_keytab_client.upload_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        keytab_file=env_context["SSB_SSE_API_KEYTAB_FILE"],
    )
    assert isinstance(response, SsbUserKeytab)  # HTTP 204 (emulated)

    # Verify that the keytab exists now
    generate = user_keytab_client.generate_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        password=env_context["SSB_SSE_API_PASSWORD"],
    )
    assert isinstance(generate, SsbUserKeytab)  # HTTP 200

    upload = user_keytab_client.upload_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        keytab_file=env_context["SSB_SSE_API_KEYTAB_FILE"],
    )
    assert isinstance(upload, SsbUserKeytab)  # HTTP 200


def test_upload_keytab_data_bytes(user_keytab_client, env_context, clear_keytab):
    """Test uploading a keytab data for the current user."""
    response = user_keytab_client.upload_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        keytab_data=open(env_context["SSB_SSE_API_KEYTAB_FILE"], "rb").read(),
    )
    assert isinstance(response, SsbUserKeytab)  # HTTP 204 (emulated)

    # Verify that the keytab exists now
    generate = user_keytab_client.generate_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        password=env_context["SSB_SSE_API_PASSWORD"],
    )
    assert isinstance(generate, SsbUserKeytab)  # HTTP 200

    upload = user_keytab_client.upload_keytab(
        principal=env_context["SSB_SSE_API_USERNAME"],
        keytab_file=env_context["SSB_SSE_API_KEYTAB_FILE"],
    )
    assert isinstance(upload, SsbUserKeytab)  # HTTP 200


def test_delete_keytab(user_keytab_client, set_keytab):
    """Test deleting a keytab for the current user."""
    response = user_keytab_client.delete_keytab()
    assert response == None

    # Verify that the keytab no longer exists
    verify = user_keytab_client.delete_keytab()
    assert verify == None

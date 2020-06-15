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

import json
import pytest
import re

from ansible_collections.cloudera.services.tests.unit import AnsibleFailJson

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    AnsibleServicesClient,
)

ENDPOINT_URL = "https://cloudera.internal"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


@pytest.fixture
def mock_ansible_module(mocker):
    """Fixture to create a mock Ansible module."""
    mock_module = mocker.Mock()
    mock_module.params = {
        "url": ENDPOINT_URL,
        "timeout": 60,
        "page_size": 100,
        "debug": False,
    }
    return mock_module


def test_services_client_init(mock_ansible_module):
    """Test default initialization."""

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    assert client.endpoint_url == ENDPOINT_URL
    assert client.timeout == 60
    assert client.default_page_size == 100


def test_services_client_init_proxy(mock_ansible_module):
    """Test listing compute usage records."""

    client = AnsibleServicesClient(
        module=mock_ansible_module,
        proxy_context_path="/proxy/path",
    )

    assert client.endpoint_url == ENDPOINT_URL
    assert client.timeout == 60
    assert client.proxy_context_path == "/proxy/path"


def test_make_request_http_200(mock_ansible_module, mocker):
    """Test processing 200 OK responses."""

    # Set up the mock response data
    test_data = {"success": True}
    mock_resp = mocker.Mock()
    mock_resp.read.return_value = json.dumps(test_data).encode("utf-8")

    # Mock the request function to return the test data (200 OK)
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    response = client._make_request("GET", "/test/path")

    assert "success" in response
    assert response["success"] is True

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_http_204(mock_ansible_module, mocker):
    """Test processing 204 No Content responses."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b""

    # Mock the request function to return 204 No Content
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 204})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    response = client._make_request("DELETE", "/test/path")

    assert response is None

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="DELETE",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_http_401(mock_ansible_module, mocker):
    """Test processing 401 Unauthorized responses."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = (
        b'{"errorMessage": "Unauthorized", "errorCode": "401"}'
    )

    # Mock the request function to return 401 Unauthorized
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 401})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    client._make_request("GET", "/test/path")

    mock_ansible_module.fail_json.assert_called_once_with(
        msg=f"[401] Unauthorized Access; {ENDPOINT_URL}/test/path",
    )

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_http_403(mock_ansible_module, mocker):
    """Test processing 403 Forbidden responses."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b'{"errorMessage": "Forbidden", "errorCode": "403"}'

    # Mock the request function to return 403 Forbidden
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 403})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    client._make_request("GET", "/test/path")

    mock_ansible_module.fail_json.assert_called_once_with(
        msg=f"[403] Forbidden Access; {ENDPOINT_URL}/test/path",
    )

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_http_404(mock_ansible_module, mocker):
    """Test processing 404 Not Found responses."""

    mock_resp = mocker.Mock()

    # Mock the request function to return 404 Not Found
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (
        mock_resp,
        {
            "status": 404,
            "body": '{"error": "Not Found", "errorCode": "404"}',
            "msg": "Not Found",
        },
    )

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    client._make_request("GET", "/test/path")

    mock_ansible_module.fail_json.assert_called_once_with(
        msg=f"[404] Not Found; {ENDPOINT_URL}/test/path",
    )

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_http_500_with_retry(mock_ansible_module, mocker):
    """Test processing 500 Internal Server Error with retry logic."""

    mock_resp = mocker.Mock()

    # Mock the request function to return 500 Internal Server Error
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (
        mock_resp,
        {"status": 500, "msg": "Internal Server Error"},
    )

    # Mock time.sleep to speed up tests
    mock_sleep = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.time.sleep",
    )

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    client._make_request("GET", "/test/path", max_retries=2)

    mock_ansible_module.fail_json.assert_called_once_with(
        msg=f"[500] Internal Server Error; {ENDPOINT_URL}/test/path",
    )

    # Should retry once (2 total attempts)
    assert mock_fetch_url.call_count == 2
    assert mock_sleep.call_count == 1

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_http_429_with_retry(mock_ansible_module, mocker):
    """Test processing 429 Too Many Requests with retry logic."""

    mock_resp = mocker.Mock()

    # Mock the request function to return 429 Too Many Requests
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (
        mock_resp,
        {"status": 429, "msg": "Too Many Requests"},
    )

    # Mock time.sleep to speed up tests
    mock_sleep = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.time.sleep",
    )

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    client._make_request("GET", "/test/path", max_retries=3)

    mock_ansible_module.fail_json.assert_called_once_with(
        msg=f"[429] Too Many Requests; {ENDPOINT_URL}/test/path",
    )

    # Should retry 2 times (3 total attempts)
    assert mock_fetch_url.call_count == 3
    assert mock_sleep.call_count == 2

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_connection_error_with_retry(mock_ansible_module, mocker):
    """Test processing connection errors with retry logic."""

    # Mock the request function to raise a connection error
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.side_effect = Exception("Connection refused")

    # Mock time.sleep to speed up tests
    mock_sleep = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.time.sleep",
    )

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    client._make_request("GET", "/test/path", max_retries=2)

    mock_ansible_module.fail_json.assert_called_once_with(
        msg=f"Connection refused, request failed after 2 attempts; {ENDPOINT_URL}/test/path",
    )

    # Should retry once (2 total attempts)
    assert mock_fetch_url.call_count == 2
    assert mock_sleep.call_count == 1

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_empty_response(mock_ansible_module, mocker):
    """Test processing 200 OK responses with empty body."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b""

    # Mock the request function to return empty response (200 OK)
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    response = client._make_request("GET", "/test/path")

    assert response == {}

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_json_decode_error(mock_ansible_module, mocker):
    """Test processing responses with invalid JSON."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b"invalid json {"

    # Mock the request function to return invalid JSON (200 OK)
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    response = client._make_request("GET", "/test/path")

    assert "response" in response
    assert response["response"] == "invalid json {"

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="GET",
        headers=DEFAULT_HEADERS,
        data=None,
        timeout=client.timeout,
    )


def test_make_request_form_data_json(mock_ansible_module, mocker):
    """Test sending JSON form data in requests."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b'{"result": "ok"}'

    # Mock the request function to return 200 OK
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    form_data = {"field1": "value1", "field2": "value2"}
    response = client._make_request(
        "POST",
        "/test/path",
        data=form_data,
    )  # format defaults to 'json'

    assert "result" in response
    assert response["result"] == "ok"

    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="POST",
        headers=DEFAULT_HEADERS | {"Content-Length": str(len(json.dumps(form_data)))},
        data=bytes(json.dumps(form_data), "utf-8"),
        timeout=client.timeout,
    )


def test_make_request_form_data_urlencoded(mock_ansible_module, mocker):
    """Test sending URL-encoded form data in requests."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b'{"result": "ok"}'

    # Mock the request function to return 200 OK
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    form_data = {"field1": "value1", "field2": "value2"}
    response = client._make_request(
        "POST",
        "/test/path",
        data=form_data,
        format="urlencoded",
    )

    assert "result" in response
    assert response["result"] == "ok"

    expected_form_encoded = "field1=value1&field2=value2"
    mock_fetch_url.assert_called_with(
        mock_ansible_module,
        f"{ENDPOINT_URL}/test/path",
        method="POST",
        headers=DEFAULT_HEADERS
        | {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(expected_form_encoded)),
        },
        data=bytes(expected_form_encoded, "utf-8"),
        timeout=client.timeout,
    )


def test_make_request_form_data_multipart(mock_ansible_module, mocker):
    """Test sending multipart form data in requests."""

    mock_resp = mocker.Mock()
    mock_resp.read.return_value = b'{"result": "ok"}'

    # Mock the request function to return 200 OK
    mock_fetch_url = mocker.patch(
        "ansible_collections.cloudera.services.plugins.module_utils.common.fetch_url",
    )
    mock_fetch_url.return_value = (mock_resp, {"status": 200})

    client = AnsibleServicesClient(
        module=mock_ansible_module,
    )

    form_data = {"field1": "value1", "field2": "value2"}
    response = client._make_request(
        "POST",
        "/test/path",
        data=form_data,
        format="multipart",
    )

    assert "result" in response
    assert response["result"] == "ok"

    # Check the call was made
    mock_fetch_url.assert_called_once()

    # Get the actual call arguments
    call_args = mock_fetch_url.call_args

    # Verify non-data parameters
    assert call_args[0][0] == mock_ansible_module  # module
    assert call_args[0][1] == f"{ENDPOINT_URL}/test/path"  # url
    assert call_args[1]["method"] == "POST"
    assert call_args[1]["timeout"] == client.timeout

    # Verify headers contain multipart content type
    headers = call_args[1]["headers"]
    assert "Content-Type" in headers
    assert re.match(r"multipart/form-data.*", headers["Content-Type"])

    # Verify data contains both fields (handle multipart format with boundaries)
    data_str = call_args[1]["data"].decode("utf-8")
    assert re.search(r'name="field1".*?value1', data_str, re.DOTALL)
    assert re.search(r'name="field2".*?value2', data_str, re.DOTALL)

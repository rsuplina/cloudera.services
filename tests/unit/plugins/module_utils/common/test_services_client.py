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

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    paginated,
    ServicesError,
    format_query_params,
    prepare_urlencoded,
    format_body,
)

TEST_URL = "http://example.com/api/v1"


def test_services_error():
    err = ServicesError("Test error")
    assert str(err) == "Test error"
    assert err.status is None


def test_services_error_404():
    err = ServicesError("Test error", status=404)
    assert str(err) == "[404] Test error"
    assert err.status == 404


def test_format_query_params():
    params = {
        "param1": "value1",
        "param2": None,
        "param3": 123,
    }
    result = format_query_params(TEST_URL, params)
    assert result == "http://example.com/api/v1?param1=value1&param2=&param3=123"


def test_format_query_params_missing():
    result = format_query_params(TEST_URL)
    assert result == "http://example.com/api/v1"


def test_format_query_params_bare_flag():
    params = {
        "param1": "value1",
        "param2": None,
        "param3": 123,
    }
    result = format_query_params(TEST_URL, params, empty_value=False)
    assert result == "http://example.com/api/v1?param1=value1&param2&param3=123"


def test_format_query_params_nested_lists():
    params = {
        "param1": "value1",
        "param2": [
            "list_value1",
            "",
        ],
        "param3": 123,
    }
    result = format_query_params(TEST_URL, params, empty_value=False)
    assert (
        result
        == "http://example.com/api/v1?param1=value1&param2=list_value1&param2=&param3=123"
    )


def test_format_query_params_multi_nested_lists():
    params = {
        "param1": "value1",
        "param2": [
            "list_value1",
            "",
            ["sublist_value1", ""],
        ],
        "param3": 123,
    }
    result = format_query_params(TEST_URL, params, empty_value=False)
    assert (
        result
        == "http://example.com/api/v1?param1=value1&param2=list_value1&param2=&param2=sublist_value1&param2=&param3=123"
    )


def test_prepare_urlencoded():
    data = {
        "field1": "value1",
        "field2": "value2",
    }
    body = prepare_urlencoded(data)
    assert body == "field1=value1&field2=value2"


def test_prepare_urlencoded_string():
    data = "field1=value1&field2=value2"
    body = prepare_urlencoded(data)
    assert body == "field1=value1&field2=value2"


def test_prepare_urlencoded_nested_list():
    data = {
        "field1": "value1",
        "field2": ["value2", "value3"],
    }
    body = prepare_urlencoded(data)
    assert body == "field1=value1&field2=value2&field2=value3"


def test_prepare_urlencoded_nested_dict():
    data = {
        "field1": "value1",
        "field2": {
            "subfield1": "subvalue1",
            "subfield2": "subvalue2",
        },
    }
    body = prepare_urlencoded(data)
    assert (
        body == "field1=value1&field2=subfield1&field2=subfield2"
    )  # Note: dicts are flattened to keys only


def test_format_body_data_json_dict():
    input = {
        "key1": "value1",
        "key2": 123,
    }
    headers, body = format_body(data=input, headers={})
    assert headers["Content-Type"] == "application/json"
    assert body == bytes(json.dumps(input), "utf-8")


def test_format_body_data_json_str():
    input = json.dumps(
        {
            "key1": "value1",
            "key2": 123,
        },
    )
    headers, body = format_body(data=input, headers={})
    assert headers["Content-Type"] == "application/json"
    assert body == bytes(input, "utf-8")


def test_format_body_data_urlencoded_dict():
    input = {
        "key1": "value1",
        "key2": 123,
    }
    headers, body = format_body(data=input, format="urlencoded", headers={})
    assert headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert body == bytes("key1=value1&key2=123", "utf-8")


def test_format_body_data_urlencoded_str():
    input = "key1=value1&key2=123"
    headers, body = format_body(data=input, format="urlencoded", headers={})
    assert headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert body == bytes("key1=value1&key2=123", "utf-8")


def test_format_body_data_multipart_text_form_field():
    input = {
        "key1": "value1",
        "key2": "value2",
    }
    headers, body = format_body(data=input, format="multipart", headers={})
    assert headers["Content-Type"].startswith("multipart/form-data; boundary=")
    assert b"--" in body  # pyright: ignore[reportOperatorIssue]


@pytest.fixture
def mock_file_lookup(mocker):
    mock_open = mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data=b"mock file content"),
    )
    mock_exists = mocker.patch("os.path.exists", return_value=True)
    return mock_open, mock_exists


def test_format_body_data_multipart_file_octet_stream(mock_file_lookup):
    input = {
        "file1": {
            "filename": "/bin/true",
            "content_type": "application/octet-stream",
        },
    }
    headers, _ = format_body(data=input, format="multipart", headers={})
    assert headers["Content-Type"].startswith("multipart/form-data; boundary=")


def test_format_body_data_multipart_file_text():
    input = {
        "file1": {
            "content": "This is a testorm_d file.",
            "filename": "test.txt",
            "content_type": "text/plain",
        },
    }
    headers, _ = format_body(data=input, format="multipart", headers={})
    assert headers["Content-Type"].startswith("multipart/form-data; boundary=")


def test_format_body_data_multipart_parsing_error():
    input = ["Invalid multipart data"]
    with pytest.raises(ServicesError) as excinfo:
        format_body(data=input, format="multipart", headers={})
    assert "Failed to prepare multipart form data" in str(excinfo.value)

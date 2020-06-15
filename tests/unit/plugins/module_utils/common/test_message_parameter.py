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


"""Test cases for the MessageParameter mixin class."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ParametersMixin,
    MessageParameter,
)


def test_message_parameter_inherits_parameters_mixin():
    """Test that MessageParameter inherits from ParametersMixin."""
    assert issubclass(MessageParameter, ParametersMixin)


def test_message_parameter_get_argument_spec():
    """Test the get_argument_spec method of MessageParameter."""
    spec = MessageParameter.get_argument_spec()

    assert "message" in spec
    assert spec["message"]["required"] is False
    assert spec["message"]["type"] == "str"
    assert spec["message"]["default"] is None


def test_message_parameter_init_parameters(mocker):
    """Test the init_parameters method of MessageParameter."""
    # Create a mock object with get_param method
    mock_get_param = mocker.Mock(return_value="test message")

    # Create MessageParameter instance and add get_param method
    message_param = MessageParameter()

    # Dynamically add the method since MessageParameter itself (the doesn't have get_param()
    setattr(message_param, "get_param", mock_get_param)

    # Call init_parameters
    message_param.init_parameters()

    # Verify the message attribute is set
    assert hasattr(message_param, "message")
    assert message_param.message == "test message"
    mock_get_param.assert_called_once_with("message")


def test_message_parameter_init_parameters_none_value(mocker):
    """Test init_parameters when get_param returns None."""
    mock_get_param = mocker.Mock(return_value=None)

    message_param = MessageParameter()
    setattr(message_param, "get_param", mock_get_param)
    message_param.init_parameters()

    assert message_param.message is None

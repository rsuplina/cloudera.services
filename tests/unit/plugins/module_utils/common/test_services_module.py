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

from ansible_collections.cloudera.services.tests.unit import AnsibleFailJson

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    MessageParameter,
    AutoExecuteMeta,
    ServicesModule,
)

BASE_URL = "https://api.cloudera.internal"


class TestServicesModule:
    """Test cases for the ServicesModule base class."""

    def test_services_module_is_abstract(self):
        """Test that ServicesModule cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ServicesModule()  # pyright: ignore[reportAbstractUsage]

    def test_services_module_abstract_methods(self):
        """Test that ServicesModule has the expected abstract methods."""
        assert hasattr(ServicesModule, "process")
        assert getattr(ServicesModule.process, "__isabstractmethod__", False)

    def test_services_module_uses_auto_execute_meta(self):
        """Test that ServicesModule uses AutoExecuteMeta metaclass."""
        assert ServicesModule.__class__ == AutoExecuteMeta


class ConcreteServicesModule(ServicesModule):
    """Concrete implementation of ServicesModule for testing."""

    def __init__(self, **kwargs):
        self._process_called = False
        super().__init__(**kwargs)

    def process(self):
        """Concrete implementation of abstract process method."""
        self._process_called = True
        self.logger.info("Process method called")


class ConcreteServicesModuleWithMixin(ServicesModule, MessageParameter):
    """Concrete implementation with mixin for testing."""

    def __init__(self, **kwargs):
        self._process_called = False
        super().__init__(**kwargs)

    def process(self):
        """Concrete implementation of abstract process method."""
        self._process_called = True
        self.logger.info("Process method called")


class TestConcreteServicesModule:
    """Test cases for concrete ServicesModule implementations."""

    def test_services_module(self, module_args):
        """Test ServicesModule initialization with endpoint."""

        module_args(
            {
                "endpoint": BASE_URL,
            },
        )

        module = ConcreteServicesModule()

        # Verify initialization
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is False
        assert module.log_capture is None
        assert module.api_client.endpoint_url == BASE_URL

    def test_services_module_missing_endpoint(
        self,
        module_args,
    ):
        """Test missing endpoint in ServicesModule initialization."""

        module_args(
            {},
        )

        with pytest.raises(
            AnsibleFailJson,
            match="missing required arguments: url",
        ):
            ConcreteServicesModule()

    def test_services_module_debug(self, module_args, mocker):
        """Test ServicesModule initialization with debug logging enabled."""

        module_args(
            {
                "endpoint": BASE_URL,
                "debug": True,
            },
        )

        # Mock logging components
        mock_logger = mocker.patch("logging.getLogger")
        mock_string_io = mocker.patch("io.StringIO")
        mock_handler = mocker.patch("logging.StreamHandler")
        mock_formatter = mocker.patch("logging.Formatter")

        module = ConcreteServicesModule()

        # Verify debug logging setup
        assert module.api_client.endpoint_url == BASE_URL
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is True
        assert module.log_capture is not None
        assert mock_logger.call_count == 2
        mock_logger.assert_has_calls([mocker.call("cloudera.services"), mocker.call()])
        mock_string_io.assert_called_once()
        mock_handler.assert_called_once()
        mock_formatter.assert_called_once()

    def test_services_module_get_param(self, module_args):
        """Test the get_param method."""

        module_args(
            {
                "url": BASE_URL,
                "debug": True,
            },
        )

        module = ConcreteServicesModule()

        # Test getting existing parameter
        assert module.get_param("url") == BASE_URL

        # Test getting non-existent parameter with default
        assert module.get_param("nonexistent", "default_val") == "default_val"

        # Test getting non-existent parameter without default
        assert module.get_param("nonexistent") is None

    def test_services_module_with_mixin(self, module_args):
        """Test ServicesModule with a parameter mixin."""

        # Add message parameter to mock params
        module_args(
            {
                "endpoint": BASE_URL,
                "message": "test message",
            },
        )

        module = ConcreteServicesModuleWithMixin()

        # Verify mixin parameters were initialized
        assert module.api_client.endpoint_url == BASE_URL
        assert module.message == "test message"
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is False
        assert module.log_capture is None

    def test_services_module_execute_method(self, module_args):
        """Test the execute method."""

        module_args(
            {
                "endpoint": BASE_URL,
            },
        )

        module = ConcreteServicesModule()

        # Verify process was called
        assert module._process_called is True
        assert module.api_client.endpoint_url == BASE_URL
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is False
        assert module.log_capture is None

    def test_services_module_execute_debug(
        self,
        module_args,
        mocker,
    ):
        """Test execute method captures logging output when debug is enabled."""

        module_args(
            {
                "endpoint": BASE_URL,
                "debug": True,
            },
        )

        # Mock StringIO to simulate log output
        mock_string_io_instance = mocker.Mock()
        mock_string_io_instance.getvalue.return_value = "Test log output\nSecond line"
        mocker.patch(
            "io.StringIO",
            return_value=mock_string_io_instance,
        )

        module = ConcreteServicesModule()

        # Verify logging output was captured
        assert module.api_client.endpoint_url == BASE_URL
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is True
        assert module.log_capture is not None
        assert module.log_out == "Test log output\nSecond line"
        assert module.log_lines == ["Test log output", "Second line"]
        mock_string_io_instance.getvalue.assert_called_once()

    def test_services_module_execute_with_empty_log_capture(
        self,
        module_args,
        mocker,
    ):
        """Test execute method handles empty log capture correctly."""

        module_args(
            {
                "endpoint": BASE_URL,
                "debug": True,
            },
        )

        # Mock StringIO to return empty string
        mock_string_io_instance = mocker.Mock()
        mock_string_io_instance.getvalue.return_value = ""
        mocker.patch("io.StringIO", return_value=mock_string_io_instance)

        module = ConcreteServicesModule()

        # Verify empty logging output is handled
        assert module.api_client.endpoint_url == BASE_URL
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is True
        assert module.log_capture is not None
        assert module.log_out == ""
        assert module.log_lines == []

    def test_services_module_argument_spec_merging(self, module_args):
        """Test that argument specs are properly merged."""

        module_args(
            {
                "endpoint": BASE_URL,
                "custom_param": "custom_value",
            },
        )

        custom_spec = dict(custom_param=dict(required=True, type="str"))

        module = ConcreteServicesModule(argument_spec=custom_spec)

        # Verify that custom parameter is set
        assert module.get_param("custom_param") == "custom_value"
        assert module.api_client.endpoint_url == BASE_URL
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is False
        assert module.log_capture is None

    def test_services_module_auto_execute_integration(self, module_args):
        """Test that AutoExecuteMeta calls execute automatically during instantiation."""

        module_args(
            {
                "endpoint": BASE_URL,
            },
        )

        # This will create the instance with auto-execute
        module = ConcreteServicesModule()

        # Verify that process was called via auto-execute
        assert module._process_called is True
        assert module.api_client.endpoint_url == BASE_URL
        assert module.timeout == 60
        assert module.page_size == 100
        assert module.debug_log is False
        assert module.log_capture is None

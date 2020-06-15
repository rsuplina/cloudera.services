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

"""Test cases for the AutoExecuteMeta metaclass."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    AutoExecuteMeta,
)


def test_auto_execute_meta_calls_execute():
    """Test that AutoExecuteMeta automatically calls execute() method."""

    class TestClass(metaclass=AutoExecuteMeta):
        def __init__(self):
            self.initialized = True
            self.execute_called = False

        def execute(self):
            self.execute_called = True

    # Create instance - execute should be called automatically
    instance = TestClass()

    assert instance.initialized is True
    assert instance.execute_called is True


def test_auto_execute_meta_no_execute_method():
    """Test that AutoExecuteMeta doesn't fail when no execute method exists."""

    class TestClass(metaclass=AutoExecuteMeta):
        def __init__(self):
            self.initialized = True

    # Should not raise an exception
    instance = TestClass()
    assert instance.initialized is True


def test_auto_execute_meta_execute_not_callable():
    """Test that AutoExecuteMeta handles non-callable execute attribute."""

    class TestClass(metaclass=AutoExecuteMeta):
        def __init__(self):
            self.initialized = True
            self.execute = "not callable"

    # Should not raise an exception
    instance = TestClass()
    assert instance.initialized is True
    assert instance.execute == "not callable"

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

"""Test cases for the ParametersMixin abstract base class."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from typing import Any, Dict

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    ParametersMixin,
)


def test_parameters_mixin_is_abstract():
    """Test that ParametersMixin cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        ParametersMixin()  # pyright: ignore[reportAbstractUsage]


def test_parameters_mixin_abstract_methods():
    """Test that ParametersMixin has the expected abstract methods."""
    assert hasattr(ParametersMixin, "get_argument_spec")
    assert hasattr(ParametersMixin, "init_parameters")

    # Check that methods are abstract
    assert getattr(ParametersMixin.get_argument_spec, "__isabstractmethod__", False)
    assert getattr(ParametersMixin.init_parameters, "__isabstractmethod__", False)


def test_concrete_mixin_implementation():
    """Test that a concrete implementation of ParametersMixin works correctly."""

    class TestMixin(ParametersMixin):
        @staticmethod
        def get_argument_spec() -> Dict[str, Dict[str, Any]]:
            return {
                "test_param": dict(
                    required=False,
                    type="str",
                    default="test_value",
                ),
            }

        def init_parameters(self) -> None:
            self.test_param = "initialized"

    # Should be able to instantiate concrete implementation
    mixin = TestMixin()
    assert mixin is not None

    # Test the methods
    spec = mixin.get_argument_spec()
    assert "test_param" in spec
    assert spec["test_param"]["default"] == "test_value"

    mixin.init_parameters()
    assert mixin.test_param == "initialized"

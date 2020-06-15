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
from unittest.mock import call

__metaclass__ = type

import unittest

from ansible_collections.cloudera.services.plugins.module_utils.ml import difference
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
)


class TestMLValidateID(ModuleTestCase):
    def test_scalar(self):
        assert difference("foo", "foo") == None
        assert difference("foo", "bar") == "foo"
        assert difference("foo", 1234) == "foo"
        assert difference(["foo"], "foo") == ["foo"]
        assert difference({"foo": "bar"}, "bar") == {"foo": "bar"}

    def test_list(self):
        assert difference(["foo", "bar"], ["foo", "bar"]) == None
        assert difference(["foo", "bar"], ["foo", "gaz"]) == ["foo", "bar"]
        assert difference(["foo", 1234], ["foo", "gaz"]) == ["foo", 1234]
        assert difference(["foo", "bar", "dur"], ["foo", "bar"]) == [
            "foo",
            "bar",
            "dur",
        ]
        assert difference(["foo", "bar"], ["foo", "bar", "gaz"]) == ["foo", "bar"]
        assert difference([["foo"], "bar"], ["foo", "bar"]) == [["foo"], "bar"]
        assert difference(["foo", "bar"], [["foo"], "bar"]) == ["foo", "bar"]
        assert difference([{"foo": "gaz"}, "bar"], ["foo", "bar"]) == [
            {"foo": "gaz"},
            "bar",
        ]
        assert difference(["foo", "bar"], [{"foo": "gaz"}, "bar"]) == ["foo", "bar"]

    def test_dict(self):
        assert difference({"foo": "bar"}, {"foo": "bar"}) == None
        assert difference({"foo": "bar"}, {"foo": "gaz"}) == {"foo": "bar"}
        assert difference({"foo": ["bar"]}, {"foo": "bar"}) == {"foo": ["bar"]}
        assert difference({"foo": "bar"}, {"foo": ["gaz"]}) == {"foo": "bar"}
        assert difference({"foo": {"bar": "gaz"}}, {"foo": "bar"}) == {
            "foo": {"bar": "gaz"},
        }
        assert difference({"foo": "bar"}, {"foo": {"gaz": "dur"}}) == {"foo": "bar"}

    def test_full_nested(self):
        source = {
            "one": "two",
            "three": {
                "four": "five",
                "six": ["seven"],
            },
        }
        target = {
            "one": "two",
            "three": {
                "four": "five",
                "six": ["seven"],
            },
        }
        assert difference(source, target) == None
        assert difference(dict(source, one="TWO"), target) == dict(one="TWO")
        assert difference(dict(source, three=dict(eight="nine")), target) == dict(
            three=dict(eight="nine"),
        )
        assert difference(dict(source, eight=dict(nine="ten")), target) == dict(
            eight=dict(nine="ten"),
        )
        assert difference({}, target) == None
        assert difference(source, {}) == source


if __name__ == "__main__":
    unittest.main()

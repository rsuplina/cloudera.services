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

from ansible_collections.cloudera.services.plugins.module_utils.ml import (
    validate_project_id,
    validate_build_id,
)
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
)


class TestMLValidateID(ModuleTestCase):
    def test_project_id_valid(self):
        assert validate_project_id("7i6s-kidc-90fh-l55x")

    def test_project_id_invalid(self):
        assert not validate_project_id("AAAA-AAAA-ZZZZ-1111")
        assert not validate_project_id("ZZZZ")
        assert not validate_project_id("")

    def test_build_id_valid(self):
        assert validate_build_id("955ba03a-c341-4c01-afa7-b50f813f2d40")

    def test_build_id_invalid(self):
        assert not validate_build_id("AAAAAAAA-AAAA-ZZZZ-ZZZZ-111111111111")
        assert not validate_build_id("ZZZZ")
        assert not validate_build_id("")


if __name__ == "__main__":
    unittest.main()

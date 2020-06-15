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

import pprint
import pytest
import unittest

from ansible_collections.cloudera.services.plugins.modules import ml_project
from ansible_collections.cloudera.services.plugins.module_utils.ml import Squelch
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    setup_module_args,
)

MODULE_ARGS = {
    "api_key": "API_KEY",
    "endpoint": "ENDPOINT",
}

PATCH_QUERY = (
    "ansible_collections.cloudera.services.plugins.module_utils.ml.MLModule.query"
)


class TestMLProject(ModuleTestCase):

    def test_empty(self):
        setup_module_args({})

        with pytest.raises(AnsibleFailJson) as e:
            ml_project.main()

        assert "api_key" in e.value.msg
        assert "endpoint" in e.value.msg

    def test_present_minimum_id(self):
        TEST_ARGS = {
            "state": "present",
            "id": "aaaa-bbbb-2222-9999",
        }
        setup_module_args(
            {
                **MODULE_ARGS,
                **TEST_ARGS,
            },
        )

        with patch(PATCH_QUERY) as api_get:
            api_get.return_value = dict(name="BOOM")

            with pytest.raises(AnsibleExitJson) as e:
                ml_project.main()

        assert e.value.project == dict(name="BOOM")

        api_get.assert_called_once_with(
            method="GET",
            api=["projects", TEST_ARGS["id"]],
            squelch=[Squelch(status_code=403, return_value=None)],
        )


if __name__ == "__main__":
    unittest.main()

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

import os
import pprint
import pytest
import unittest

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.modules import ml_project
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    setup_module_args,
)


@unittest.skipUnless(
    os.getenv("CML_ENDPOINT") and os.getenv("CML_API_KEY"),
    "ML access parameters not set",
)
class TestMLProjectIntegration(ModuleTestCase):

    def test_create_project_minimum(self):
        setup_module_args(
            {
                "name": "integration test",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project.main()

    def test_update_project(self):
        setup_module_args(
            {
                "name": "integration test",
                "desc": "Updated!",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project.main()

    def test_delete_project(self):
        setup_module_args(
            {
                "name": "integration test",
                "state": "absent",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project.main()


if __name__ == "__main__":
    unittest.main()

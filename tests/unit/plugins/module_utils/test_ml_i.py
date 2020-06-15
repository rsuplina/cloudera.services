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
import unittest

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.ml import MLModule
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
    setup_module_args,
)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.getenv("CML_API_KEY", ""),
}

PATCH_GET = "requests.get"


@unittest.skipUnless(
    os.getenv("CML_ENDPOINT") and os.getenv("CML_API_KEY"),
    "ML access parameters not set",
)
class TestMLInfo(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.ml = MLModule(
            AnsibleModule(
                argument_spec=MLModule.argument_spec(),
            ),
        )

    def test_find_project(self):
        result = self.ml.find_project("Ansible Modules")
        pprint.pp(result) if result else print("Results: None")

    def test_find_project_not_found(self):
        result = self.ml.find_project("Initial projectX")
        pprint.pp(result) if result else print("Results: None")

    def test_get_project(self):
        result = self.ml.get_project("u4bj-tfzy-to3w-znpw")
        pprint.pp(result) if result else print("Results: None")

    def test_get_project_not_found(self):
        result = self.ml.get_project("7i6s-kidc-90fh-l55x")
        pprint.pp(result) if result else print("Results: None")


if __name__ == "__main__":
    unittest.main()

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

import os
import pprint
import pytest
import unittest

from ansible_collections.cloudera.services.plugins.modules import ml_runtimes_info
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    setup_module_args,
)


@unittest.skipUnless(
    os.getenv("CML_ENDPOINT") and os.getenv("CML_API_KEY"),
    "ML access parameters not set",
)
class TestMLRuntimesIntegration(ModuleTestCase):

    def test_list_all(self):
        setup_module_args({})

        with pytest.raises(AnsibleExitJson) as e:
            ml_runtimes_info.main()

        pprint.pp(e.value.runtimes)

    def test_filter_image(self):
        setup_module_args(
            {
                "image": "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-workbench-r4.1-standard:2022.04.1-b6",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_runtimes_info.main()

        pprint.pp(e.value.runtimes)

    def test_filter_image_invalid(self):
        setup_module_args(
            {
                "image": "12345",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_runtimes_info.main()

        pprint.pp(e.value.runtimes)

    def test_filter_editor(self):
        setup_module_args(
            {
                "editor": "Workbench",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_runtimes_info.main()

        pprint.pp(e.value.runtimes)


if __name__ == "__main__":
    unittest.main()

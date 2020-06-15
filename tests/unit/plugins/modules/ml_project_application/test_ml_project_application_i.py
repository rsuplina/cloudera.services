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

from ansible_collections.cloudera.services.plugins.modules import ml_project_application
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    setup_module_args,
)

PROJECT = "Ansible Module - Runtime"
APPLICATION = "Application Two"
SUBDOMAIN = "test"
SCRIPT = "example_application.py"
RUNTIME = "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-workbench-python3.7-standard:2022.04.1-b6"


@unittest.skipUnless(
    os.getenv("CML_ENDPOINT") and os.getenv("CML_API_KEY"),
    "ML access parameters not set",
)
class TestMLRuntimesIntegration(ModuleTestCase):

    def test_missing_application(self):
        setup_module_args(
            {
                "project_name": PROJECT,
            },
        )

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_application.main()

        pprint.pp(e.value)
        assert "id" in e.value.msg
        assert "name" in e.value.msg

    def test_missing_project(self):
        setup_module_args(
            {
                "name": APPLICATION,
            },
        )

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_application.main()

        pprint.pp(e.value)
        assert "project_id" in e.value.msg
        assert "project_name" in e.value.msg

    def test_create_minimal(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "name": APPLICATION,
                "subdomain": SUBDOMAIN,
                "script": SCRIPT,
                "runtime": RUNTIME,
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_application.main()

        pprint.pp(e.value.application)
        assert e.value.application

    def test_update(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "name": APPLICATION,
                "cpu": 2,
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_application.main()

        pprint.pp(e.value.application)
        assert e.value.application

    def test_stop(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "name": APPLICATION,
                "state": "stopped",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_application.main()

        pprint.pp(e.value.application)
        assert e.value.application


if __name__ == "__main__":
    unittest.main()

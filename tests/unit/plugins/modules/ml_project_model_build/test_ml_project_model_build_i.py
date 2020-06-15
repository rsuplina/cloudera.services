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
from multiprocessing.pool import RUN

__metaclass__ = type

import os
import pprint
import pytest
import unittest

from ansible_collections.cloudera.services.plugins.modules import ml_project_model_build
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    setup_module_args,
)

PROJECT_NAME = "Ansible Module - Runtime"
MODEL_NAME = "Model Two"
SCRIPT = "example_serve.py"
FUNCTION = "serve"
KERNEL = "python3"
RUNTIME = "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-workbench-python3.7-standard:2022.04.1-b6"
ADDONS = ["hadoop-cli-7.2.8-hf1"]


@unittest.skipUnless(
    os.getenv("CML_ENDPOINT") and os.getenv("CML_API_KEY"),
    "ML access parameters not set",
)
class TestMLRuntimesIntegration(ModuleTestCase):

    def test_missing_project(self):
        setup_module_args(
            {
                "model_name": MODEL_NAME,
                # "file": "foo"
            },
        )

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_model_build.main()

        pprint.pp(e.value)
        assert "project_id" in e.value.msg
        assert "project_name" in e.value.msg

    def test_missing_model(self):
        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                # "file": "foo"
            },
        )

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_model_build.main()

        pprint.pp(e.value)
        assert "name" in e.value.msg

    def test_create_runtime(self):
        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                "model_name": MODEL_NAME,
                "file": SCRIPT,
                "function": FUNCTION,
                "runtime": RUNTIME,
                "comment": "runtime",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_build.main()

        pprint.pp(e.value.build)
        assert e.value.build

    def test_create_kernel(self):
        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                "model_name": MODEL_NAME,
                "file": SCRIPT,
                "function": FUNCTION,
                "kernel": KERNEL,
                "comment": "kernel",
            },
        )

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_model_build.main()

        assert "runtime" in e.value.msg

        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                "model_name": MODEL_NAME,
                "file": SCRIPT,
                "function": FUNCTION,
                "runtime": RUNTIME,
                "kernel": KERNEL,
                "comment": "kernel",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_build.main()

        pprint.pp(e.value.build)
        assert e.value.build

    def test_update(self):
        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                "model_name": MODEL_NAME,
                "file": SCRIPT,
                "function": FUNCTION,
                "runtime": RUNTIME,
                "comment": "update",
            },
        )

        with pytest.raises(AnsibleExitJson) as e1:
            ml_project_model_build.main()

        pprint.pp(e1.value.build)
        assert e1.value.build

        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                "model_name": MODEL_NAME,
                "id": e1.value.build["id"],
            },
        )

        with pytest.raises(AnsibleExitJson) as e2:
            ml_project_model_build.main()

        pprint.pp(e2.value.build)
        assert e2.value.build

    def test_delete(self):
        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                "model_name": MODEL_NAME,
                "file": SCRIPT,
                "function": FUNCTION,
                "runtime": RUNTIME,
                "comment": "delete",
            },
        )

        with pytest.raises(AnsibleExitJson) as e1:
            ml_project_model_build.main()

        pprint.pp(e1.value.build)
        assert e1.value.build

        setup_module_args(
            {
                "project_name": PROJECT_NAME,
                "model_name": MODEL_NAME,
                "id": e1.value.build["id"],
                "state": "absent",
            },
        )

        with pytest.raises(AnsibleExitJson) as e2:
            ml_project_model_build.main()

        pprint.pp(e2.value.build)
        assert not e2.value.build


if __name__ == "__main__":
    unittest.main()

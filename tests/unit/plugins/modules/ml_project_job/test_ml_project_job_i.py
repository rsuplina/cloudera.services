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

from ansible_collections.cloudera.services.plugins.modules import ml_project_job
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    setup_module_args,
)

PROJECT_RUNTIME = "Ansible Module - Runtime"
PROJECT_KERNEL = "Ansible Module - Kernel"
JOB_RUNTIME = "Ansible Job - Runtime"
JOB_KERNEL = "Ansible Job - Kernel"


@unittest.skipUnless(
    os.getenv("CML_ENDPOINT") and os.getenv("CML_API_KEY"),
    "ML access parameters not set",
)
class TestMLRuntimesIntegration(ModuleTestCase):

    def test_missing_job(self):
        setup_module_args({})

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_job.main()

        assert "id" in e.value.msg
        assert "name" in e.value.msg
        pprint.pp(e.value)

    def test_missing_project(self):
        setup_module_args(
            {
                "name": JOB_RUNTIME,
            },
        )

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_job.main()

        assert "project_id" in e.value.msg
        assert "project_name" in e.value.msg
        pprint.pp(e.value)

    def test_create_minimal_runtime_engine(self):
        setup_module_args(
            {
                "project_name": PROJECT_RUNTIME,
                "name": JOB_RUNTIME,
                "runtime": "docker.io/rvanheerden/splash4:1.0",
                "script": "example_script.py",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_job.main()

        assert e.value.job
        pprint.pp(e.value.job)

    def test_create_minimal_kernel(self):
        setup_module_args(
            {
                "project_name": PROJECT_KERNEL,
                "name": JOB_KERNEL,
                "kernel": "python3",
                "script": "example_script.py",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_job.main()

        assert e.value.job
        pprint.pp(e.value.job)

    def test_update_timeout(self):
        setup_module_args(
            {
                "project_name": PROJECT_RUNTIME,
                "name": JOB_RUNTIME,
                "timeout": 60,
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_job.main()

        assert e.value.job
        pprint.pp(e.value.job)

    @unittest.skip("teardown")
    def test_delete_runtime_engine(self):
        setup_module_args(
            {
                "project_name": PROJECT_RUNTIME,
                "name": JOB_RUNTIME,
                "state": "absent",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_job.main()

        assert not e.value.job
        pprint.pp(e.value.job)

    @unittest.skip("teardown")
    def test_delete_kernel(self):
        setup_module_args(
            {
                "project_name": PROJECT_KERNEL,
                "name": JOB_KERNEL,
                "state": "absent",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_job.main()

        assert not e.value.job
        pprint.pp(e.value.job)


if __name__ == "__main__":
    unittest.main()

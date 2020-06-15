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

from ansible_collections.cloudera.services.plugins.modules import ml_project_model_info
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    setup_module_args,
)

PROJECT = "Ansible Module - Runtime"
MODEL = "Model One"


@unittest.skipUnless(
    os.getenv("CML_ENDPOINT") and os.getenv("CML_API_KEY"),
    "ML access parameters not set",
)
class TestMLRuntimesIntegration(ModuleTestCase):

    def test_missing_project(self):
        setup_module_args({})

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_model_info.main()

        pprint.pp(e.value)
        assert "project_id" in e.value.msg
        assert "project_name" in e.value.msg

    def test_all_project_name(self):
        setup_module_args(
            {
                "project_name": PROJECT,
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_info.main()

        pprint.pp(e.value.models)
        assert len(e.value.models) > 0

    def test_filter_name(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "name": MODEL,
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_info.main()

        pprint.pp(e.value.models)
        assert len(e.value.models) == 1

    def test_filter_name_invalid(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "name": "Not There",
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_info.main()

        pprint.pp(e.value)
        assert len(e.value.models) == 0

    def test_filter_creator_email(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "creator": {
                    "email": "wmudge@cloudera.com",
                },
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_info.main()

        pprint.pp(e.value)
        assert len(e.value.models) == 1

    def test_filter_creator_email_invalid(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "creator": {
                    "email": "example@cloudera.com",
                },
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_info.main()

        pprint.pp(e.value)
        assert len(e.value.models) == 0

    def test_filter_auth(self):
        setup_module_args(
            {
                "project_name": PROJECT,
                "auth": True,
            },
        )

        with pytest.raises(AnsibleExitJson) as e:
            ml_project_model_info.main()

        pprint.pp(e.value)
        assert len(e.value.models) == 1


if __name__ == "__main__":
    unittest.main()

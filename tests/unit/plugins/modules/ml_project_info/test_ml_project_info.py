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

import pytest
import unittest

from ansible_collections.cloudera.services.plugins.modules import ml_project_info
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


class TestMLProjectInfo(ModuleTestCase):

    def test_empty(self):
        setup_module_args({})

        with pytest.raises(AnsibleFailJson) as e:
            ml_project_info.main()

        assert "api_key" in e.value.msg
        assert "endpoint" in e.value.msg

    def test_none(self):
        setup_module_args(
            {
                **MODULE_ARGS,
            },
        )

        with patch(PATCH_QUERY) as api_get:
            api_get.return_value = []

            with pytest.raises(AnsibleExitJson) as e:
                ml_project_info.main()

            assert e.value.projects == []

            api_get.assert_called_once_with(
                method="GET",
                api=["projects"],
                field="projects",
                params=dict(include_public_projects=True),
            )

    def test_all(self):
        setup_module_args(
            {
                **MODULE_ARGS,
            },
        )

        with patch(PATCH_QUERY) as api_get:
            api_get.return_value = [dict(name="BOOM"), dict(name="BASH")]

            with pytest.raises(AnsibleExitJson) as e:
                ml_project_info.main()

            assert e.value.projects == [dict(name="BOOM"), dict(name="BASH")]

            api_get.assert_called_once_with(
                method="GET",
                api=["projects"],
                field="projects",
                params=dict(include_public_projects=True),
            )

    def test_username(self):
        setup_module_args(
            {
                **MODULE_ARGS,
                "user": "USER",
            },
        )

        with patch(PATCH_QUERY) as api_get:
            api_get.return_value = [dict(name="BOOM")]

            with pytest.raises(AnsibleExitJson) as e:
                ml_project_info.main()

            assert e.value.projects == [dict(name="BOOM")]

            api_get.assert_called_once_with(
                method="GET",
                api=["projects"],
                field="projects",
                params=dict(
                    include_public_projects=True,
                    search_filter='{"creator.username":"USER"}',
                ),
            )

    def test_project_name(self):
        setup_module_args(
            {
                **MODULE_ARGS,
                "name": "PROJECT NAME",
            },
        )

        with patch(PATCH_QUERY) as api_get:
            api_get.return_value = [dict(name="BOOM")]

            with pytest.raises(AnsibleExitJson) as e:
                ml_project_info.main()

            assert e.value.projects == [dict(name="BOOM")]

            api_get.assert_called_once_with(
                method="GET",
                api=["projects"],
                field="projects",
                params=dict(
                    include_public_projects=True,
                    search_filter='{"name":"PROJECT NAME"}',
                ),
            )


if __name__ == "__main__":
    unittest.main()

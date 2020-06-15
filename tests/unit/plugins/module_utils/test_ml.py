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

import json
import unittest

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cloudera.services.plugins.module_utils.ml import MLModule
from ansible_collections.cloudera.services.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
    setup_module_args,
)

ENDPOINT = "ENDPOINT/api/v2/foo"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer API_KEY",
}

PATCH_REQUEST = "requests.request"


class TestMLInfo(ModuleTestCase):
    def setUp(self):
        super().setUp()
        setup_module_args(
            {
                "api_key": "API_KEY",
                "endpoint": "ENDPOINT",
            },
        )
        self.ml = MLModule(
            AnsibleModule(
                argument_spec=MLModule.argument_spec(),
            ),
        )

    def test_get_no_params(self):
        with patch(PATCH_REQUEST) as api:
            api.return_value.json.return_value = {"projects": ["boom"]}
            api.return_value.status_code = 200

            # with pytest.raises(Exception) as e:
            #    result = self.ml.get("foo", "projects")
            # print("Returned: ", str(e.value))

            result = self.ml.query(method="GET", api=["foo"], field="projects")
            assert result == ["boom"]

            api.assert_called_once_with(
                "GET",
                ENDPOINT,
                headers=HEADERS,
                params={},
            )

    def test_get_params(self):
        with patch(PATCH_REQUEST) as api:
            api.return_value.json.return_value = {"projects": ["boom"]}
            api.return_value.status_code = 200

            # with pytest.raises(Exception) as e:
            #    result = self.ml.get("foo", "projects")
            # print("Returned: ", str(e.value))

            params = dict(one=1234)

            result = self.ml.query(
                method="GET",
                api=["foo"],
                field="projects",
                params=params,
            )
            assert result == ["boom"]

            api.assert_called_once_with(
                "GET",
                ENDPOINT,
                headers=HEADERS,
                params=params,
            )

    def test_get_multi_params(self):
        with patch(PATCH_REQUEST) as api:
            api.return_value.json.return_value = {"projects": ["boom"]}
            api.return_value.status_code = 200

            # with pytest.raises(Exception) as e:
            #    result = self.ml.get("foo", "projects")
            # print("Returned: ", str(e.value))

            params = dict(
                one=1234,
                two=json.dumps({"creator.username": "foo"}),
            )

            result = self.ml.query(
                method="GET",
                api=["foo"],
                field="projects",
                params=params,
            )
            assert result == ["boom"]

            api.assert_called_once_with(
                "GET",
                ENDPOINT,
                headers=HEADERS,
                params=params,
            )

    def test_get_pagination(self):
        with patch(PATCH_REQUEST) as api:
            api.return_value.json.side_effect = [
                {"projects": ["boom1"], "next_page_token": "gimme2"},
                {"projects": ["boom2"], "next_page_token": "gimme3"},
                {"projects": ["boom3"]},
            ]
            api.return_value.status_code = 200

            # with pytest.raises(Exception) as e:
            #    result = self.ml.get("foo", "projects")
            # print("Returned: ", str(e.value))

            result = self.ml.query("GET", ["foo"], "projects")
            assert result == ["boom1", "boom2", "boom3"]
            assert api.call_count == 3

    @unittest.skip("Needs adjustment, also, need to add Squelch tests")
    def test_error(self):
        with patch(PATCH_REQUEST) as api:
            api.return_value = dict(
                message="BOOM",
                code=42,
                error="Went boom",
                details=["boom", "thing"],
            )

            # assert e.value.msg == "BOOM"

            api.assert_called_once_with(
                "GET",
                "ENDPOINT/api/v",
                field="projects",
                params=dict(include_public_projects=True),
            )

    @unittest.skip("Not yet implemented")
    def test_find_project(self):
        """Nothing here yet"""

    @unittest.skip("Not yet implemented")
    def test_get_project(self):
        """Nothing here yet"""


if __name__ == "__main__":
    unittest.main()

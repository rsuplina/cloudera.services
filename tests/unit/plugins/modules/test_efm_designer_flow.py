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

import json
import os
import pprint
import pytest
import unittest

from ansible_collections.cloudera.services.plugins.modules import efm_designer_flow
from ansible_collections.cloudera.services.tests.unit.plugins.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    setup_module_args,
)

FLOW_01 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "flow_01.json")


@unittest.skipUnless(os.getenv("EFM_ENDPOINT"), "EFM access parameters not set")
class TestMLRuntimesIntegration(ModuleTestCase):

    def test_create(self):
        with open(FLOW_01, "+r") as f:

            setup_module_args(
                {
                    "endpoint": os.getenv("EFM_ENDPOINT"),
                    "username": "",
                    "password": "",
                    "agent_class": "minifi-1.21.0",
                    "flow_body": json.loads(f.read()),
                    "state": "present",
                },
            )

            with pytest.raises(AnsibleExitJson) as e:
                efm_designer_flow.main()

            pprint.pp(e.value.args[0], compact=True)

    def test_publish(self):
        with open(FLOW_01, "+r") as f:

            setup_module_args(
                {
                    "endpoint": os.getenv("EFM_ENDPOINT"),
                    "username": "",
                    "password": "",
                    "agent_class": "minifi-1.21.0",
                    # "flow_body": json.loads(f.read()),
                    "state": "publish",
                    "debug": False,
                },
            )

            with pytest.raises(AnsibleFailJson) as e:
                efm_designer_flow.main()

            pprint.pp(e.value.args[0], compact=True)

    def test_publish_force(self):
        with open(FLOW_01, "+r") as f:

            setup_module_args(
                {
                    "endpoint": os.getenv("EFM_ENDPOINT"),
                    "username": "",
                    "password": "",
                    "agent_class": "minifi-1.21.0",
                    # "flow_body": json.loads(f.read()),
                    "state": "publish",
                    "force": True,
                    "debug": False,
                },
            )

            with pytest.raises(AnsibleExitJson) as e:
                efm_designer_flow.main()

            pprint.pp(e.value.args[0], compact=True)

    def test_publish_parameters(self):
        with open(FLOW_01, "+r") as f:

            setup_module_args(
                {
                    "endpoint": os.getenv("EFM_ENDPOINT"),
                    "username": "",
                    "password": "",
                    "agent_class": "minifi-1.21.0",
                    # "flow_body": json.loads(f.read()),
                    "parameters": {
                        "foo": "bar",
                    },
                    "state": "publish",
                    "force": True,
                    "debug": False,
                },
            )

            with pytest.raises(AnsibleExitJson) as e:
                efm_designer_flow.main()

        pprint.pp(e.value.args[0], compact=True)

    def test_publish_all(self):
        with open(FLOW_01, "+r") as f:

            setup_module_args(
                {
                    "endpoint": os.getenv("EFM_ENDPOINT"),
                    "username": "",
                    "password": "",
                    "agent_class": "minifi-1.21.0",
                    "flow_body": json.loads(f.read()),
                    "parameters": {
                        "foobar": "Inline update",
                    },
                    "state": "publish",
                    "force": True,
                    "debug": False,
                },
            )

            with pytest.raises(AnsibleExitJson) as e:
                efm_designer_flow.main()

        pprint.pp(e.value.args[0], compact=True)


if __name__ == "__main__":
    unittest.main()

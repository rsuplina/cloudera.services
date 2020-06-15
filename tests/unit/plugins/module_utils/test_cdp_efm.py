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

import unittest

from unittest.mock import patch

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cloudera.services.plugins.module_utils.cdp_efm import (
    CdpEfmModule,
)
from ansible_collections.cloudera.services.tests.unit.plugins.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    setup_module_args,
)


class TestCdpEfm(ModuleTestCase):

    def test_get_access(self):
        setup_module_args(
            {
                "endpoint": "http://ec2-18-118-195-154.us-east-2.compute.amazonaws.com:10090",
                "username": "test",
                "password": "not_there",
                "debug": "yes",
            },
        )

        expected = dict()

        with self.assertRaises(AnsibleExitJson) as e:
            module = AnsibleModule(**CdpEfmModule.module_spec())

            efm_util = CdpEfmModule(module, "efm-util-test")
            # print(efm_util._get_access())
            efm_util._session.close()

            # print(efm_util._get_debug_log())

        # with patch('cdpy.cdpy.CdpyEnvironments') as mocked_cdp:
        #     mocked_cdp.return_value.describe_environment.return_value = None
        #     mocked_cdp.return_value.create_aws_environment.return_value = { 'name': 'Successful test' }

        #     with pytest.raises(AnsibleExitJson) as e:
        #         env.main()

        #     print("Returned: ", str(e.value))

        #     mocked_cdp.return_value.describe_environment.assert_called_once_with('unit-test')
        #     mocked_cdp.return_value.create_aws_environment.assert_called_once_with(**expected)


if __name__ == "__main__":
    unittest.main()

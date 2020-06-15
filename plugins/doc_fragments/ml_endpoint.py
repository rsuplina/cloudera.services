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


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      endpoint:
        description:
          - Endpoint URL of the CML Workspace.
          - If not set, the environment variable C(CML_ENDPOINT) will be used.
        type: str
        required: True
        aliases:
          - url
          - workspace_url
      api_key:
        description:
          - A user API token or key for the CML Workspace.
          - If not set, the environment variable C(CML_API_KEY) will be used.
          - This option uses C(no_log).
        type: str
        required: True
        aliases:
          - token
      endpoint_tls:
        description:
          - Verify the TLS certificates for the Cloudera API endpoint.
          - Set to False to skip TLS certificate verification.
        type: bool
        default: True
        aliases:
          - verify_endpoint_tls
          - verify_tls
          - verify_api_tls
      debug:
        description:
          - Flag to set the capture of CML Workspace endpoint logging.
        type: bool
        default: False
        aliases:
          - debug_endpoint
      agent_header:
        description:
          - A descriptive name for the HTTP agent used to access the CML Workspace endpoint.
        type: str
        default: ClouderaFoundry
    """

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
                - URL of the CDP REST endpoint.
            type: str
            required: True
            aliases:
                - url
                - api
        username:
            description:
                - Username authentication field for the CDP REST endpoint.
            type: str
            required: True
            aliases:
                - user
                - usr
        password:
            description:
                - Password authentication field for the CDP REST endpoint.
            type: str
            required: True
            aliases:
                - pass
                - pwd
        verify_tls:
            description:
                - Flag to verify the TLS certificates for the CDP REST endpoint.
            type: bool
            required: False
            default: True
            aliases:
                - tls
        ca_cert_file:
            description:
                - CA certification file for verifying the TLS certificates for the CDP REST endpoint.
                - See U(https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification) for SSL certificate verification details.
            type: path
            required: False
            aliases:
                - cert
                - truststore
        agent_header:
            description:
                - Request user agent for CDP REST endpoint interaction.
            type: str
            required: False
            default: CDP_REST
            aliases:
                - agent
        debug:
            description:
                - Flag to capture the CDP REST API debug log.
            type: bool
            required: False
            default: False
            aliases:
                - debug_endpoints
    """

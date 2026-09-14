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

"""
REST clients for the Apache Ranger Admin API.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import json

from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.common.dict_transformations import (
    camel_dict_to_snake_dict,
    snake_dict_to_camel_dict,
)

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    from_dict,
    to_dict,
    NULLABLE,
    ServicesClient,
    ServicesError,
)


@dataclass
class RangerService:
    """Representation of an Apache Ranger service."""

    # Mutable - required when creating a service
    name: str

    # Mutable - optional
    type: Union[str, None, NULLABLE] = NULLABLE
    display_name: Union[str, None, NULLABLE] = NULLABLE
    description: Union[str, None, NULLABLE] = NULLABLE
    tag_service: Union[str, None, NULLABLE] = NULLABLE
    is_enabled: Union[bool, None, NULLABLE] = NULLABLE
    configs: Union[Dict[str, Any], None, NULLABLE] = NULLABLE

    # Read-only (set by Ranger)
    id: Union[int, None, NULLABLE] = NULLABLE
    guid: Union[str, None, NULLABLE] = NULLABLE
    version: Union[int, None, NULLABLE] = NULLABLE
    create_time: Union[int, None, NULLABLE] = NULLABLE
    update_time: Union[int, None, NULLABLE] = NULLABLE
    created_by: Union[str, None, NULLABLE] = NULLABLE
    updated_by: Union[str, None, NULLABLE] = NULLABLE
    policy_version: Union[int, None, NULLABLE] = NULLABLE
    policy_update_time: Union[int, None, NULLABLE] = NULLABLE
    tag_version: Union[int, None, NULLABLE] = NULLABLE
    tag_update_time: Union[int, None, NULLABLE] = NULLABLE

    @classmethod
    def argument_spec(cls) -> Dict[str, Any]:
        """Return the Ansible argument spec for the mutable RangerService parameters."""
        return dict(
            name=dict(type="str", required=False),
            type=dict(type="str", required=False),
            display_name=dict(type="str", required=False),
            description=dict(type="str", required=False),
            tag_service=dict(type="str", required=False),
            is_enabled=dict(
                type="bool",
                required=False,
                default=True,
                aliases=["enabled"],
            ),
            configs=dict(type="dict", required=False),
        )


def _service_to_payload(service: RangerService) -> Dict[str, Any]:
    """Serialise a RangerService into a camelCase Ranger request payload."""
    data = to_dict(service)
    configs = data.pop("configs", None)
    payload = snake_dict_to_camel_dict(data)
    if configs is not None:
        payload["configs"] = configs
    return payload


def _service_from_response(raw: Dict[str, Any]) -> RangerService:
    """Deserialise a Ranger service response into a RangerService."""
    data = dict(raw)
    configs = data.pop("configs", None)
    service = from_dict(
        RangerService,
        camel_dict_to_snake_dict(data, reversible=True),
    )
    if configs is not None:
        service.configs = configs
    return service


def _is_ranger_not_found(result: Any) -> bool:
    """Check whether a passthru response is Ranger's DATA_NOT_FOUND 400 (its substitute for 404)."""
    if not isinstance(result, dict) or "status" not in result:
        return False

    if result["status"] != 400:
        return False

    body = result.get("body")
    if not body:
        return False

    try:
        error_data = json.loads(body) if isinstance(body, bytes) else body
        if error_data.get("statusCode") == 1:
            message_list = error_data.get("messageList", [])
            return any(msg.get("name") == "DATA_NOT_FOUND" for msg in message_list)
    except (json.JSONDecodeError, AttributeError, KeyError):
        pass

    return False


class RangerServiceClient:
    """Apache Ranger Service API client."""

    def __init__(self, api_client: ServicesClient) -> None:
        self.api_client: ServicesClient = api_client

    def list_services(self) -> List[RangerService]:
        """List all services."""
        result = self.api_client.get(
            "/service/plugins/services",
            squelch={404: {"services": []}},
        )
        services_raw = result.get("services", []) if result else []
        return [_service_from_response(s) for s in services_raw]

    def get_service_by_id(self, service_id: int) -> Optional[RangerService]:
        """Retrieve a single service by id, or None if not found."""
        result = self.api_client.get(
            f"/service/plugins/services/{service_id}",
            squelch={404: None},
            passthru=[400],
        )

        if result is None or _is_ranger_not_found(result):
            return None

        if isinstance(result, dict) and result.get("status") == 400:
            raise ServicesError(
                f"HTTP 400 Error retrieving service {service_id}",
                status=400,
            )

        return _service_from_response(result)

    def get_service_by_name(self, service_name: str) -> Optional[RangerService]:
        """Retrieve a single service by name, or None if not found."""
        result = self.api_client.get(
            f"/service/plugins/services/name/{service_name}",
            squelch={404: None},
            passthru=[400],
        )

        if result is None or _is_ranger_not_found(result):
            return None

        if isinstance(result, dict) and result.get("status") == 400:
            raise ServicesError(
                f"HTTP 400 Error retrieving service '{service_name}'",
                status=400,
            )

        return _service_from_response(result)

    def create_service(self, service: RangerService) -> RangerService:
        """Create a new service."""
        result = self.api_client.post(
            "/service/plugins/services",
            data=_service_to_payload(service),
        )
        return _service_from_response(result)

    def update_service(self, service: RangerService) -> RangerService:
        """Update an existing service by its id."""
        if service.id is NULLABLE or service.id is None:
            raise ValueError("Cannot update a service without an id.")
        result = self.api_client.put(
            f"/service/plugins/services/{service.id}",
            data=_service_to_payload(service),
        )
        return _service_from_response(result)

    def delete_service_by_id(self, service_id: int) -> None:
        """Delete a service by id (idempotent)."""
        result = self.api_client.delete(
            f"/service/plugins/services/{service_id}",
            squelch={404: None},
            passthru=[400],
        )

        if _is_ranger_not_found(result):
            return None

        if isinstance(result, dict) and result.get("status") == 400:
            raise ServicesError(
                f"HTTP 400 Error deleting service {service_id}",
                status=400,
            )


def extract_service_params(module_instance) -> Dict[str, Any]:
    """Extract the mutable service parameters from a module instance into a dict."""
    return {
        "name": getattr(module_instance, "name", None),
        "type": getattr(module_instance, "type", None),
        "display_name": getattr(module_instance, "display_name", None),
        "description": getattr(module_instance, "description", None),
        "tag_service": getattr(module_instance, "tag_service", None),
        "is_enabled": getattr(module_instance, "is_enabled", None),
        "configs": getattr(module_instance, "configs", None),
    }

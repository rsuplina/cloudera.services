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
REST clients for the Apache Ranger API.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import json
from ansible.module_utils.common.dict_transformations import (
    camel_dict_to_snake_dict,
    snake_dict_to_camel_dict,
)
from ansible_collections.ansible.utils.plugins.module_utils.common.utils import (
    dict_merge,
)

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    from_dict,
    to_dict,
    NULLABLE,
    ServicesClient,
    ServicesError,
)


@dataclass
class RangerPolicyItemAccess:
    """A single access entry inside a RangerPolicyItem (type + isAllowed)."""

    type: str
    is_allowed: Union[bool, None, NULLABLE] = NULLABLE


@dataclass
class RangerPolicyItemCondition:
    """A custom condition entry inside a RangerPolicyItem or RangerPolicy."""

    type: str
    values: Union[List[str], None, NULLABLE] = NULLABLE


@dataclass
class RangerPolicyItem:
    """
    A policy item (allow / deny / allow-exception / deny-exception) as defined
    in the Ranger Swagger ``RangerPolicyItem`` schema.
    """

    accesses: Union[List[RangerPolicyItemAccess], None, NULLABLE] = NULLABLE
    users: Union[List[str], None, NULLABLE] = NULLABLE
    groups: Union[List[str], None, NULLABLE] = NULLABLE
    roles: Union[List[str], None, NULLABLE] = NULLABLE
    conditions: Union[List[RangerPolicyItemCondition], None, NULLABLE] = NULLABLE
    delegate_admin: Union[bool, None, NULLABLE] = NULLABLE


@dataclass
class RangerPolicyItemDataMaskInfo:
    """Data-mask info for ``dataMaskPolicyItems``."""

    data_mask_type: Union[str, None, NULLABLE] = NULLABLE
    condition_expr: Union[str, None, NULLABLE] = NULLABLE
    value_expr: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class RangerDataMaskPolicyItem:
    """
    A data-mask policy item as defined by the Ranger Swagger
    ``RangerDataMaskPolicyItem`` schema.
    """

    data_mask_info: Union[RangerPolicyItemDataMaskInfo, None, NULLABLE] = NULLABLE
    accesses: Union[List[RangerPolicyItemAccess], None, NULLABLE] = NULLABLE
    users: Union[List[str], None, NULLABLE] = NULLABLE
    groups: Union[List[str], None, NULLABLE] = NULLABLE
    roles: Union[List[str], None, NULLABLE] = NULLABLE
    conditions: Union[List[RangerPolicyItemCondition], None, NULLABLE] = NULLABLE
    delegate_admin: Union[bool, None, NULLABLE] = NULLABLE


@dataclass
class RangerPolicyItemRowFilterInfo:
    """Row-filter info for ``rowFilterPolicyItems``."""

    filter_expr: Union[str, None, NULLABLE] = NULLABLE


@dataclass
class RangerRowFilterPolicyItem:
    """
    A row-filter policy item as defined by the Ranger Swagger
    ``RangerRowFilterPolicyItem`` schema.
    """

    row_filter_info: Union[RangerPolicyItemRowFilterInfo, None, NULLABLE] = NULLABLE
    accesses: Union[List[RangerPolicyItemAccess], None, NULLABLE] = NULLABLE
    users: Union[List[str], None, NULLABLE] = NULLABLE
    groups: Union[List[str], None, NULLABLE] = NULLABLE
    roles: Union[List[str], None, NULLABLE] = NULLABLE
    conditions: Union[List[RangerPolicyItemCondition], None, NULLABLE] = NULLABLE
    delegate_admin: Union[bool, None, NULLABLE] = NULLABLE


@dataclass
class RangerPolicyResource:
    """
    A single resource definition used inside ``RangerPolicy.resources`` as
    defined by the Ranger Swagger ``RangerPolicyResource`` schema.
    """

    values: Union[List[str], None, NULLABLE] = NULLABLE
    is_excludes: Union[bool, None, NULLABLE] = NULLABLE
    is_recursive: Union[bool, None, NULLABLE] = NULLABLE


@dataclass
class RangerValidityRecurrence:
    """One recurrence entry inside a ``RangerValiditySchedule``."""

    schedule: Union[Dict[str, Any], None, NULLABLE] = NULLABLE
    interval: Union[Dict[str, Any], None, NULLABLE] = NULLABLE


@dataclass
class RangerValiditySchedule:
    """A validity schedule as defined by the Ranger Swagger schema."""

    start_time: Union[str, None, NULLABLE] = NULLABLE
    end_time: Union[str, None, NULLABLE] = NULLABLE
    time_zone: Union[str, None, NULLABLE] = NULLABLE
    recurrences: Union[List[RangerValidityRecurrence], None, NULLABLE] = NULLABLE


@dataclass
class RangerPolicy:
    """
    Full representation of an Apache Ranger policy, mirroring the Ranger
    Swagger ``RangerPolicy`` schema (which extends ``RangerBaseModelObject``).

    Read-only fields (id, guid, create_time, update_time, created_by,
    updated_by, version, resource_signature) are modelled as optional
    NULLABLE so they are omitted when serialising to a request payload via
    :func:`to_dict`.
    """

    # Mutable – required when creating a policy
    name: str
    service: str

    # Mutable – optional
    service_type: Union[str, None, NULLABLE] = NULLABLE
    description: Union[str, None, NULLABLE] = NULLABLE
    policy_type: Union[int, None, NULLABLE] = NULLABLE
    policy_priority: Union[int, None, NULLABLE] = NULLABLE
    is_enabled: Union[bool, None, NULLABLE] = NULLABLE
    is_audit_enabled: Union[bool, None, NULLABLE] = NULLABLE
    is_deny_all_else: Union[bool, None, NULLABLE] = NULLABLE
    zone_name: Union[str, None, NULLABLE] = NULLABLE
    resources: Union[Dict[str, RangerPolicyResource], None, NULLABLE] = NULLABLE
    additional_resources: Union[
        List[Dict[str, RangerPolicyResource]],
        None,
        NULLABLE,
    ] = NULLABLE
    conditions: Union[List[RangerPolicyItemCondition], None, NULLABLE] = NULLABLE
    policy_items: Union[List[RangerPolicyItem], None, NULLABLE] = NULLABLE
    deny_policy_items: Union[List[RangerPolicyItem], None, NULLABLE] = NULLABLE
    allow_exceptions: Union[List[RangerPolicyItem], None, NULLABLE] = NULLABLE
    deny_exceptions: Union[List[RangerPolicyItem], None, NULLABLE] = NULLABLE
    data_mask_policy_items: Union[List[RangerDataMaskPolicyItem], None, NULLABLE] = (
        NULLABLE
    )
    row_filter_policy_items: Union[List[RangerRowFilterPolicyItem], None, NULLABLE] = (
        NULLABLE
    )
    validity_schedules: Union[List[RangerValiditySchedule], None, NULLABLE] = NULLABLE
    policy_labels: Union[List[str], None, NULLABLE] = NULLABLE
    options: Union[Dict[str, Any], None, NULLABLE] = NULLABLE

    # Read-only (set by Ranger)
    id: Union[int, None, NULLABLE] = NULLABLE
    guid: Union[str, None, NULLABLE] = NULLABLE
    resource_signature: Union[str, None, NULLABLE] = NULLABLE
    version: Union[int, None, NULLABLE] = NULLABLE
    create_time: Union[int, None, NULLABLE] = NULLABLE
    update_time: Union[int, None, NULLABLE] = NULLABLE
    created_by: Union[str, None, NULLABLE] = NULLABLE
    updated_by: Union[str, None, NULLABLE] = NULLABLE

    @classmethod
    def argument_spec(cls) -> Dict[str, Any]:
        """Return the Ansible argument spec for RangerPolicy parameters."""
        return dict(
            name=dict(type="str", required=False),
            service=dict(type="str", required=False),
            service_type=dict(type="str", required=False),
            description=dict(type="str", required=False),
            policy_type=dict(type="int", required=False),
            policy_priority=dict(type="int", required=False),
            is_enabled=dict(type="bool", required=False, aliases=["enabled"]),
            is_audit_enabled=dict(
                type="bool",
                required=False,
                aliases=["audit_enabled"],
            ),
            is_deny_all_else=dict(
                type="bool",
                required=False,
                aliases=["deny_all_else"],
            ),
            zone_name=dict(type="str", required=False),
            resources=dict(type="dict", required=False),
            additional_resources=dict(
                type="list",
                elements="dict",
                required=False,
            ),
            conditions=dict(type="list", elements="dict", required=False),
            policy_items=dict(
                type="list",
                elements="dict",
                required=False,
                aliases=["access_policies"],
            ),
            deny_policy_items=dict(
                type="list",
                elements="dict",
                required=False,
                aliases=["deny_policies"],
            ),
            allow_exceptions=dict(type="list", elements="dict", required=False),
            deny_exceptions=dict(type="list", elements="dict", required=False),
            data_mask_policy_items=dict(
                type="list",
                elements="dict",
                required=False,
                aliases=["data_mask_policies"],
            ),
            row_filter_policy_items=dict(
                type="list",
                elements="dict",
                required=False,
                aliases=["row_filter_policies"],
            ),
            validity_schedules=dict(type="list", elements="dict", required=False),
            policy_labels=dict(type="list", elements="str", required=False),
            options=dict(type="dict", required=False),
        )


# ---------------------------------------------------------------------------
# RangerPolicyClient
# ---------------------------------------------------------------------------


def _is_ranger_policy_not_found(result: Any) -> bool:
    """
    Check if a Ranger API response indicates a policy was not found.

    Ranger returns HTTP 400 with a "DATA_NOT_FOUND" error body when a policy doesn't exist,
    rather than the standard HTTP 404. This helper checks for that specific pattern.

    Args:
        result: The API response dict from a passthru status code

    Returns:
        True if the policy was not found, False otherwise
    """
    if not isinstance(result, dict) or "status" not in result:
        return False

    if result["status"] != 400:
        return False

    body = result.get("body")
    if not body:
        return False

    try:
        error_data = json.loads(body) if isinstance(body, bytes) else body
        # Check for Ranger's specific "DATA_NOT_FOUND" error pattern
        if error_data.get("statusCode") == 1:
            message_list = error_data.get("messageList", [])
            return any(msg.get("name") == "DATA_NOT_FOUND" for msg in message_list)
    except (json.JSONDecodeError, AttributeError, KeyError):
        pass

    return False


class RangerPolicyClient:
    """Cloudera / Apache Ranger Policy API client.

    Wraps the ``/service/plugins/policies`` REST endpoints documented in the Ranger
    Swagger specification (``ServiceREST`` tag).
    """

    def __init__(self, api_client: ServicesClient) -> None:
        """
        Initialise the client.

        Args:
            api_client: A :class:`ServicesClient` (or subclass) instance used
                to make HTTP requests against the Ranger Admin.
        """
        self.api_client: ServicesClient = api_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_policies(
        self,
        service_name: Optional[str] = None,
    ) -> List[RangerPolicy]:
        """List all policies, optionally filtered by *service_name*.

        Calls ``GET /service/plugins/policies`` with an optional ``serviceName`` query
        parameter.

        Args:
            service_name: When provided only policies for this service are
                returned.

        Returns:
            A list of :class:`RangerPolicy` instances.
        """
        params: Dict[str, Any] = {}
        if service_name:
            params["serviceName"] = service_name

        result = self.api_client.get(
            "/service/plugins/policies",
            params=params if params else None,
            squelch={404: {"policies": []}},
        )
        policies_raw = result.get("policies", []) if result else []
        return [
            from_dict(RangerPolicy, camel_dict_to_snake_dict(p, reversible=True))
            for p in policies_raw
        ]

    def get_policy_by_id(self, policy_id: int) -> Optional[RangerPolicy]:
        """Retrieve a single policy by its numeric *policy_id*.

        Calls ``GET /service/plugins/policies/{id}``.

        Args:
            policy_id: The numeric identifier of the policy.

        Returns:
            A :class:`RangerPolicy` instance, or ``None`` if not found.
        """
        # Use passthru=[400] because Ranger returns HTTP 400 with "DATA_NOT_FOUND" error
        # when a policy doesn't exist, instead of the standard HTTP 404.
        # This allows us to inspect the response and return None gracefully.
        result = self.api_client.get(
            f"/service/plugins/policies/{policy_id}",
            passthru=[400],
        )

        # Handle Ranger's 400 "DATA_NOT_FOUND" response
        if _is_ranger_policy_not_found(result):
            return None

        # If we got a 400 but it's not a "not found" error, raise it
        if isinstance(result, dict) and result.get("status") == 400:
            raise ServicesError(
                f"HTTP 400 Error retrieving policy {policy_id}",
                status=400,
            )

        return (
            from_dict(RangerPolicy, camel_dict_to_snake_dict(result, reversible=True))
            if result is not None
            else None
        )

    def get_policy_by_name(
        self,
        service_name: str,
        policy_name: str,
    ) -> Optional[RangerPolicy]:
        """Retrieve a policy by *service_name* and *policy_name*.

        Calls ``GET /service/plugins/policies`` and filters on the client side.

        Args:
            service_name: The Ranger service the policy belongs to.
            policy_name: The name of the policy.

        Returns:
            A :class:`RangerPolicy` instance, or ``None`` if not found.
        """
        policies = self.list_policies(service_name=service_name)
        for policy in policies:
            if policy.name == policy_name:
                return policy
        return None

    def create_policy(self, policy: RangerPolicy) -> RangerPolicy:
        """Create a new policy.

        Calls ``POST /service/plugins/policies``.

        Args:
            policy: The :class:`RangerPolicy` to create.

        Returns:
            The created :class:`RangerPolicy` with server-assigned fields
            (``id``, ``guid``, ``version``, etc.) populated.
        """
        result = self.api_client.post(
            "/service/plugins/policies",
            data=snake_dict_to_camel_dict(to_dict(policy)),
        )
        return from_dict(
            RangerPolicy,
            camel_dict_to_snake_dict(result, reversible=True),
        )

    def update_policy(self, policy: RangerPolicy) -> RangerPolicy:
        """Update an existing policy by its ``id``.

        Calls ``PUT /service/plugins/policies/{id}``.

        Args:
            policy: The :class:`RangerPolicy` to update. Must have ``id`` set.

        Returns:
            The updated :class:`RangerPolicy`.

        Raises:
            ValueError: If ``policy.id`` is not set.
        """
        if policy.id is NULLABLE or policy.id is None:
            raise ValueError("Cannot update a policy without an id.")
        result = self.api_client.put(
            f"/service/plugins/policies/{policy.id}",
            data=snake_dict_to_camel_dict(to_dict(policy)),
        )
        return from_dict(
            RangerPolicy,
            camel_dict_to_snake_dict(result, reversible=True),
        )

    def delete_policy_by_id(self, policy_id: int) -> None:
        """Delete a policy by its numeric *policy_id*.

        Calls ``DELETE /service/plugins/policies/{id}``.

        Args:
            policy_id: The numeric identifier of the policy to delete.
        """
        # Use passthru=[400] because Ranger returns HTTP 400 with "DATA_NOT_FOUND" error
        # when a policy doesn't exist, instead of the standard HTTP 404.
        # This allows us to treat non-existent policies as successfully deleted (idempotent).
        result = self.api_client.delete(
            f"/service/plugins/policies/{policy_id}",
            passthru=[400],
        )

        # Handle Ranger's 400 "DATA_NOT_FOUND" response - treat as successful delete
        if _is_ranger_policy_not_found(result):
            return None  # Policy already doesn't exist, treat as success

        # If we got a 400 but it's not a "not found" error, raise it
        if isinstance(result, dict) and result.get("status") == 400:
            raise ServicesError(
                f"HTTP 400 Error deleting policy {policy_id}",
                status=400,
            )


# ---------------------------------------------------------------------------
# Helper functions for modules
# ---------------------------------------------------------------------------


def is_policy_subset(subset: Dict[str, Any], superset: Dict[str, Any]) -> bool:
    """
    Check if 'subset' is a subset of 'superset' (recursively).

    This is used to determine if a policy payload is already present in an
    existing policy, helping to avoid unnecessary updates. The function checks
    that all keys and values in subset exist in superset, while allowing superset
    to have additional keys not present in subset.

    Args:
        subset: The dictionary to check (e.g., incoming policy)
        superset: The dictionary to compare against (e.g., existing policy)

    Returns:
        True if all keys and values in subset exist in superset, False otherwise
    """
    for key, value in subset.items():
        if key not in superset:
            return False
        if isinstance(value, dict):
            if not isinstance(superset[key], dict):
                return False
            if not is_policy_subset(value, superset[key]):
                return False
        elif isinstance(value, list):
            if not isinstance(superset[key], list):
                return False
            # For lists, check if all items in subset list are present in superset list
            if not _is_subset_list(value, superset[key]):
                return False
        elif value != superset[key]:
            return False
    return True


def _is_subset_list(subset: List[Any], superset: List[Any]) -> bool:
    """
    Check if all items in 'subset' list are present in 'superset' list.

    For primitive types, checks if all items in subset exist in superset.
    For dicts, checks if each dict in subset has a matching dict in superset
    (using subset matching, not exact equality).

    Args:
        subset: The list to check (e.g., incoming policy items)
        superset: The list to compare against (e.g., existing policy items)

    Returns:
        True if all items in subset are present in superset, False otherwise
    """
    for subset_item in subset:
        found = False
        for superset_item in superset:
            if isinstance(subset_item, dict) and isinstance(superset_item, dict):
                # For dicts, check if subset_item is a subset of superset_item
                if is_policy_subset(subset_item, superset_item):
                    found = True
                    break
            elif isinstance(subset_item, list) and isinstance(superset_item, list):
                # For nested lists, recursively check
                if _is_subset_list(subset_item, superset_item):
                    found = True
                    break
            elif subset_item == superset_item:
                # For primitives, direct comparison
                found = True
                break

        if not found:
            return False

    return True


def extract_policy_params(module_instance) -> Dict[str, Any]:
    """
    Extract all policy-related parameters from a module instance into a dictionary.

    This utility function standardizes parameter extraction for RangerPolicy operations,
    making it reusable across different modules that work with Ranger policies.

    Args:
        module_instance: An Ansible module instance with policy-related parameters.

    Returns:
        Dictionary mapping parameter names to their values from the module instance.
    """
    return {
        "name": getattr(module_instance, "name", None),
        "service": getattr(module_instance, "service", None),
        "service_type": getattr(module_instance, "service_type", None),
        "description": getattr(module_instance, "description", None),
        "policy_type": getattr(module_instance, "policy_type", None),
        "policy_priority": getattr(module_instance, "policy_priority", None),
        "is_enabled": getattr(module_instance, "is_enabled", None),
        "is_audit_enabled": getattr(module_instance, "is_audit_enabled", None),
        "is_deny_all_else": getattr(module_instance, "is_deny_all_else", None),
        "zone_name": getattr(module_instance, "zone_name", None),
        "resources": getattr(module_instance, "resources", None),
        "additional_resources": getattr(module_instance, "additional_resources", None),
        "conditions": getattr(module_instance, "conditions", None),
        "policy_items": getattr(module_instance, "policy_items", None),
        "deny_policy_items": getattr(module_instance, "deny_policy_items", None),
        "allow_exceptions": getattr(module_instance, "allow_exceptions", None),
        "deny_exceptions": getattr(module_instance, "deny_exceptions", None),
        "data_mask_policy_items": getattr(
            module_instance,
            "data_mask_policy_items",
            None,
        ),
        "row_filter_policy_items": getattr(
            module_instance,
            "row_filter_policy_items",
            None,
        ),
        "validity_schedules": getattr(module_instance, "validity_schedules", None),
        "policy_labels": getattr(module_instance, "policy_labels", None),
        "options": getattr(module_instance, "options", None),
    }


def build_policy_from_params(
    params: Dict[str, Any],
    existing: Optional[RangerPolicy] = None,
    none_as_nullable: bool = True,
) -> RangerPolicy:
    """
    Build a RangerPolicy object from module parameters.

    This helper streamlines policy creation by handling the repetitive None checks
    and conditional logic for each field.

    Args:
        params: Dictionary of policy parameters (typically from module.params)
        existing: Optional existing policy to use as fallback (for updates)
        none_as_nullable: If True, None values become NULLABLE (for create/merge).
                         If False, None values use existing policy values (for replace).

    Returns:
        A RangerPolicy object with all fields populated according to the mode.
    """

    def _get_value(key: str, default=NULLABLE):
        """Get parameter value with appropriate fallback."""
        value = params.get(key)
        if value is not None:
            return value
        if none_as_nullable:
            return default
        if existing is not None:
            return getattr(existing, key, default)
        return default

    # Build policy with read-only fields from existing (if provided)
    policy_kwargs = {
        "name": _get_value("name"),
        "service": _get_value("service"),
        "service_type": _get_value("service_type"),
        "description": _get_value("description"),
        "policy_type": _get_value("policy_type"),
        "policy_priority": _get_value("policy_priority"),
        "is_enabled": _get_value("is_enabled"),
        "is_audit_enabled": _get_value("is_audit_enabled"),
        "is_deny_all_else": _get_value("is_deny_all_else"),
        "zone_name": _get_value("zone_name"),
        "resources": _get_value("resources"),
        "additional_resources": _get_value("additional_resources"),
        "conditions": _get_value("conditions"),
        "policy_items": _get_value("policy_items"),
        "deny_policy_items": _get_value("deny_policy_items"),
        "allow_exceptions": _get_value("allow_exceptions"),
        "deny_exceptions": _get_value("deny_exceptions"),
        "data_mask_policy_items": _get_value("data_mask_policy_items"),
        "row_filter_policy_items": _get_value("row_filter_policy_items"),
        "validity_schedules": _get_value("validity_schedules"),
        "policy_labels": _get_value("policy_labels"),
        "options": _get_value("options"),
    }

    # Preserve read-only fields from existing policy if provided
    if existing is not None:
        policy_kwargs.update(
            {
                "id": existing.id,
                "guid": existing.guid,
                "version": existing.version,
                "resource_signature": existing.resource_signature,
            },
        )

    return RangerPolicy(**policy_kwargs)


def merge_policies(existing: RangerPolicy, incoming: RangerPolicy) -> RangerPolicy:
    """
    Merge an incoming policy with an existing policy.

    Uses ansible.utils dict_merge logic for non-list fields, and manually handles
    list fields to avoid dict sorting issues. Then consolidates duplicate policy items
    by merging users/groups/roles for items with matching access permissions.

    Args:
        existing: The existing RangerPolicy from Ranger
        incoming: The new RangerPolicy with desired changes

    Returns:
        A new RangerPolicy with merged values
    """
    existing_dict = to_dict(existing)
    incoming_dict = to_dict(incoming)

    # List of policy item fields that need special handling
    policy_list_fields = [
        "policy_items",
        "deny_policy_items",
        "allow_exceptions",
        "deny_exceptions",
        "data_mask_policy_items",
        "row_filter_policy_items",
    ]

    # Separate list fields from the rest to avoid dict sorting issues
    existing_lists = {}
    incoming_lists = {}

    for field in policy_list_fields:
        if field in existing_dict:
            existing_lists[field] = existing_dict.pop(field)
        if field in incoming_dict:
            incoming_lists[field] = incoming_dict.pop(field)

    # Use ansible.utils dict_merge for non-list fields (scalars, dicts, simple lists)
    merged_dict = dict_merge(existing_dict, incoming_dict)

    # Manually merge policy item lists by appending incoming to existing
    for field in policy_list_fields:
        existing_items = existing_lists.get(field, [])
        incoming_items = incoming_lists.get(field, [])

        if incoming_items:
            # Append incoming items to existing items
            merged_dict[field] = existing_items + incoming_items
        elif existing_items:
            # No incoming items, keep existing
            merged_dict[field] = existing_items

    # Consolidate policy items: merge items with same accesses into one item
    for field in policy_list_fields:
        if field in merged_dict and merged_dict[field]:
            merged_dict[field] = _consolidate_policy_items(merged_dict[field])

    return from_dict(RangerPolicy, merged_dict)


def _consolidate_policy_items(items: List[Dict]) -> List[Dict]:
    """
    Consolidate policy items: merge users/groups/roles for items with matching accesses.

    Args:
        items: List of policy item dicts (may contain duplicates from merge_hash)

    Returns:
        List with duplicates consolidated into single items
    """
    if not items:
        return items

    consolidated = {}

    for item in items:
        # Create signature from accesses (sorted for consistency)
        accesses = item.get("accesses", [])
        key = str(
            sorted([(a.get("type"), a.get("is_allowed", True)) for a in accesses]),
        )

        if key not in consolidated:
            # First time seeing this access pattern - store it
            consolidated[key] = item.copy()
        else:
            # Already have this access pattern - merge users/groups/roles/conditions
            for field in ["users", "groups", "roles", "conditions"]:
                if field in item and item[field]:
                    if field in consolidated[key] and consolidated[key][field]:
                        consolidated[key][field] += item[field]
                    else:
                        consolidated[key][field] = item[field]

    return list(consolidated.values())

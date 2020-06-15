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

from dataclasses import dataclass
from typing import List, Optional, Union

from ansible_collections.cloudera.services.plugins.module_utils.common import (
    from_dict,
    to_dict,
    diff_dict,
    NULLABLE,
)


@dataclass
class SimpleClass:
    name: str
    age: int


@dataclass
class OptionalFieldsClass:
    name: str
    description: Optional[str] = None
    count: Optional[int] = None


@dataclass
class NullableFieldsClass:
    name: str
    description: Union[str, None, NULLABLE] = NULLABLE
    count: Union[int, None, NULLABLE] = NULLABLE


@dataclass
class NestedCredential:
    username: str
    password: str


@dataclass
class NestedConfig:
    type: str
    url: str
    credential: Optional[NestedCredential] = None


@dataclass
class ParentClass:
    name: str
    config: Optional[NestedConfig] = None


@dataclass
class ListFieldsClass:
    name: str
    tags: List[str]


@dataclass
class NestedListClass:
    name: str
    configs: List[NestedConfig]


def test_from_dict_simple():
    """Test from_dict with simple dataclass."""
    data = {"name": "Alice", "age": 30}
    result = from_dict(SimpleClass, data)
    assert result.name == "Alice"
    assert result.age == 30


def test_from_dict_with_none():
    """Test from_dict with None value."""
    result = from_dict(SimpleClass, None)
    assert result is None


def test_from_dict_optional_fields():
    """Test from_dict with optional fields."""
    data = {"name": "Alice", "description": "Test user"}
    result = from_dict(OptionalFieldsClass, data)
    assert result.name == "Alice"
    assert result.description == "Test user"
    assert result.count is None


def test_from_dict_nested():
    """Test from_dict with nested dataclasses."""
    data = {
        "name": "Project",
        "config": {
            "type": "git",
            "url": "https://github.com/example/repo",
            "credential": {
                "username": "user",
                "password": "pass",
            },
        },
    }
    result: ParentClass = from_dict(ParentClass, data)
    assert result.name == "Project"
    assert result.config is not None
    assert result.config.type == "git"
    assert result.config.url == "https://github.com/example/repo"
    assert result.config.credential is not None
    assert result.config.credential.username == "user"
    assert result.config.credential.password == "pass"


def test_from_dict_nested_none():
    """Test from_dict with nested dataclass set to None."""
    data = {"name": "Project", "config": None}
    result: ParentClass = from_dict(ParentClass, data)
    assert result.name == "Project"
    assert result.config is None


def test_from_dict_list_primitives():
    """Test from_dict with list of primitives."""
    data = {"name": "Project", "tags": ["tag1", "tag2", "tag3"]}
    result: ListFieldsClass = from_dict(ListFieldsClass, data)
    assert result.name == "Project"
    assert result.tags == ["tag1", "tag2", "tag3"]


def test_from_dict_list_dataclasses():
    """Test from_dict with list of dataclasses."""
    data = {
        "name": "Project",
        "configs": [
            {"type": "git", "url": "https://github.com/example/repo1"},
            {"type": "svn", "url": "https://svn.example.com/repo2"},
        ],
    }
    result: NestedListClass = from_dict(NestedListClass, data)
    assert result.name == "Project"
    assert len(result.configs) == 2
    assert result.configs[0].type == "git"
    assert result.configs[1].type == "svn"


def test_from_dict_empty_list():
    """Test from_dict with empty list."""
    data = {"name": "Project", "tags": []}
    result: ListFieldsClass = from_dict(ListFieldsClass, data)
    assert result.name == "Project"
    assert result.tags == []


def test_from_dict_extra_fields_ignored():
    """Test from_dict ignores extra fields not in dataclass."""
    data = {"name": "Alice", "age": 30, "extra_field": "ignored"}
    result: SimpleClass = from_dict(SimpleClass, data)
    assert result.name == "Alice"
    assert result.age == 30
    assert not hasattr(result, "extra_field")


# Tests for to_dict()
def test_to_dict_simple():
    """Test to_dict with simple dataclass."""
    instance = SimpleClass(name="Alice", age=30)
    result = to_dict(instance)
    assert result == {"name": "Alice", "age": 30}


def test_to_dict_with_none():
    """Test to_dict with None values."""
    instance = OptionalFieldsClass(name="Alice", description=None, count=None)
    result = to_dict(instance)
    assert result == {"name": "Alice", "description": None, "count": None}


def test_to_dict_with_nullable():
    """Test to_dict filters out NULLABLE sentinel values."""
    instance = NullableFieldsClass(name="Alice", description=NULLABLE, count=NULLABLE)
    result = to_dict(instance)
    assert result == {"name": "Alice"}
    assert "description" not in result
    assert "count" not in result


def test_to_dict_nullable_vs_none():
    """Test to_dict distinguishes between NULLABLE and None."""
    instance = NullableFieldsClass(name="Alice", description=None, count=NULLABLE)
    result = to_dict(instance)
    assert result == {"name": "Alice", "description": None}
    assert "count" not in result


def test_to_dict_nested():
    """Test to_dict with nested dataclasses."""
    instance = ParentClass(
        name="Project",
        config=NestedConfig(
            type="git",
            url="https://github.com/example/repo",
            credential=NestedCredential(username="user", password="pass"),
        ),
    )
    result = to_dict(instance)
    assert result["name"] == "Project"
    assert result["config"]["type"] == "git"
    assert result["config"]["credential"]["username"] == "user"


def test_to_dict_list_primitives():
    """Test to_dict with list of primitives."""
    instance = ListFieldsClass(name="Project", tags=["tag1", "tag2"])
    result = to_dict(instance)
    assert result == {"name": "Project", "tags": ["tag1", "tag2"]}


def test_to_dict_list_dataclasses():
    """Test to_dict with list of dataclasses."""
    instance = NestedListClass(
        name="Project",
        configs=[
            NestedConfig(type="git", url="https://github.com/example/repo"),
            NestedConfig(type="svn", url="https://svn.example.com/repo"),
        ],
    )
    result = to_dict(instance)
    assert result["name"] == "Project"
    assert len(result["configs"]) == 2
    assert result["configs"][0]["type"] == "git"


def test_to_dict_not_dataclass():
    """Test to_dict raises TypeError for non-dataclass."""
    with pytest.raises(TypeError, match="Expected dataclass type"):
        to_dict("not a dataclass")


def test_to_dict_dataclass_type():
    """Test to_dict raises TypeError for dataclass type instead of instance."""
    with pytest.raises(TypeError, match="Expected dataclass type"):
        to_dict(SimpleClass)


# Tests for diff_dict()
def test_diff_dict_no_differences():
    """Test diff_dict with identical instances."""
    old = SimpleClass(name="Alice", age=30)
    new = SimpleClass(name="Alice", age=30)
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {}
    assert new_diff == {}


def test_diff_dict_simple_change():
    """Test diff_dict with simple field change."""
    old = SimpleClass(name="Alice", age=30)
    new = SimpleClass(name="Alice", age=31)
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"age": 30}
    assert new_diff == {"age": 31}


def test_diff_dict_multiple_changes():
    """Test diff_dict with multiple field changes."""
    old = SimpleClass(name="Alice", age=30)
    new = SimpleClass(name="Bob", age=31)
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"name": "Alice", "age": 30}
    assert new_diff == {"name": "Bob", "age": 31}


def test_diff_dict_none_to_value():
    """Test diff_dict changing from None to a value."""
    old = OptionalFieldsClass(name="Alice", description=None)
    new = OptionalFieldsClass(name="Alice", description="New description")
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"description": None}
    assert new_diff == {"description": "New description"}


def test_diff_dict_value_to_none():
    """Test diff_dict changing from value to None."""
    old = OptionalFieldsClass(name="Alice", description="Old description")
    new = OptionalFieldsClass(name="Alice", description=None)
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"description": "Old description"}
    assert new_diff == {"description": None}


def test_diff_dict_nullable_both():
    """Test diff_dict with NULLABLE on both sides (no diff)."""
    old = NullableFieldsClass(name="Alice", description=NULLABLE)
    new = NullableFieldsClass(name="Alice", description=NULLABLE)
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {}
    assert new_diff == {}


def test_diff_dict_nullable_to_value():
    """Test diff_dict changing from NULLABLE to a value."""
    old = NullableFieldsClass(name="Alice", description=NULLABLE)
    new = NullableFieldsClass(name="Alice", description="New description")
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"description": None}  # NULLABLE treated as None
    assert new_diff == {"description": "New description"}


def test_diff_dict_nullable_filter_off():
    """Test diff_dict with filter_nullable=False."""
    old = NullableFieldsClass(name="Alice", description=NULLABLE)
    new = NullableFieldsClass(name="Alice", description="New description")
    old_diff, new_diff = diff_dict(old, new, filter_nullable=False)
    assert old_diff == {"description": NULLABLE}
    assert new_diff == {"description": "New description"}


def test_diff_dict_nested_no_change():
    """Test diff_dict with nested dataclasses, no changes."""
    old = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo"),
    )
    new = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo"),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {}
    assert new_diff == {}


def test_diff_dict_nested_change():
    """Test diff_dict with nested dataclass changes."""
    old = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo1"),
    )
    new = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo2"),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"config": {"url": "https://github.com/example/repo1"}}
    assert new_diff == {"config": {"url": "https://github.com/example/repo2"}}


def test_diff_dict_nested_deep_change():
    """Test diff_dict with deeply nested dataclass changes."""
    old = ParentClass(
        name="Project",
        config=NestedConfig(
            type="git",
            url="https://github.com/example/repo",
            credential=NestedCredential(username="user", password="pass1"),
        ),
    )
    new = ParentClass(
        name="Project",
        config=NestedConfig(
            type="git",
            url="https://github.com/example/repo",
            credential=NestedCredential(username="user", password="pass2"),
        ),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"config": {"credential": {"password": "pass1"}}}
    assert new_diff == {"config": {"credential": {"password": "pass2"}}}


def test_diff_dict_nested_none_to_value():
    """Test diff_dict with nested dataclass changing from None to value."""
    old = ParentClass(name="Project", config=None)
    new = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo"),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"config": None}
    assert new_diff == {
        "config": {
            "credential": None,
            "type": "git",
            "url": "https://github.com/example/repo",
        },
    }


def test_diff_dict_nested_value_to_none():
    """Test diff_dict with nested dataclass changing from value to None."""
    old = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo"),
    )
    new = ParentClass(name="Project", config=None)
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {
        "config": {
            "credential": None,
            "type": "git",
            "url": "https://github.com/example/repo",
        },
    }
    assert new_diff == {"config": None}


def test_diff_dict_nested_multiple_fields():
    """Test diff_dict with multiple fields changing in nested dataclass."""
    old = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo1"),
    )
    new = ParentClass(
        name="Project",
        config=NestedConfig(type="svn", url="https://github.com/example/repo2"),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {
        "config": {
            "type": "git",
            "url": "https://github.com/example/repo1",
        },
    }
    assert new_diff == {
        "config": {
            "type": "svn",
            "url": "https://github.com/example/repo2",
        },
    }


def test_diff_dict_nested_credential_added():
    """Test diff_dict with nested credential being added."""
    old = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo"),
    )
    new = ParentClass(
        name="Project",
        config=NestedConfig(
            type="git",
            url="https://github.com/example/repo",
            credential=NestedCredential(username="user", password="pass"),
        ),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"config": {"credential": None}}
    assert new_diff == {
        "config": {
            "credential": {
                "username": "user",
                "password": "pass",
            },
        },
    }


def test_diff_dict_nested_credential_removed():
    """Test diff_dict with nested credential being removed."""
    old = ParentClass(
        name="Project",
        config=NestedConfig(
            type="git",
            url="https://github.com/example/repo",
            credential=NestedCredential(username="user", password="pass"),
        ),
    )
    new = ParentClass(
        name="Project",
        config=NestedConfig(type="git", url="https://github.com/example/repo"),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {
        "config": {
            "credential": {
                "username": "user",
                "password": "pass",
            },
        },
    }
    assert new_diff == {"config": {"credential": None}}


def test_diff_dict_nested_multi_level_change():
    """Test diff_dict with changes at multiple nesting levels."""
    old = ParentClass(
        name="Project1",
        config=NestedConfig(
            type="git",
            url="https://github.com/example/repo1",
            credential=NestedCredential(username="user1", password="pass1"),
        ),
    )
    new = ParentClass(
        name="Project2",
        config=NestedConfig(
            type="svn",
            url="https://github.com/example/repo2",
            credential=NestedCredential(username="user2", password="pass2"),
        ),
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff["name"] == "Project1"
    assert old_diff["config"]["type"] == "git"
    assert old_diff["config"]["url"] == "https://github.com/example/repo1"
    assert old_diff["config"]["credential"]["username"] == "user1"
    assert old_diff["config"]["credential"]["password"] == "pass1"
    assert new_diff["name"] == "Project2"
    assert new_diff["config"]["type"] == "svn"
    assert new_diff["config"]["url"] == "https://github.com/example/repo2"
    assert new_diff["config"]["credential"]["username"] == "user2"
    assert new_diff["config"]["credential"]["password"] == "pass2"


def test_diff_dict_list_no_change():
    """Test diff_dict with list fields, no changes."""
    old = ListFieldsClass(name="Project", tags=["tag1", "tag2"])
    new = ListFieldsClass(name="Project", tags=["tag1", "tag2"])
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {}
    assert new_diff == {}


def test_diff_dict_list_item_change():
    """Test diff_dict with list item changes."""
    old = ListFieldsClass(name="Project", tags=["tag1", "tag2"])
    new = ListFieldsClass(name="Project", tags=["tag1", "tag3"])
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"tags": ["tag1", "tag2"]}
    assert new_diff == {"tags": ["tag1", "tag3"]}


def test_diff_dict_list_length_change():
    """Test diff_dict with list length changes."""
    old = ListFieldsClass(name="Project", tags=["tag1", "tag2"])
    new = ListFieldsClass(name="Project", tags=["tag1"])
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff == {"tags": ["tag1", "tag2"]}
    assert new_diff == {"tags": ["tag1"]}


def test_diff_dict_list_dataclasses_change():
    """Test diff_dict with list of dataclasses changes."""
    old = NestedListClass(
        name="Project",
        configs=[
            NestedConfig(type="git", url="https://github.com/example/repo1"),
            NestedConfig(type="svn", url="https://svn.example.com/repo"),
        ],
    )
    new = NestedListClass(
        name="Project",
        configs=[
            NestedConfig(type="git", url="https://github.com/example/repo2"),
            NestedConfig(type="svn", url="https://svn.example.com/repo"),
        ],
    )
    old_diff, new_diff = diff_dict(old, new)
    assert old_diff["configs"][0]["url"] == "https://github.com/example/repo1"
    assert new_diff["configs"][0]["url"] == "https://github.com/example/repo2"


def test_diff_dict_not_dataclass_prev():
    """Test diff_dict raises TypeError for non-dataclass prev."""
    new = SimpleClass(name="Alice", age=30)
    with pytest.raises(TypeError, match="Expected dataclass instance for prev"):
        diff_dict("not a dataclass", new)


def test_diff_dict_not_dataclass_next():
    """Test diff_dict raises TypeError for non-dataclass next."""
    old = SimpleClass(name="Alice", age=30)
    with pytest.raises(TypeError, match="Expected dataclass instance for next"):
        diff_dict(old, "not a dataclass")


def test_diff_dict_dataclass_type_prev():
    """Test diff_dict raises TypeError for dataclass type instead of instance (prev)."""
    new = SimpleClass(name="Alice", age=30)
    with pytest.raises(TypeError, match="Expected dataclass instance for prev"):
        diff_dict(SimpleClass, new)


def test_diff_dict_dataclass_type_next():
    """Test diff_dict raises TypeError for dataclass type instead of instance (next)."""
    old = SimpleClass(name="Alice", age=30)
    with pytest.raises(TypeError, match="Expected dataclass instance for next"):
        diff_dict(old, SimpleClass)


def test_diff_dict_different_types():
    """Test diff_dict raises TypeError for different dataclass types."""
    old = SimpleClass(name="Alice", age=30)
    new = OptionalFieldsClass(name="Alice")
    with pytest.raises(TypeError, match="Cannot compare different dataclass types"):
        diff_dict(old, new)


def test_roundtrip_simple():
    """Test roundtrip from_dict -> to_dict."""
    data = {"name": "Alice", "age": 30}
    instance = from_dict(SimpleClass, data)
    result = to_dict(instance)
    assert result == data


def test_roundtrip_nested():
    """Test roundtrip from_dict -> to_dict with nested structures."""
    data = {
        "name": "Project",
        "config": {
            "type": "git",
            "url": "https://github.com/example/repo",
            "credential": {
                "username": "user",
                "password": "pass",
            },
        },
    }
    instance = from_dict(ParentClass, data)
    result = to_dict(instance)
    assert result == data


def test_roundtrip_with_diff():
    """Test roundtrip with diff detection."""
    data1 = {"name": "Alice", "age": 30}
    data2 = {"name": "Alice", "age": 31}

    old = from_dict(SimpleClass, data1)
    new = from_dict(SimpleClass, data2)

    old_diff, new_diff = diff_dict(old, new)

    assert old_diff == {"age": 30}
    assert new_diff == {"age": 31}

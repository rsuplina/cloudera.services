import pytest
from ansible_collections.cloudera.services.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger_role
from apache_ranger.model.ranger_role import RangerRole


def test_ranger_role_create_basic_role(conn, module_args, role_teardown):

    name = "role_test_07"
    service = "cm_hdfs"

    role_teardown(name)

    module_args(
        {
            **conn,
            "name": name,
            "service": service,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_role.main()

    assert e.value.role["name"] == name
    assert e.value.changed == True

    with pytest.raises(AnsibleExitJson) as e:
        ranger_role.main()

    assert e.value.changed == True


def test_ranger_role_update_role(conn, module_args, role_factory):

    new_description = "Updated with Ansible"

    first_role = role_factory(
        role=RangerRole(
            attrs={
                "name": "test_role_09",
                "description": "test",
                "users": [
                    {"name": "nifi", "is_admin": False},
                ],
                "groups": [
                    {"name": "bin", "is_admin": True},
                ],
            },
        ),
    )
    module_args(
        {
            **conn,
            "name": "test_role_09",
            "description": new_description,
            "users": [
                {"name": "nifi", "is_admin": False},
                {"name": "admin", "is_admin": True},
                {"name": "knox", "is_admin": False},
            ],
            "groups": [
                {"name": "bin", "is_admin": True},
                {"name": "atlas", "is_admin": False},
                {"name": "public", "is_admin": False},
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_role.main()
    assert e.value.changed == True
    assert e.value.role["name"] == first_role.name
    assert e.value.role["description"] == new_description
    assert "users" in e.value.role
    assert len(e.value.role["users"]) == 3
    assert "groups" in e.value.role
    assert len(e.value.role["groups"]) == 3
    with pytest.raises(AnsibleExitJson) as e:
        ranger_role.main()
    assert e.value.changed == True


def test_ranger_role_delete_role(conn, module_args, role_wihtout_teardown):

    minimal_role = role_wihtout_teardown(
        role=RangerRole(
            attrs={
                "name": "role_test_08",
            },
        ),
    )

    module_args(
        {
            **conn,
            "name": minimal_role.name,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_role.main()
    assert e.value.changed == True

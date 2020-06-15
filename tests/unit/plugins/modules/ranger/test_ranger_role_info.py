import pytest
from ansible_collections.cloudera.services.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger_role_info
from apache_ranger.model.ranger_role import RangerRole


def test_ranger_role_info_get_role_by_id(conn, module_args, role_factory):

    minimal_role = role_factory(
        role=RangerRole(
            attrs={
                "name": "Test_role_1",
            },
        ),
    )

    module_args(
        {
            **conn,
            "id": minimal_role.id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_role_info.main()
    assert e.value.roles[0]["name"] == minimal_role.name
    assert e.value.roles[0]["id"] == minimal_role.id


def test_ranger_role_info_get_role_by_name(conn, module_args, role_factory):

    minimal_role = role_factory(
        role=RangerRole(
            attrs={
                "name": "Test_role_2",
                "users": [{"name": "admin", "isAdmin": "true"}],
                "groups": [{"name": "kafka", "isAdmin": "false"}],
            },
        ),
    )

    module_args(
        {
            **conn,
            "name": minimal_role.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_role_info.main()

    assert e.value.roles[0]["name"] == minimal_role.name
    assert e.value.roles[0]["id"] == minimal_role.id
    assert e.value.roles[0]["users"][0]["name"] == minimal_role.users[0]["name"]
    assert e.value.roles[0]["users"][0].get("is_admin") == minimal_role.users[0].get(
        "isAdmin",
    )


def test_ranger_role_info_get_all_roles(conn, module_args, role_factory):

    first_role = role_factory(
        role=RangerRole(
            attrs={
                "name": "Test_role_3",
            },
        ),
    )
    second_role = role_factory(
        role=RangerRole(
            attrs={
                "name": "Test_role_4",
            },
        ),
    )

    module_args(
        {
            **conn,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_role_info.main()

    returned_role_names = {role["name"] for role in e.value.roles}
    assert first_role.name in returned_role_names
    assert second_role.name in returned_role_names

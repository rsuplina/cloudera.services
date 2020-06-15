import pytest
from ansible_collections.cloudera.services.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger_service
from apache_ranger.model.ranger_service import RangerService


def test_ranger_service_create_service(conn, module_args, service_teardown):

    name = "test02"
    type = "hdfs"

    service_teardown(name)

    module_args(
        {
            **conn,
            "name": name,
            "type": type,
            "configs": {
                "username": "hdfs",
                "password": "hdfs",
                "fs.default.name": "hdfs://namenode:8020",
                "hadoop.security.authentication": "simple",
                "hadoop.security.authorization": "true",
                "ranger.plugin.audit.filters": "[{'resources':{'path':{'values':['/test'],'isRecursive':true } },'accessResult':'ALLOWED','accessTypes':['read'],'users':['admin'],'isAudited':true}]",
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()
    assert e.value.service["name"] == name
    assert e.value.service["type"] == type
    assert e.value.service["configs"]["username"] == "hdfs"
    assert e.value.changed == True


def test_ranger_service_delete_service(conn, module_args, service_wihtout_teardown):

    minimal_service = service_wihtout_teardown(
        service=RangerService(
            attrs={
                "name": "test02",
                "type": "hdfs",
                "configs": {
                    "username": "hdfs",
                    "password": "hdfs",
                    "fs.default.name": "hdfs://namenode:8020",
                    "hadoop.security.authentication": "simple",
                    "hadoop.security.authorization": "true",
                },
            },
        ),
    )

    module_args(
        {
            **conn,
            "name": minimal_service.name,
            "state": "absent",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()
    assert e.value.changed == True


def test_ranger_service_update_service(conn, module_args, service_factory):

    old_description = "This is a description"
    new_description = "Updated via Ansible module"

    minimal_service = service_factory(
        service=RangerService(
            attrs={
                "name": "test03",
                "type": "hdfs",
                "description": old_description,
                "configs": {
                    "username": "hdfs",
                    "password": "hdfs",
                    "fs.default.name": "hdfs://namenode:8020",
                    "hadoop.security.authentication": "simple",
                    "hadoop.security.authorization": "true",
                },
            },
        ),
    )

    module_args(
        {
            **conn,
            "name": "test03",
            "type": "hdfs",
            "description": new_description,
            "configs": {
                "username": "hdfs",
                "password": "hdfs",
                "fs.default.name": "hdfs://namenode:8888",
                "hadoop.security.authentication": "simple",
                "hadoop.security.authorization": "true",
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()
    assert e.value.service["description"] == new_description
    assert e.value.changed == True


def test_ranger_service_update_check_audits(conn, module_args, service_factory):

    simple_audit = "[{'resources':{'path':{'values':['/test'],'isRecursive':true } },'accessResult':'ALLOWED','accessTypes':['read'],'users':['admin'],'isAudited':true}]"
    minimal_service = service_factory(
        service=RangerService(
            attrs={
                "name": "test03",
                "type": "hdfs",
                "description": "Updated via Ansible module",
                "configs": {
                    "username": "hdfs",
                    "password": "hdfs",
                    "fs.default.name": "hdfs://namenode:8020",
                    "hadoop.security.authentication": "simple",
                    "hadoop.security.authorization": "true",
                    "ranger.plugin.audit.filters": simple_audit,
                },
            },
        ),
    )

    module_args(
        {
            **conn,
            "name": "test03",
            "type": "hdfs",
            "description": "Updated via Ansible module",
            "configs": {
                "username": "hdfs",
                "password": "hdfs",
                "fs.default.name": "hdfs://namenode:8888",
                "hadoop.security.authentication": "simple",
                "hadoop.security.authorization": "true",
                "ranger.plugin.audit.filters": simple_audit,
            },
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service.main()
    assert e.value.service["configs"]["ranger.plugin.audit.filters"] == simple_audit
    assert e.value.changed == True

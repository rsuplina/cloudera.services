import pytest
from ansible_collections.cloudera.services.tests.unit import (
    AnsibleFailJson,
    AnsibleExitJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger
from apache_ranger.model.ranger_service import RangerService


def test_ranger_create_service(conn, module_args, service_teardown):

    name = "test02"
    type = "hdfs"

    service_teardown(name)
    module_args(
        {
            **conn,
            "services": [
                {
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
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger.main()
    assert e.value.services[0]["name"] == name
    assert e.value.services[0]["type"] == type
    assert e.value.services[0]["configs"]["username"] == "hdfs"
    assert e.value.changed == True


def test_ranger_create_service_with_policy(conn, module_args, service_teardown):

    name = "test02"
    type = "hdfs"
    policy_name = "test02_policy"

    service_teardown(name)

    module_args(
        {
            **conn,
            "services": [
                {
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
                    "policies": [
                        {
                            "name": policy_name,
                            "resources": {
                                "path": {
                                    "values": ["/test"],
                                },
                            },
                        },
                    ],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger.main()


def test_ranger_create_multiple_services_with_policy(
    conn,
    module_args,
    service_teardown,
):

    service_name1 = "Service1"
    service_name2 = "Service2"
    type = "hdfs"
    policy_name = "test02_policy"

    service_teardown(service_name1)
    service_teardown(service_name2)

    module_args(
        {
            **conn,
            "services": [
                {
                    "name": service_name1,
                    "type": type,
                    "configs": {
                        "username": "hdfs",
                        "password": "hdfs",
                        "fs.default.name": "hdfs://namenode:8020",
                        "hadoop.security.authentication": "simple",
                        "hadoop.security.authorization": "true",
                    },
                    "policies": [
                        {
                            "name": policy_name,
                            "resources": {
                                "path": {
                                    "values": ["/test"],
                                },
                            },
                        },
                    ],
                },
                {
                    "name": service_name2,
                    "type": type,
                    "configs": {
                        "username": "hdfs",
                        "password": "hdfs",
                        "fs.default.name": "hdfs://namenode:8020",
                        "hadoop.security.authentication": "simple",
                        "hadoop.security.authorization": "true",
                    },
                    "policies": [
                        {
                            "name": policy_name,
                            "resources": {
                                "path": {
                                    "values": ["/test2"],
                                },
                            },
                        },
                    ],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger.main()


def test_ranger_create_service_with_two_policies(conn, module_args, service_teardown):

    name = "test02"
    type = "hdfs"
    policy_name1 = "Policy1"
    policy_name2 = "Policy2"

    service_teardown(name)

    module_args(
        {
            **conn,
            "services": [
                {
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
                    "policies": [
                        {
                            "name": policy_name1,
                            "resources": {
                                "path": {
                                    "values": ["/test"],
                                },
                            },
                        },
                        {
                            "name": policy_name2,
                            "resources": {
                                "path": {
                                    "values": ["/test2"],
                                },
                            },
                        },
                    ],
                },
            ],
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger.main()

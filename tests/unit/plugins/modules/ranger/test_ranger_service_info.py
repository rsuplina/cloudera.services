import pytest
from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)
from ansible_collections.cloudera.services.plugins.modules import ranger_service_info
from apache_ranger.model.ranger_service import RangerService


def test_ranger_service_info_get_service_by_id(conn, module_args, service_factory):

    minimal_service = service_factory(
        service=RangerService(
            attrs={
                "name": "test01",
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
            "id": minimal_service.id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()
    assert e.value.services[0]["id"] == minimal_service.id


def test_ranger_service_info_get_service_by_name(conn, module_args, service_factory):

    minimal_service = service_factory(
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
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()
    assert e.value.services[0]["name"] == minimal_service.name


def test_ranger_service_info_get_all_services(conn, module_args, service_factory):

    first_service = service_factory(
        service=RangerService(
            attrs={
                "name": "test03",
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
    second_service = service_factory(
        service=RangerService(
            attrs={
                "name": "test04",
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
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ranger_service_info.main()

    returned_service_names = {service["name"] for service in e.value.services}
    assert first_service.name in returned_service_names
    assert second_service.name in returned_service_names

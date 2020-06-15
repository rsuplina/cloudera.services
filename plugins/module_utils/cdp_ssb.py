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
Ansible Modules for shared functions of the Cloudera SQL Stream Builder (SSB) service
"""

from __future__ import annotations

import base64
import io
import os
import time

import requests

from ansible_collections.cloudera.services.plugins.module_utils.cdp_rest import (
    CdpRestModule,
)

__credits__ = ["araujo@cloudera.com"]
__maintainer__ = [
    "araujo@cloudera.com",
]


class CdpSsbModule(CdpRestModule):
    """A base CDP module class for dealing with Cloudera SQL Stream Builder (SSB) REST APIs."""

    def __init__(self, module, name="ssb"):
        super(CdpSsbModule, self).__init__(module, name)

    # Private functions

    def _assert_response(self, resp, expected_codes=None, message=None):
        if not expected_codes:
            expected_codes = []
        if not message:
            message = "Call to URL {} failed.".format(resp.url)
        if resp.status_code not in expected_codes:
            # try:
            def _serialize(obj):
                if obj.__class__.__name__ == "CaseInsensitiveDict":
                    return dict(obj)
                elif isinstance(obj, bytes):
                    return obj.decode("utf-8")
                else:
                    return obj

            import json

            serialized_request = json.dumps(
                dict(
                    [
                        (k, _serialize(getattr(resp.request, k)))
                        for k in dir(resp.request)
                        if not k.startswith("_")
                        and not callable(getattr(resp.request, k))
                    ],
                ),
            )
            # except:
            #     serialized_request =resp.request
            self.module.fail_json(
                msg="{} Return Code: {}, Response: {}, Request: {}".format(
                    message,
                    resp.status_code,
                    resp.text,
                    serialized_request,
                ),
            )

    def _get_user(self):
        resp = self._get("/api/v1/user")
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to retrieve user info.",
        )
        return resp.json()

    def _get_user_id(self):
        return self._get_user()["id"]

    def _get_active_project_id(self):
        return self._get_user()["project_id"]

    def _get_active_project(self):
        project_id = self._get_active_project_id()
        resp = self._get("/api/v1/projects/{}".format(project_id))
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to retrieve project with id [{}].".format(project_id),
        )
        return resp.json()

    def _get_active_project_name(self):
        return self._get_active_project()["name"]

    def _get_projects(self, project=None):
        resp = self._get(
            "/api/v1/project-permissions?user_id={}".format(self._get_user_id()),
        )
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to retrieve project info.",
        )
        permissions = resp.json()
        return [
            p["project"]
            for p in permissions["project_permissions"]
            if project is None
            or p["project"]["name"] == project
            or p["project"]["id"] == project
        ]

    def _upload_keytab(self, principal, keytab_file=None, keytab_base64_data=None):
        assert keytab_file is None or keytab_base64_data is None
        assert keytab_file is not None or keytab_base64_data is not None

        if keytab_base64_data:
            stream = io.BytesIO(base64.standard_b64decode(keytab_base64_data))
        else:
            if keytab_file is None:
                self.module.fail_json(
                    msg="Keytab file must be provided when keytab_base64_data is not set.",
                )
            if not os.path.exists(keytab_file):
                self.module.fail_json(
                    msg="Keytab file {} does not exist.".format(keytab_file),
                )

            stream = open(keytab_file, "rb")

        files = {"file": (principal + ".keytab", stream, "application/octet-stream")}
        resp = self._post(
            "/api/v1/user/keytab/upload",
            data={"principal": principal},
            files=files,
        )
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to upload keytab for principal [{}].".format(principal),
        )

    def _generate_keytab(self, principal, password):
        resp = self._post(
            "/api/v2/user/keytab/generate",
            json={"principal": principal, "password": password},
        )
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to generate keytab for principal [{}].".format(principal),
        )

    def _delete_keytab(self, principal):
        resp = self._delete("/api/v1/user/keytab", data={"principal": principal})
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to delete keytab for principal [{}].".format(principal),
        )


class CdpSsbProjectEntityModule(CdpSsbModule):
    """A base CDP module class for dealing with project-related Cloudera SQL Stream Builder (SSB) REST APIs."""

    def __init__(self, module):
        super(CdpSsbProjectEntityModule, self).__init__(module)

        self.project = self._get_param("project")

    @staticmethod
    def module_spec(**spec):
        """Default Ansible Module spec values"""
        return CdpSsbProjectEntityModule.merge_specs(
            super(CdpSsbProjectEntityModule, CdpSsbProjectEntityModule).module_spec(),
            dict(
                argument_spec=dict(
                    project=dict(required=True, type="str"),
                ),
            ),
            spec,
        )

    # Private functions

    def _switch_to_project(self):
        projects = self._get_projects(self.project)
        if not projects:
            self.module.fail_json(msg="Cannot access project [{}]".format(self.project))
        resp = self._patch(
            "/api/v1/user/project",
            json={"project_id": projects[0]["id"]},
        )
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to switch to project [{}]].".format(self.project),
        )

    def _get_data_sources(self, data_source_name=None, data_source_type=None):
        self._switch_to_project()
        resp = self._get("/api/v1/data-sources")
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to retrieve data sources from project [{}].".format(
                self.project,
            ),
        )
        sources = resp.json()
        return [
            p
            for p in sources
            if (data_source_name is None or p["name"] == data_source_name)
            and (data_source_type is None or p["type"] == data_source_type)
        ]

    def _create_data_source(self, data):
        self._switch_to_project()
        resp = self._post("/api/v1/data-sources", json=data)
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to create data source [{}] in project [{}].".format(
                data,
                self.project,
            ),
        )
        return resp.json()

    def _delete_data_source(self, data_source_name=None, data_source_id=None):
        assert data_source_name is None or data_source_id is None
        assert data_source_name is not None or data_source_id is not None
        if data_source_id is None:
            data_sources = self._get_data_sources(data_source_name=data_source_name)
            if not data_sources:
                return
            data_source_id = data_sources[0]["id"]
        self._switch_to_project()
        resp = self._delete("/api/v1/data-sources/{}".format(data_source_id))
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to delete data source [{}] from project [{}].".format(
                data_source_name or data_source_id,
                self.project,
            ),
        )

    def _get_udfs(self, udf_name=None):
        self._switch_to_project()
        resp = self._get("/api/v1/udfs")
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to retrieve UDFs from project [{}].".format(
                self.project,
            ),
        )
        udfs = resp.json()
        return [u for u in udfs if (udf_name is None or u["name"] == udf_name)]

    def _delete_udf(self, udf_name=None, udf_id=None):
        assert udf_name is None or udf_id is None
        assert udf_name is not None or udf_id is not None
        if udf_id is None:
            udfs = self._get_udfs(udf_name=udf_name)
            if not udfs:
                return
            udf_id = udfs[0]["id"]
        self._switch_to_project()
        resp = self._delete("/api/v1/udfs/{}".format(udf_id))
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to delete function [{}] from project [{}]".format(
                udf_name or udf_id,
                self.project,
            ),
        )

    def _create_udf(
        self,
        name,
        language,
        code,
        output_type,
        input_types,
        description=None,
    ):
        data = {
            "name": name,
            "description": description,
            "language": language,
            "code": code,
            "output_type": output_type,
            "input_types": input_types,
        }
        self._switch_to_project()
        resp = self._post("/api/v1/udfs", json=data)
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to create function [{}] in project [{}]. Error code: {}, Output: {}".format(
                name,
                self.project,
                resp.status_code,
                resp.text,
            ),
        )
        return resp.json()

    def _get_jobs(self, job_name=None, job_id=None):
        assert (
            job_name is None or job_id is None
        ), "job_name and job_id are mutually-exclusive parameters"
        assert (
            job_name is not None or job_id is not None
        ), "One of job_name and job_id must be specified"
        self._switch_to_project()
        resp = self._get("/api/v1/jobs")
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to retrieve jobs from project [{}]".format(self.project),
        )
        jobs = [
            j
            for j in resp.json()["jobs"]
            if (job_name is None or job_name == j["name"])
            and (job_id is None or job_id == j["job_id"])
        ]
        if job_name or job_id:
            if jobs:
                if len(jobs) > 1:
                    self.module.fail_json(
                        "More than 1 job in project [{}] matches the criteria "
                        "[job_name={} or job_id={}].".format(
                            self.project,
                            job_name,
                            job_id,
                        ),
                    )
                else:
                    return jobs[0]
            else:
                return None
        else:
            return jobs

    def _create_job(
        self,
        job_name=None,
        job_id=None,
        sql=None,
        runtime_config=None,
        checkpoint_config=None,
        mv_endpoints=None,
        mv_config=None,
        execute_in_session=None,
        add_to_history=None,
    ):
        existing_job = self._get_jobs(job_name=job_name, job_id=job_id)
        if not existing_job:
            if not job_name:
                self.module.fail_json("Job must have a name. job_name is null.")
            data = {
                "selection": False,
                "job_config": {
                    "job_name": job_name,
                },
            }
        else:
            data = {
                "selection": False,
                "job_config": {
                    "job_name": existing_job["name"],  # type: ignore
                    "mv_endpoints": existing_job["mv_endpoints"],  # type: ignore
                    "mv_config": existing_job["mv_config"],  # type: ignore
                    "checkpoint_config": existing_job["checkpoint_config"],  # type: ignore
                    "runtime_config": existing_job["runtime_config"],  # type: ignore
                },
            }
            if not data["job_config"]["mv_config"]["name"]:
                data["job_config"]["mv_config"]["name"] = existing_job["name"]  # type: ignore

        if execute_in_session is not None:
            data["execute_in_session"] = execute_in_session
        if add_to_history is not None:
            data["add_to_history"] = execute_in_session

        if sql:
            data["sql"] = sql
        if runtime_config:
            data["job_config"]["runtime_config"] = runtime_config
        if checkpoint_config:
            data["job_config"]["checkpoint_config"] = checkpoint_config
        if mv_config:
            data["job_config"]["mv_config"] = mv_config.copy()
            if (
                "name" not in data["job_config"]["mv_config"]
                or not data["job_config"]["mv_config"]["name"]
            ):
                data["job_config"]["mv_config"]["name"] = data["job_config"]["job_name"]
        if mv_endpoints:
            data["mv_endpoints"] = mv_endpoints

        self._switch_to_project()
        resp = self._post("/api/v1/jobs", json=data)
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to create job [{}] in project [{}]".format(
                job_name,
                self.project,
            ),
        )

        return resp.json()

    def _execute_job(self, job_name=None, job_id=None):
        job = self._get_jobs(job_name=job_name, job_id=job_id)
        if not job:
            self.module.fail_json(
                "Job [{}] does not exist in project [{}].".format(
                    job_name,
                    self.project,
                ),
            )
        job_id = job["job_id"]  # type: ignore
        resp = self._post(
            "/api/v1/jobs/{}/execute".format(job_id),
            headers={"Content-Type": "application/json"},
        )
        # TODO: This should be removed once the Jira CSA-4401 is resolved.
        # TODO: Due to CSA-4401 a job submission can fail if there's no YARN session started yet
        # TODO: If we get a HTTP 400, we wait a bit and retry.
        if resp.status_code == requests.codes.bad_request:
            time.sleep(60)
            resp = self._post(
                "/api/v1/jobs/{}/execute".format(job_id),
                headers={"Content-Type": "application/json"},
            )
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to execute job [{}] in project [{}].".format(
                job_name or job_id,
                self.project,
            ),
        )
        return resp.json()

    def _stop_job(
        self,
        job_name=None,
        job_id=None,
        savepoint=False,
        savepoint_path=None,
        timeout_secs=0,
    ):
        job = self._get_jobs(job_name=job_name, job_id=job_id)
        if not job:
            self.module.fail_json(
                "Job [{}] does not exist in project [{}].".format(
                    job_name,
                    self.project,
                ),
            )
        assert isinstance(job, dict), "Expected job to be a dictionary"
        assert job is not None and isinstance(
            job,
            dict,
        ), "Expected job to be a dictionary"
        job_id = job["job_id"]
        resp = self._post(
            "/api/v1/jobs/{}/stop".format(job_id),
            json={
                "savepoint": savepoint,
                "savepoint_path": savepoint_path,
                "timeout": timeout_secs,
            },
        )
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to stop job [{}] in project [{}].".format(
                job_name or job_id,
                self.project,
            ),
        )
        return resp.json()

    def _delete_job(self, job_name=None, job_id=None):
        job = self._get_jobs(job_name=job_name, job_id=job_id)
        if not job:
            self.module.fail_json(
                "Job [{}] does not exist in project [{}].".format(
                    job_name,
                    self.project,
                ),
            )
        assert job is not None and isinstance(
            job,
            dict,
        ), "Expected job to be a dictionary"
        job_id = job["job_id"]
        job_id = job["job_id"]
        resp = self._delete("/api/v1/jobs/{}".format(job_id))
        self._assert_response(
            resp,
            [requests.codes.ok],
            "Failed to delete job [{}] in project [{}].".format(
                job_name or job_id,
                self.project,
            ),
        )
        return None

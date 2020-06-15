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

from typing import Callable

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_job_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbJobConfig,
    SsbJobRequest,
)

REQUIRED_ENV_VARS = [
    "SSB_SSE_API_URL",
    "SSB_SSE_API_USERNAME",
    "SSB_SSE_API_PASSWORD",
]


@pytest.fixture
def ssb_module_args(module_args, env_context) -> Callable[[dict], None]:
    """Fixture to set common module args for SSB tests."""

    def _ssb_module_args(overrides: dict = {}) -> None:
        args = {
            "url": env_context["SSB_SSE_API_URL"],
            "url_username": env_context["SSB_SSE_API_USERNAME"],
            "url_password": env_context["SSB_SSE_API_PASSWORD"],
            "force_basic_auth": True,
        }
        if overrides:
            args.update(overrides)
        module_args(args)

    return _ssb_module_args


@pytest.fixture
def test_job(
    request,
    job_client,
    existing_project,
    purge_job,
):
    """Fixture to create a test job for integration tests."""
    job_name = f"{request.node.name.lower()}_test_job"

    # Create a simple test job
    job = job_client.create_job(
        project_id=existing_project.id,
        job=SsbJobRequest(
            sql="SELECT 1 as test_column",
            job_config=SsbJobConfig(job_name=job_name),
        ),
    )

    # Register for cleanup
    purge_job(job)

    yield job


def test_ssb_job_info_module_list_all(ssb_module_args, existing_project, test_job):
    """Test SsbJobInfoModule list all jobs."""

    ssb_module_args({"project_id": existing_project.id})

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert isinstance(result["jobs"], list)
    # Verify our test job is in the results
    assert any(j["job_id"] == test_job.job_id for j in result["jobs"])


def test_ssb_job_info_module_by_job_id(ssb_module_args, existing_project, test_job):
    """Test SsbJobInfoModule get job by ID."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "job_id": test_job.job_id,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["job_id"] == test_job.job_id
    assert result["jobs"][0]["name"] == test_job.name


def test_ssb_job_info_module_by_name(ssb_module_args, existing_project, test_job):
    """Test SsbJobInfoModule get job by name."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "name": test_job.name,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert len(result["jobs"]) >= 1
    # All returned jobs should match the name
    assert all(j["name"] == test_job.name for j in result["jobs"])
    # Our test job should be in the results
    assert any(j["job_id"] == test_job.job_id for j in result["jobs"])


def test_ssb_job_info_module_by_state(ssb_module_args, existing_project, test_job):
    """Test SsbJobInfoModule filter by state."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "state": "CREATED",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert isinstance(result["jobs"], list)
    # All returned jobs should be in CREATED state
    for job in result["jobs"]:
        if "state" in job:
            assert job["state"] == "CREATED"


def test_ssb_job_info_module_nonexistent_job_id(ssb_module_args, existing_project):
    """Test SsbJobInfoModule with nonexistent job ID."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "job_id": 999999999,  # Very unlikely to exist
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert len(result["jobs"]) == 0


def test_ssb_job_info_module_nonexistent_name(ssb_module_args, existing_project):
    """Test SsbJobInfoModule with nonexistent job name."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "name": "nonexistent-job-name-12345",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert len(result["jobs"]) == 0


def test_ssb_job_info_module_check_mode(ssb_module_args, existing_project):
    """Test SsbJobInfoModule in check mode."""

    ssb_module_args(
        {
            "project_id": existing_project.id,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result

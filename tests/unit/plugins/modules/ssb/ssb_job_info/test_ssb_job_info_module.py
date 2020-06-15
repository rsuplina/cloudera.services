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

from ansible_collections.cloudera.services.tests.unit import (
    AnsibleExitJson,
    AnsibleFailJson,
)

from ansible_collections.cloudera.services.plugins.modules import ssb_job_info
from ansible_collections.cloudera.services.plugins.module_utils.ssb import (
    SsbJob,
)

BASE_URL = "https://api.cloudera.internal"
PROJECT_ID = "proj123"


def test_ssb_job_info_module_list_all_jobs(module_args, mocker):
    """Test SsbJobInfoModule listing all jobs in a project."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=1,
                name="streaming_job_1",
                sql="SELECT * FROM orders",
                state="RUNNING",
                start_time=1609459200000,
                user_id="user-123",
                username="analyst1",
                project_id=PROJECT_ID,
                flink_job_id="flink-job-001",
                created_at="2024-01-01T00:00:00Z",
            ),
            SsbJob(
                job_id=2,
                name="streaming_job_2",
                sql="SELECT COUNT(*) FROM customers",
                state="FINISHED",
                start_time=1609459200000,
                end_time=1609462800000,
                user_id="user-456",
                username="analyst2",
                project_id=PROJECT_ID,
                flink_job_id="flink-job-002",
                created_at="2024-01-01T01:00:00Z",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 2

    # Verify first job
    assert result["jobs"][0]["job_id"] == 1
    assert result["jobs"][0]["name"] == "streaming_job_1"
    assert result["jobs"][0]["state"] == "RUNNING"
    assert result["jobs"][0]["sql"] == "SELECT * FROM orders"

    # Verify second job
    assert result["jobs"][1]["job_id"] == 2
    assert result["jobs"][1]["name"] == "streaming_job_2"
    assert result["jobs"][1]["state"] == "FINISHED"

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state=None,
    )


def test_ssb_job_info_module_get_specific_job_by_id(module_args, mocker):
    """Test SsbJobInfoModule retrieving a specific job by ID."""
    mock_describe_job = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.describe_job",
        return_value=SsbJob(
            job_id=42,
            name="specific_job",
            sql="SELECT * FROM sales WHERE date > CURRENT_DATE - 7",
            state="RUNNING",
            start_time=1609459200000,
            user_id="user-789",
            username="dataengineer",
            project_id=PROJECT_ID,
            flink_job_id="flink-job-042",
            created_at="2024-01-15T10:30:00Z",
            cluster_id="cluster-001",
            jm_url="http://jobmanager:8081",
            savepoint_id=5,
        ),
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "job_id": 42,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["job_id"] == 42
    assert result["jobs"][0]["name"] == "specific_job"
    assert result["jobs"][0]["state"] == "RUNNING"
    assert result["jobs"][0]["cluster_id"] == "cluster-001"
    assert result["jobs"][0]["jm_url"] == "http://jobmanager:8081"
    assert result["jobs"][0]["savepoint_id"] == 5

    mock_describe_job.assert_called_once_with(
        project_id=PROJECT_ID,
        job_id=42,
    )


def test_ssb_job_info_module_job_by_id_not_found(module_args, mocker):
    """Test SsbJobInfoModule when specific job ID doesn't exist."""
    mock_describe_job = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.describe_job",
        return_value=None,
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "job_id": 999,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 0

    mock_describe_job.assert_called_once_with(
        project_id=PROJECT_ID,
        job_id=999,
    )


def test_ssb_job_info_module_filter_by_name(module_args, mocker):
    """Test SsbJobInfoModule filtering jobs by name."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=10,
                name="customer_analytics",
                sql="SELECT * FROM customers",
                state="RUNNING",
                start_time=1609459200000,
                user_id="user-001",
                username="analyst",
                project_id=PROJECT_ID,
            ),
            SsbJob(
                job_id=11,
                name="order_processing",
                sql="SELECT * FROM orders",
                state="RUNNING",
                start_time=1609459200000,
                user_id="user-002",
                username="engineer",
                project_id=PROJECT_ID,
            ),
            SsbJob(
                job_id=12,
                name="customer_analytics",
                sql="SELECT COUNT(*) FROM customers GROUP BY region",
                state="FINISHED",
                start_time=1609459200000,
                end_time=1609462800000,
                user_id="user-001",
                username="analyst",
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "customer_analytics",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 2

    # All returned jobs should have the name "customer_analytics"
    assert all(job["name"] == "customer_analytics" for job in result["jobs"])
    assert result["jobs"][0]["job_id"] == 10
    assert result["jobs"][1]["job_id"] == 12

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state=None,
    )


def test_ssb_job_info_module_filter_by_name_not_found(module_args, mocker):
    """Test SsbJobInfoModule filtering by name when no jobs match."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=1,
                name="job_a",
                sql="SELECT 1",
                state="RUNNING",
                user_id="user-001",
                username="analyst",
                project_id=PROJECT_ID,
            ),
            SsbJob(
                job_id=2,
                name="job_b",
                sql="SELECT 2",
                state="RUNNING",
                user_id="user-002",
                username="engineer",
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "name": "nonexistent_job",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 0

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state=None,
    )


def test_ssb_job_info_module_filter_by_state_running(module_args, mocker):
    """Test SsbJobInfoModule filtering jobs by state (RUNNING)."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=20,
                name="active_job_1",
                sql="SELECT * FROM stream1",
                state="RUNNING",
                start_time=1609459200000,
                user_id="user-100",
                username="operator",
                project_id=PROJECT_ID,
            ),
            SsbJob(
                job_id=21,
                name="active_job_2",
                sql="SELECT * FROM stream2",
                state="RUNNING",
                start_time=1609459200000,
                user_id="user-101",
                username="admin",
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "state": "RUNNING",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 2

    # Verify all jobs are in RUNNING state
    assert all(job["state"] == "RUNNING" for job in result["jobs"])
    assert result["jobs"][0]["job_id"] == 20
    assert result["jobs"][1]["job_id"] == 21

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state="RUNNING",
    )


def test_ssb_job_info_module_filter_by_state_failed(module_args, mocker):
    """Test SsbJobInfoModule filtering jobs by state (FAILED)."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=30,
                name="failed_job",
                sql="SELECT * FROM broken_source",
                state="FAILED",
                start_time=1609459200000,
                end_time=1609460000000,
                user_id="user-200",
                username="developer",
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "state": "FAILED",
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["state"] == "FAILED"
    assert result["jobs"][0]["job_id"] == 30
    assert result["jobs"][0]["end_time"] == 1609460000000

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state="FAILED",
    )


def test_ssb_job_info_module_empty_list(module_args, mocker):
    """Test SsbJobInfoModule when no jobs exist in project."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert len(result["jobs"]) == 0

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state=None,
    )


def test_ssb_job_info_module_check_mode(module_args, mocker):
    """Test SsbJobInfoModule in check mode."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=1,
                name="test_job",
                sql="SELECT 1",
                state="RUNNING",
                user_id="user-001",
                username="analyst",
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "_ansible_check_mode": True,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert "jobs" in result
    assert len(result["jobs"]) == 1

    # In check mode, the module should still execute and return data
    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state=None,
    )


def test_ssb_job_info_module_mutually_exclusive_job_id_and_name(module_args, mocker):
    """Test SsbJobInfoModule validates mutually exclusive parameters (job_id and name)."""
    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "job_id": 42,
            "name": "test_job",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_job_info.main()

    result = e.value
    assert "parameters are mutually exclusive" in result["msg"].lower()


def test_ssb_job_info_module_mutually_exclusive_job_id_and_state(module_args, mocker):
    """Test SsbJobInfoModule validates mutually exclusive parameters (job_id and state)."""
    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
            "job_id": 42,
            "state": "RUNNING",
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_job_info.main()

    result = e.value
    assert "parameters are mutually exclusive" in result["msg"].lower()


def test_ssb_job_info_module_with_complex_job_config(module_args, mocker):
    """Test SsbJobInfoModule with jobs containing complex configurations."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=100,
                name="complex_streaming_job",
                sql="SELECT a.*, b.* FROM kafka_source a JOIN database_source b ON a.id = b.id",
                state="RUNNING",
                start_time=1609459200000,
                user_id="user-500",
                username="senior_engineer",
                project_id=PROJECT_ID,
                flink_job_id="flink-job-100",
                created_at="2024-02-15T14:30:00Z",
                cluster_id="production-cluster-01",
                sample_id="sample-123",
                jm_url="http://prod-jm.example.com:8081",
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 1

    job = result["jobs"][0]
    assert job["job_id"] == 100
    assert job["cluster_id"] == "production-cluster-01"
    assert job["sample_id"] == "sample-123"
    assert job["jm_url"] == "http://prod-jm.example.com:8081"
    assert "JOIN" in job["sql"]

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state=None,
    )


def test_ssb_job_info_module_with_all_job_states(module_args, mocker):
    """Test SsbJobInfoModule listing jobs with various states."""
    mock_list_jobs = mocker.patch(
        "ansible_collections.cloudera.services.plugins.modules.ssb_job_info.SsbJobClient.list_jobs",
        return_value=[
            SsbJob(
                job_id=1,
                name="running_job",
                sql="SELECT 1",
                state="RUNNING",
                user_id="user-001",
                username="analyst",
                project_id=PROJECT_ID,
            ),
            SsbJob(
                job_id=2,
                name="finished_job",
                sql="SELECT 2",
                state="FINISHED",
                user_id="user-002",
                username="engineer",
                project_id=PROJECT_ID,
            ),
            SsbJob(
                job_id=3,
                name="failed_job",
                sql="SELECT 3",
                state="FAILED",
                user_id="user-003",
                username="developer",
                project_id=PROJECT_ID,
            ),
            SsbJob(
                job_id=4,
                name="canceled_job",
                sql="SELECT 4",
                state="CANCELED",
                user_id="user-004",
                username="admin",
                project_id=PROJECT_ID,
            ),
        ],
    )

    module_args(
        {
            "endpoint": BASE_URL,
            "project_id": PROJECT_ID,
        },
    )

    with pytest.raises(AnsibleExitJson) as e:
        ssb_job_info.main()

    result = e.value
    assert result["changed"] is False
    assert len(result["jobs"]) == 4

    states = [job["state"] for job in result["jobs"]]
    assert "RUNNING" in states
    assert "FINISHED" in states
    assert "FAILED" in states
    assert "CANCELED" in states

    mock_list_jobs.assert_called_once_with(
        project_id=PROJECT_ID,
        state=None,
    )


def test_ssb_job_info_module_missing_required_parameter(module_args, mocker):
    """Test SsbJobInfoModule fails when required project_id parameter is missing."""
    module_args(
        {
            "endpoint": BASE_URL,
            # Missing project_id
        },
    )

    with pytest.raises(AnsibleFailJson) as e:
        ssb_job_info.main()

    result = e.value
    assert (
        "missing required arguments" in result["msg"].lower()
        or "required" in result["msg"].lower()
    )

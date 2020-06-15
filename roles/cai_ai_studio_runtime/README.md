# AI Agent Studio Runtime Deployment

Deploy Cloudera AI Studio using runtime image application.

## Requirements

None

## Role Variables

Available variables are listed below, along with default values (see also `defaults/main.yml`).

| Variable | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `cai_workspace_api` | `str` | Yes | | Cloudera AI Workbench API endpoint. |
| `cai_workbench_api_key` | `str` | Yes | | Cloudera AI Workbench API v2 key. |
| `cai_project` | `str` | Yes | | The name of a pre-existing Cloudera AI project name. |
| `cai_endpoint_tls` | `bool` | No | `true` | Whether to verify TLS certificates for API endpoints. Set to `false` to skip TLS certificate verification. |
| `cai_agent_studio_runtime_repo_url` | `str` | No | `https://archive.cloudera.com/agent-studio/latest/artifacts/repo-assembly.json` | URL to the Agent Studio runtime repository. |
| `cai_agent_studio_runtime_name` | `str` | No | `Agent Studio` | Name of the Agent Studio runtime. |
| `cai_agent_studio_app_name` | `str` | No | `Agent Studio` | Name of the Agent Studio application. |
| `cai_ai_studio_async_setup` | `bool` | No | `false` | Whether to set up AI Studio asynchronously. |
| `cai_agent_app_cpu` | `int` | No | `2` | CPU allocation for the Agent Studio application. |
| `cai_agent_app_memory` | `int` | No | `4` | Memory allocation (in GB) for the Agent Studio application. |
| `cai_agent_studio_script` | `str` | No | `/studio_app/startup_scripts/run-app.py` | Script path to run the Agent Studio application. |
| `cai_agent_studio_subdomain` | `str` | No | `agent-studio` | Subdomain for the Agent Studio application. |
| `cai_agent_studio_app_auth` | `bool` | No | `true` | Whether authentication is required for the Agent Studio application. |
| `cai_agent_studio_environment` | `dict` | No | | Environment variables for the Agent Studio application. |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: localhost
  connection: local
  tasks:

    - name: Deploy Agent Studio Runtime
      ansible.builtin.import_role:
        name: cai_ai_studio_runtime
      vars:
        cai_project: "example-project"
        cai_workspace_api: "https://example-workbench.cloudera.com"
        cai_workbench_api_key: "example-workbench-api-key"
        cai_ai_studio_async_setup: false
```

## License

```
Copyright 2026 Cloudera, Inc.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
```

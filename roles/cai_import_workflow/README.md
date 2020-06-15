# AI Studios Import Workflow Template Role

Import Workflow Templates to Cloudera AI Agent Studio.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values (see also `defaults/main.yml`).

| Variable | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `cai_workspace_api` | `str` | Yes | | Cloudera AI Workbench API endpoint. |
| `cai_workbench_api_key` | `str` | Yes | | Cloudera AI Workbench API v2 key. |
| `cai_project` | `str` | Yes | | The name of a pre-existing Cloudera AI project name. |
| `cai_endpoint_tls` | `bool` | No | `true` | Whether to verify TLS certificates for API endpoints. Set to `false` to skip TLS certificate verification. |
| `cai_user` | `str` | Yes |  | Cloudera AI Username. |
| `ai_studio` | `str` | No | `agent_studio` | String to select pre-defined AI Studio configurations. |
| `cai_ai_studio_amp_deployment` | `bool` | No | `true` | Whether the AI Studio is deployed as an AMP deployment. |
| `cai_ai_studio_override` | `dict` | No |  | Override of the pre-defined AI Studio configurations. Setting this variable ignores the variable for `ai_studio`. |
| `workflow_template_upload_path` | `str` | No | `/home/cdsw` |  Location in Cloudera AI project where workflow templates are uploaded. |
| `workflow_templates` | `list` | No |  | Details of Workflow templates to import. |

## Notes

The pre-defined AI Studio configurations defined by the role are listed below.

```yaml
agent_studio:
  slug: "agent-studio"
  application_name: "Agent Studio"
fine_tuning_studio:
  slug: "fine-tuning-studio"
  application_name: "Fine Tuning Studio"
synthetic_data_studio:
  slug: "synthetic-data-studio"
  application_name: "Synthetic Data Studio"
rag_studio:
  slug: "rag-studio"
  application_name: "RAG Studio"
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: localhost
  connection: local
  tasks:

    - name: Register LLM models
      ansible.builtin.import_role:
        name: cai_import_workflow
      vars:
        ai_studio: "agent_studio"
        cai_project: "example-project"
        cai_workspace_api: "example-workbench-api"
        cai_workbench_api_key: "example-workbench-api-key"
        cai_user: "example-user"
        workflow_templates:
          - template_name: "Test Workflow 1"
            file: "files/cai/workflow_template_example1.zip"
          - template_name: "Test Workflow 2"
            file: "files/cai/workflow_template_example2.zip"
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

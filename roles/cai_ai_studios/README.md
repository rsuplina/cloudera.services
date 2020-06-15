<!--
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
-->

# AI Studios Role

Launch and configure Cloudera AI Studio. The role has pre-defined configurations to support deployment of the core AI Studios - Agent Studio, Fine Tuning Studio, Synthetic Data Studio and RAG Studio - but is flexible to deploy any AI Studio.

## Requirements

## Role Variables

Available variables are listed below, along with default values (see also `defaults/main.yml`).

| Variable | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `cai_workspace_api` | `str` | Yes | | Cloudera AI Workbench API endpoint. |
| `cai_workbench_api_key` | `str` | Yes | | Cloudera AI Workbench API v2 key. |
| `cai_project` | `str` | Yes | | The name of a pre-existing Cloudera AI project name. |
| `cai_user` | `str` | Yes |  | Cloudera AI Username. |
| `cai_runtime_image_name` | `str` | Yes |  | Runtime Image to use for the AI Studio. |
| `cai_environment_variables` | `dict` | No | `{}`  | Environment Variables to set for the AI studio. |
| `cai_runtime_addons` | `list` | No | `[]`  | List of Cloudera AI runtime to include in the AI Studio configuration. |
| `cai_task_level_runtimes` | `list` | No | `[]`  | List of Cloudera AI adds ons to include in the AI Studio task configurations |
| `ai_studio` | `str` | No | `agent_studio` | String to select pre-defined AI Studio configurations. |
| `cai_ai_studio_details` | `dict` | No |  | Details of AI Studio configuration. Use if not using a pre-defined AI Studio, as defined in `vars/main.yml`. |

## Dependencies

None.

## Example Playbook

```yaml
- hosts: localhost
  connection: local
  vars:
    cdp_env: my-cloudera-env
    cai_workbench: "my-cai-workbench"
    cai_workbench_api_key: "<WORKBENCH_API_KEY>"
    cai_project: "my-cai-studio-proj"
    cai_user: "<USERNAME>"
  tasks:

    - name: Provision the CAI project
        cloudera.services.ml_project:
        endpoint: "{{ cai_workspace_api }}"
        api_key: "{{ cai_workbench_api_key }}"
        name: "{{ cai_project }}"
        desc: "AI Studio Automation"
        runtime: ml_runtime
        template: blank
        visibility: organization
        register: __ai_studio_proj

    - name: Provision Fine Tuning AI Studio
      ansible.builtin.import_role:
        name: cai_ai_studios
      vars:
        ai_studio: "fine_tuning_studio"
        cai_runtime_image_name: "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-pbj-jupyterlab-python3.10-cuda:2025.01.3-b8"
        cai_environment_variables:
          FINE_TUNING_STUDIO_SQLITE_DB: ".app/state.db"
          FINE_TUNING_STUDIO_PROJECT_DEFAULTS: "data/project_defaults.json"
          CUSTOM_LORA_ADAPTERS_DIR: "data/adapters/"
          HUGGINGFACE_ACCESS_TOKEN: "< HF_TOKEN >"
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

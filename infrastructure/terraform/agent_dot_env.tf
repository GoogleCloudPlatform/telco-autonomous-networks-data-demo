#
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

resource "local_file" "rca_agent_dot_env" {
  filename        = "${path.module}/../../agents/root_cause_analysis/.env"
  file_permission = "0666"
  content         = <<EOF
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_LOCATION=global

AGENT_DATA_LOG_DATASET=agent_logs
AGENT_DATA_LOG_TABLE=agent_events
AGENT_DATA_LOG_PROJECT_ID=${var.bigquery_data_project_id}

BIGQUERY_DATA_LOCATION=${google_bigquery_dataset.telco-dataset.location}
BIGQUERY_DATA_PROJECT_ID=${google_bigquery_dataset.telco-dataset.project}
BIGQUERY_DATASET=${google_bigquery_dataset.telco-dataset.dataset_id}
BIGQUERY_RUN_PROJECT_ID=${var.project_id}

BIGQUERY_TABLE_CELL_TRACES=${google_bigquery_table.cell_traces.table_id}
BIGQUERY_TABLE_INCIDENTS=${google_bigquery_table.incidents.table_id}
BIGQUERY_TABLE_PERFORMANCE=${google_bigquery_table.performance.table_id}
BIGQUERY_TABLE_PERFORMANCE_KPI=${google_bigquery_table.performance_kpi.table_id}

INTERNAL_DOCS_DATASTORE_ID=${google_discovery_engine_data_store.rca_rules.id}

PROJECT_ID=${var.project_id}
VERTEX_AI_SEARCH_ENGINE_RCA_RULES=${google_discovery_engine_search_engine.rca_rules_search_engine.engine_id}
VERTEX_AI_SEARCH_ENGINE_RCA_RULES_LOCATION=${google_discovery_engine_search_engine.rca_rules_search_engine.location}
EOF
}

resource "local_file" "incident_detector_agent_dot_env" {
  filename        = "${path.module}/../../agents/incident_detector/.env"
  file_permission = "0666"
  content         = <<EOF
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_LOCATION=global

AGENT_DATA_LOG_DATASET=agent_logs
AGENT_DATA_LOG_TABLE=agent_events
AGENT_DATA_LOG_PROJECT_ID=${var.bigquery_data_project_id}

BIGQUERY_DATA_LOCATION=${google_bigquery_dataset.telco-dataset.location}
BIGQUERY_DATA_PROJECT_ID=${google_bigquery_dataset.telco-dataset.project}
BIGQUERY_DATASET=${google_bigquery_dataset.telco-dataset.dataset_id}
BIGQUERY_RUN_PROJECT_ID=${var.project_id}

BIGQUERY_TABLE_INCIDENTS=${google_bigquery_table.incidents.table_id}
BIGQUERY_TABLE_PERFORMANCE=${google_bigquery_table.performance.table_id}
BIGQUERY_TABLE_PERFORMANCE_KPI=${google_bigquery_table.performance_kpi.table_id}

EOF
}
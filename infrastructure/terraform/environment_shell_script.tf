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

resource "local_file" "cloud_env" {
  filename        = "${path.module}/../../.cloud-env.sh"
  file_permission = "0555"
  content         = <<EOF
export PROJECT_ID=${var.project_id}
# We don't have a dedicated BigQuery billing project id in this demo, but for most production
# environments it will be separate from the data project id
export BIGQUERY_RUN_PROJECT_ID=${var.project_id}
export BIGQUERY_DATA_PROJECT_ID=${var.bigquery_data_project_id}
export BIGQUERY_DATA_LOCATION=${var.bigquery_dataset_location}
export BIGQUERY_DATASET=${google_bigquery_dataset.telco-dataset.dataset_id}
export BIGQUERY_TABLE_PERFORMANCE=${google_bigquery_table.performance.table_id}
export BIGQUERY_TABLE_INCIDENTS=${google_bigquery_table.incidents.table_id}
export BIGQUERY_TABLE_CELL_TRACES=${google_bigquery_table.cell_traces.table_id}
export VERTEX_AI_DATASTORE_RCA_RULES=${google_discovery_engine_data_store.rca_rules.data_store_id}
export VERTEX_AI_SEARCH_ENGINE_RCA_RULES=${google_discovery_engine_search_engine.rca_rules_search_engine.engine_id}
EOF
}
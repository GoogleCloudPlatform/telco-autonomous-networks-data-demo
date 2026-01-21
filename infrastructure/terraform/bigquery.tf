# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

resource "google_bigquery_dataset" "telco-dataset" {
  project = var.bigquery_data_project_id
  dataset_id    = "telco_demo"
  friendly_name = "Simulated telco data"
  location      = var.bigquery_dataset_location

  delete_contents_on_destroy = true
}

locals {
  dataset_id                 = google_bigquery_dataset.telco-dataset.dataset_id
  fq_dataset_id              = "${var.project_id}.${google_bigquery_dataset.telco-dataset.dataset_id}"
}

resource "google_bigquery_table" "performance" {
  deletion_protection = false
  dataset_id          = local.dataset_id
  table_id            = "performance"
  description         = "Performance measurements collected at 15 minute intervals"
  schema              = file("${path.module}/bigquery-schema/performance.json")
  clustering          = ["enodeb_id", "cell_id"]
  time_partitioning {
    type = "DAY"
    field = "measurement_end"
  }
}

locals {
  performance_fqn = "${google_bigquery_dataset.telco-dataset.project}.${google_bigquery_dataset.telco-dataset.dataset_id}.${google_bigquery_table.performance.table_id}"
}

resource "google_bigquery_table" "performance_kpi" {
  deletion_protection = false
  depends_on = [google_bigquery_table.performance]
  dataset_id          = local.dataset_id
  table_id            = "performance_kpi"
  description         = "Calculated performance KPIs"
  materialized_view {
    query = templatefile("${path.module}/bigquery-schema/performance_kpi.sql.tftpl",
      { base_table = local.performance_fqn})
  }
}

resource "google_bigquery_table" "cell_traces" {
  deletion_protection = false
  dataset_id          = local.dataset_id
  table_id            = "cell_traces"
  description         = "Cell traces"
  schema              = file("${path.module}/bigquery-schema/cell-traces.json")
  clustering          = ["start_enodeb_id", "start_cell_id"]
  time_partitioning {
    type = "DAY"
    field = "starttime"
  }
}

resource "google_bigquery_table" "incidents" {
  deletion_protection = false
  dataset_id          = local.dataset_id
  table_id            = "incidents"
  description         = "Incidents generated based on the KPI levels dropping below thresholds"
  schema              = file("${path.module}/bigquery-schema/incidents.json")
}

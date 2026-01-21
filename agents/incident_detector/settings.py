#  Copyright 2025 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    incident_detector_model: str = 'gemini-3-pro-preview'

    bigquery_run_project_id: str
    bigquery_data_project_id: str
    bigquery_data_location: str
    bigquery_dataset: str
    bigquery_table_performance: str
    bigquery_table_incidents: str
    bigquery_table_performance_kpi: str

    agent_data_log_project_id: str
    agent_data_log_dataset: str
    agent_data_log_table: str

    user_agent: str = "cloud-solutions/telco-rca-usage-v1"


settings = AgentSettings()

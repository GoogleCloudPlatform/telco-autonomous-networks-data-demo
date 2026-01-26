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
from google.api_core.client_info import ClientInfo
from pydantic import model_validator, Field
from pydantic_settings import BaseSettings
from typing import Self, Optional


class AgentSettings(BaseSettings):
    root_agent_name: str = "root_cause_analyst"
    external_doc_retriever_model: Optional[str] = None
    internal_doc_retriever_model: Optional[str] = None
    incident_retriever_model: str = 'gemini-2.5-flash'
    prior_incidents_searcher_model: Optional[str] = None
    report_generator_model: Optional[str] = None
    instruction_generator_model: Optional[str] = None
    analyzer_model: Optional[str] = None
    root_agent_model: Optional[str] = None
    default_model: str = 'gemini-3-pro-preview'
    show_thoughts: bool = True

    internal_docs_datastore_id: str = Field(
        description="Vertex AI Datastore ID")

    agent_data_log_project_id: str
    agent_data_log_dataset: str
    agent_data_log_table: str

    bigquery_run_project_id: str
    bigquery_data_project_id: str
    bigquery_data_location: str
    bigquery_dataset: str

    bigquery_table_cell_traces: str
    bigquery_table_performance: str
    bigquery_table_incidents: str

    project_id: str
    vertex_ai_search_engine_rca_rules: str
    vertex_ai_search_engine_rca_rules_location: str

    embeddings_model: str = "gemini-embedding-001"

    # TODO: these need to be tested and adjusted as needed
    similarity_search_cutoff_distance: float = .5
    similarity_search_likely_match_distance: float = .9
    similarity_search_max_number_of_incidents: int = 5

    api_client_info: ClientInfo = ClientInfo(
        user_agent="cloud-solutions/telco-rca-usage-v1")

    confirm_each_step: bool = False

    @model_validator(mode='after')
    def set_defaults(self) -> Self:
        if not self.external_doc_retriever_model:
            self.external_doc_retriever_model = self.default_model
        if not self.internal_doc_retriever_model:
            self.internal_doc_retriever_model = self.default_model
        if not self.incident_retriever_model:
            self.incident_retriever_model = self.default_model
        if not self.prior_incidents_searcher_model:
            self.prior_incidents_searcher_model = self.default_model
        if not self.report_generator_model:
            self.report_generator_model = self.default_model
        if not self.instruction_generator_model:
            self.instruction_generator_model = self.default_model
        if not self.analyzer_model:
            self.analyzer_model = self.default_model
        if not self.root_agent_model:
            self.root_agent_model = self.default_model

        return self


settings = AgentSettings()

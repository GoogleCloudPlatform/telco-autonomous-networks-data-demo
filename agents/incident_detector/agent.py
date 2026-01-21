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
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.plugins.bigquery_agent_analytics_plugin import \
    BigQueryAgentAnalyticsPlugin

from incident_detector.settings import settings
from incident_detector.tools import get_potential_incidents, create_new_incident

incident_detector_agent = LlmAgent(
    model=Gemini(
        model=settings.incident_detector_model
    ),
    name="incident_detector",
    static_instruction="""
Get and analyze potential incidents, prioritize based on severity and ask the user to confirm before creating the new incident.
""",
    description="Checks to see if there are new incidents in the networks and prompts to create a new instance.",
    tools=[get_potential_incidents, create_new_incident]
)

root_agent = incident_detector_agent

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=settings.agent_data_log_project_id,
    dataset_id=settings.agent_data_log_dataset,
    table_id=settings.agent_data_log_table
)

app = App(
    name="incident_detector",
    root_agent=root_agent,
    plugins=[bq_logging_plugin]
)

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
from google.adk import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.planners import BuiltInPlanner
from google.adk.plugins.bigquery_agent_analytics_plugin import \
    BigQueryAgentAnalyticsPlugin
from google.adk.tools import AgentTool
from google.genai.types import ThinkingConfig

from root_cause_analysis.settings import settings
from root_cause_analysis.subagents.analyzer.agent import build_analyzer_agent
from root_cause_analysis.subagents.external_documentation_searcher.agent import \
    build_external_documentation_retriever
from root_cause_analysis.subagents.incident_retriever.agent import \
    build_incident_retriever_agent
from root_cause_analysis.subagents.incident_retriever.tools import \
    get_incident_info
from root_cause_analysis.subagents.instructions_generator.agent import \
    build_instruction_generator_agent
from root_cause_analysis.subagents.internal_documentation_retriever.agent import \
    build_internal_documentation_retriever_agent
from root_cause_analysis.subagents.prior_incident_searcher.agent import \
    build_prior_incidents_searcher
from root_cause_analysis.subagents.report_generator.agent import \
    build_report_generator
from root_cause_analysis.subagents.rules_retriever.agent import \
    build_rules_retriever_agent
from root_cause_analysis.subagents.severity_classifier.agent import \
    build_severity_classifier_agent
from root_cause_analysis.tools.incident_data import update_incident

incident_retriever_agent = build_incident_retriever_agent()
external_documentation_retriever_agent = build_external_documentation_retriever()
internal_documentation_retriever_agent = build_internal_documentation_retriever_agent()
prior_incidents_search_agent = build_prior_incidents_searcher()
report_generator_agent = build_report_generator()
instruction_generator = build_instruction_generator_agent()
analyzer = build_analyzer_agent()
rules_retriever = build_rules_retriever_agent()
severity_classifier = build_severity_classifier_agent()

how_to_proceed_before_each_step = \
    "Show what the next step is and confirm before proceeding." \
        if settings.confirm_each_step else \
        "Indicate progress before executing every step."

root_agent = Agent(
    model=Gemini(
        # TODO: add dedicated model
        model=settings.default_model
    ),
    name=settings.root_agent_name,
    description="Root cause analysis agent",
    static_instruction=f"""
    You are an agent responsible for root cause analysis of incidents in telecommunication networks.

    First, obtain the incident id and retrieve the incident information. Don't proceed until you succeeded.
    
    Then, perform the incident processing using the following steps:
    1. Retrieve rules related to this incident.
    2. Generate specific agent instructions based on these rules.
    3. Perform the root cause analysis of the incident using these instructions. Delegate this work to the subagent.
    4. Determine the severity level of the incident. Don't provide any additional information about the incident because the tool has access to all the data needed.
    5. Retrieve external and internal documentation related to the incident.
    6. Search for prior incidents similar to the one being analyzed.
    7. Generate the final report by using the report_generator_agent tool.
    
    Finally, display the report. Ask the user if they want to update the incident with this report.
    
    {how_to_proceed_before_each_step}
    """,
    sub_agents=[analyzer],
    tools=[
        get_incident_info,
        AgentTool(agent=rules_retriever),
        AgentTool(agent=instruction_generator),
        AgentTool(agent=severity_classifier),
        AgentTool(agent=external_documentation_retriever_agent),
        AgentTool(agent=internal_documentation_retriever_agent),
        AgentTool(agent=prior_incidents_search_agent),
        AgentTool(agent=report_generator_agent),
        update_incident],
    planner=BuiltInPlanner(
        thinking_config=ThinkingConfig(
            include_thoughts=settings.show_thoughts))
)

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=settings.agent_data_log_project_id,
    dataset_id=settings.agent_data_log_dataset,
    table_id=settings.agent_data_log_table
)

app = App(
    name="root_cause_analysis",
    root_agent=root_agent,
    # TODO: there is a bug with the plugin - it doesn't work with custom agents.
    # Uncomment once fixed.
    # plugins=[bq_logging_plugin]
)

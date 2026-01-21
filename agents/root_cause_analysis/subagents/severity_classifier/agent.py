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
from google.adk.models import Gemini
from google.adk.planners import BuiltInPlanner
from google.adk.tools import ToolContext
from google.genai.types import ThinkingConfig, GenerateContentConfig

from root_cause_analysis.constants import KEY_SEVERITY_DETERMINATION_RULES, \
    KEY_SEVERITY_LEVEL, KEY_INCIDENT_INFO, \
    KEY_SEVERITY_DETERMINATION_RULES_TOOLS
from root_cause_analysis.settings import settings
from root_cause_analysis.tools.analysis_tools import AnalysisToolset

# TODO: use this agent similar to the primary analysis agent.
async def update_severity_level(tool_context: ToolContext,
    severity: str) -> dict:
    tool_context.state[KEY_SEVERITY_LEVEL] = severity

    return {'status': 'success'}


severity_determination_rule_toolset = AnalysisToolset(
    state_key=KEY_SEVERITY_DETERMINATION_RULES_TOOLS)


def build_severity_classifier_agent():
    return Agent(
        model=Gemini(
            model=settings.analyzer_model),
        name='severity_classifier_agent',
        description="Classifies the current incident's severity",
        instruction=f"""
        Classify the severity of the following incident:
        
        {{{KEY_INCIDENT_INFO}}}
         
        Use the following rules to do classification:
        
        {{{KEY_SEVERITY_DETERMINATION_RULES}}}
        
        The severity must be only HIGH, MEDIUM, or LOW.
        
        You must call the update_severity_level tool with the value of the severity.
        
        Reply with the brief explanation why you selected this severity.
        """,
        tools=[severity_determination_rule_toolset, update_severity_level],
        generate_content_config=GenerateContentConfig(
            labels={"agent": "rca"},
        ),
        planner=BuiltInPlanner(
            thinking_config=ThinkingConfig(
                include_thoughts=settings.show_thoughts))
    )

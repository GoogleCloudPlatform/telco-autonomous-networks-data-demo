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

from root_cause_analysis.constants import KEY_INSTRUCTIONS, \
    KEY_ANALYSIS, KEY_PROCESSING_RULES_TOOLS
from root_cause_analysis.settings import settings
from root_cause_analysis.tools.analysis_tools import AnalysisToolset

processing_rules_toolset = AnalysisToolset(state_key=KEY_PROCESSING_RULES_TOOLS)


# This tool serves two purposes - stores the analysis in the state and also transfers the control to the root agent.
async def save_analysis(tool_context: ToolContext, analysis: str):
    tool_context.state[KEY_ANALYSIS] = analysis
    tool_context.actions.transfer_to_agent = settings.root_agent_name


def build_analyzer_agent():
    return Agent(
        model=Gemini(
            model=settings.analyzer_model),
        name='analyzer_agent',
        description='Performs root cause analysis of the incident using the generated instructions',
        instruction=f"""
        {{{KEY_INSTRUCTIONS}}}
        
        Once you successfully complete the analysis, save it using the save_analysis tool.
        """,
        tools=[processing_rules_toolset, save_analysis],
        generate_content_config=GenerateContentConfig(
            labels={"agent": "rca"},
        ),
        output_key=KEY_ANALYSIS,
        planner=BuiltInPlanner(
            thinking_config=ThinkingConfig(
                include_thoughts=settings.show_thoughts))
    )

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
from google.adk.models import Gemini
from google.adk.tools import ToolContext

from root_cause_analysis.constants import KEY_INSTRUCTIONS, \
    KEY_PROCESSING_RULES
from root_cause_analysis.settings import settings


async def receive_instructions(tool_context: ToolContext,
    instructions: str) -> dict:
    tool_context.state[KEY_INSTRUCTIONS] = instructions

    return {'status': 'success'}


def build_instruction_generator_agent():
    return Agent(
        model=Gemini(
            model=settings.instruction_generator_model),
        name='instruction_generator_agent',
        description='Generates instructions for the anaysis agent based on the incident specific rules.',
        instruction=f"""
        Generate the instructions for a Gemini based Root Cause Analysis agent based on the information about the incident.
        
        Use these rules to generate the instructions:
        {{{KEY_PROCESSING_RULES}}}
        
        Call the receive_instructions tool with the generated instructions. 
        At the end, simply state the instructions were successfully generated.
        """,
        tools=[receive_instructions],
        planner=settings.planner,
        generate_content_config=settings.content_config
    )

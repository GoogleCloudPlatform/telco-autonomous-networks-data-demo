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
from typing import Optional

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.genai.types import FunctionCall

from root_cause_analysis.constants import KEY_ACTIONS
from root_cause_analysis.settings import settings
from root_cause_analysis.tools.analysis_tools import automatic_action_toolset


async def check_if_there_are_actions(callback_context: CallbackContext) -> \
        Optional[types.Content]:
    if not KEY_ACTIONS in callback_context.state:
        return types.Content(
            role="model",
            parts=[
                types.Part(text="There are no suggested automated actions to be taken."),
                types.Part(
                    function_call=FunctionCall(name="transfer_to_agent", args={"agent_name": settings.root_agent_name}))
            ],
        )
    return None


def build_action_executor():
    return Agent(
        model=settings.agent_executor_model,
        name='action_executor',
        description='Lists, confirms and executes suggested actions',
        instruction=f'''
You are given the list of actions:

*Actions:*
{{{KEY_ACTIONS}}}

*Instructions:*

First, list the actions with the SUGGESTED status. Include their names, parameters, and the reason to perform.

In a separate section after that list all other actions. Include their name and status only. If there are no actions with SUGGESTED status - don't show this section.

If there are no more suggested actions left, automatically transfer to the {settings.root_agent_name} agent.

Ask the user if and which action they want to execute. If the answer is negative then return to the {settings.root_agent_name} agent.

Once you find the suggested action - execute the tool with the same name and exactly the same parameters as provided in the list.
    ''',
        tools=[automatic_action_toolset],
        before_agent_callback=check_if_there_are_actions,
        planner=settings.planner,
        generate_content_config=settings.content_config
    )

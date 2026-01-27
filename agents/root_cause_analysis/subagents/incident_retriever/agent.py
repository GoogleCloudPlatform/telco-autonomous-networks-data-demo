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

from root_cause_analysis.settings import settings
from root_cause_analysis.subagents.incident_retriever.tools import \
    get_incident_info


def build_incident_retriever_agent():
    return Agent(
        model=Gemini(
            model=settings.incident_retriever_model),
        name='incident_retriever_agent',
        description='Retrieves the general incident information.',
        instruction="""
        Retrieve the incident information based on the incident id.
        
        If you can't find the incident or if there is an error, respond to the user with this information and ask whether to try another incident id or use the same one.
        """,
        tools=[get_incident_info],
        planner=settings.planner,
        generate_content_config=settings.content_config
    )

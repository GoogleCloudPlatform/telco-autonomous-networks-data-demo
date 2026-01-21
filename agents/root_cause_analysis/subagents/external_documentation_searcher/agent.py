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
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, Gemini
from google.adk.tools import url_context
from google.genai.types import Part, Content
from typing import Optional

from root_cause_analysis.constants import KEY_EXTERNAL_SEARCH_GROUNDING, \
    KEY_EXTERNAL_SEARCH_RESULTS, KEY_INCIDENT_INFO
from root_cause_analysis.models import ExternalSearchResult
from root_cause_analysis.settings import settings
from root_cause_analysis.tools.vertex_ai_search import \
    extract_vertex_ai_grounding_metadata, get_grounding_details


async def extract_grounding_metadata(callback_context: CallbackContext,
    llm_response: LlmResponse) -> Optional[LlmResponse]:
    await extract_vertex_ai_grounding_metadata(
        callback_context=callback_context,
        llm_response=llm_response,
        key_to_store_metadata=KEY_EXTERNAL_SEARCH_GROUNDING)


async def assert_search_is_grounded(callback_context: CallbackContext,
    llm_response: LlmResponse) -> Optional[LlmResponse]:
    if llm_response.partial:
        return None

    grounded, grounding_metadata, references = await get_grounding_details(
        callback_context, KEY_EXTERNAL_SEARCH_GROUNDING)

    if not grounded:
        return LlmResponse(
            content=Content(role="model", parts=[
                Part(
                    text="External search haven't found any documents or the search failed.")
            ])
        )

    final_result = ExternalSearchResult(
        # TODO: this needs to be more sophisticated in case there are multiple parts.
        search_results=llm_response.content.parts[0].text,
        references=references
    )

    callback_context.state[
        KEY_EXTERNAL_SEARCH_RESULTS] = final_result.model_dump_json()

    return None


external_sites_to_search = [
    "https://ourtechplanet.com/lte-erab-success-rate/"
]


def build_external_documentation_retriever():
    return Agent(
        model=Gemini(
            model=settings.external_doc_retriever_model,
        ),
        name='external_documentation_retriever_agent',
        description='Retrieves external documentation related to the incident',
        static_instruction=
        '''If you cannot access the URLs then respond with a message that the external search 
        is misconfigured.''',
        instruction=
        f'''Identify the root causes and potential remedies related to this incident: 
        
        {{{KEY_INCIDENT_INFO}}}.
        
        Only use these URLs to get the possible root causes of the problem:
        {external_sites_to_search}
        ''',
        tools=[url_context],
        after_model_callback=[extract_grounding_metadata,
                              assert_search_is_grounded]
    )

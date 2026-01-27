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
from google.adk.models import LlmResponse
from google.adk.tools import VertexAiSearchTool
from google.genai.types import Part, Content

from root_cause_analysis.constants import KEY_INTERNAL_SEARCH_RESULTS, \
    KEY_INTERNAL_SEARCH_GROUNDING, KEY_INCIDENT_INFO
from root_cause_analysis.models import InternalSearchResult
from root_cause_analysis.settings import settings
from root_cause_analysis.tools.vertex_ai_search import \
    extract_vertex_ai_grounding_metadata, get_grounding_details


async def extract_grounding_metadata(callback_context: CallbackContext,
    llm_response: LlmResponse) -> Optional[LlmResponse]:
    await extract_vertex_ai_grounding_metadata(
        callback_context=callback_context,
        llm_response=llm_response,
        key_to_store_metadata=KEY_INTERNAL_SEARCH_GROUNDING)


async def assert_search_is_grounded(callback_context: CallbackContext,
    llm_response: LlmResponse) -> Optional[LlmResponse]:
    if llm_response.partial:
        return None

    grounded, grounding_metadata, references = await get_grounding_details(
        callback_context, KEY_INTERNAL_SEARCH_GROUNDING)

    if not grounded:
        return LlmResponse(
            content=Content(role="model", parts=[
                Part(
                    text="Internal search haven't found any documents or the search failed.")
            ])
        )

    final_result = InternalSearchResult(
        queries=grounding_metadata.retrieval_queries,
        # TODO: this needs to be more sophisticated in case there are multiple parts.
        search_result=llm_response.content.parts[0].text,
        references=references
    )

    callback_context.state[
        KEY_INTERNAL_SEARCH_RESULTS] = final_result.model_dump_json()

    return None


def build_internal_documentation_retriever_agent():
    return Agent(
        model=settings.internal_doc_retriever_model,
        name='internal_documentation_retriever_agent',
        description='Retrieves internal documentation related to the incident',
        instruction=
        f'''Retrieve the causes and suggested actions related to the incident: 
        {{{KEY_INCIDENT_INFO}}}.
        
        **Critical:** only use the results returned by 'vertex_ai_search' tool and nothing else. 
        
        If the tool doesn't return any results just state that in the final response.
        ''',
        tools=[VertexAiSearchTool(
            data_store_id=settings.internal_docs_datastore_id)],
        # Order is important - grounding metadata needs to be extracted first.
        after_model_callback=[extract_grounding_metadata,
                              assert_search_is_grounded],
        planner=settings.planner,
        generate_content_config=settings.content_config
    )

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
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from google.genai.types import GroundingChunk

from root_cause_analysis.models import MissedKPI, Rules, Document
from root_cause_analysis.settings import settings


async def extract_vertex_ai_grounding_metadata(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
    key_to_store_metadata: str) -> None:
    # We are only interested in capturing the grounding metadata if there are chunks.
    if llm_response.grounding_metadata and llm_response.grounding_metadata.grounding_chunks:
        callback_context.state[
            key_to_store_metadata] = llm_response.grounding_metadata


vertexai_datastore_api_prefix = 'https://discoveryengine.googleapis.com/v1/'


async def get_grounding_details(callback_context: CallbackContext,
    grounding_state_key: str):
    grounding_metadata = callback_context.state.get(
        grounding_state_key)
    grounded = grounding_metadata and grounding_metadata.grounding_chunks

    if not grounded:
        return False, None, None

    references: list[Document] = []
    for chunk in grounding_metadata.grounding_chunks:
        chunk: GroundingChunk
        if chunk.web:
            references.append(
                Document(url=chunk.web.uri, title=chunk.web.title))
            continue

        if chunk.retrieved_context:
            references.append(Document(
                url=vertexai_datastore_api_prefix + chunk.retrieved_context.document_name,
                title=chunk.retrieved_context.text))
            continue

    return grounded, grounding_metadata, references


async def find_rca_rules(missed_kpis: list[MissedKPI]) -> list[Rules]:
    location = settings.vertex_ai_search_engine_rca_rules_location

    project_id = settings.project_id
    engine_id = settings.vertex_ai_search_engine_rca_rules

    filter = ('kpi_missed: ANY(' +
              ",".join(
                  ['"' + missed_kpi.kpi + '"' for missed_kpi in missed_kpis])
              + ')')

    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None

    )

    # Create a client
    client = discoveryengine.SearchServiceClient(
        client_options=client_options
    )

    # The full resource name of the search app serving config
    serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

    # Refer to the `SearchRequest` reference for all supported fields:
    # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query="",
        # in this demo we only use the filters to get the list of rules.
        page_size=10,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
        filter=filter
    )

    result: list[Rules] = []

    search_result = client.search(request)
    for response in search_result:
        data = response.document.struct_data
        result.append(Rules(
            processing_rule=data['processing_rule'],
            processing_rule_tools=data['processing_rule_tools'],
            severity_determination_rule=data['severity_determination_rule'],
            severity_determination_rule_tools=data[
                'severity_determination_rule_tools'],
            source_document=response.id
        ))
    return result

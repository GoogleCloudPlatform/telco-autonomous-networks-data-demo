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
import os
import sys

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

location = 'global'

project_id = os.environ['PROJECT_ID']
engine_id = os.environ['VERTEX_AI_SEARCH_ENGINE_RCA_RULES']

search_query = sys.argv[1]

client_options = (
    ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    if location != "global"
    else None
)

# Create a client
client = discoveryengine.SearchServiceClient(client_options=client_options)

# The full resource name of the search app serving config
serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"

# Optional - only supported for unstructured data: Configuration options for search.
# Refer to the `ContentSearchSpec` reference for all supported fields:
# https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
    # For information about snippets, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/snippets
    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=True
    ),
    # For information about search summaries, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
    summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
        summary_result_count=5,
        include_citations=True,
        ignore_adversarial_query=True,
        ignore_non_summary_seeking_query=True,
        model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
            preamble="YOUR_CUSTOM_PROMPT"
        ),
        model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
            version="stable",
        ),
    ),
)

# Refer to the `SearchRequest` reference for all supported fields:
# https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
request = discoveryengine.SearchRequest(
    serving_config=serving_config,
    query=search_query,
    page_size=10,
    content_search_spec=content_search_spec,
    query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
        condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
    ),
    spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
        mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
    ),
    # Optional: Use fine-tuned model for this request
    # custom_fine_tuning_spec=discoveryengine.CustomFineTuningSpec(
    #     enable_search_adaptor=True
    # ),
)

page_result = client.search(request)

# print(page_result)
# Handle the response
for response in page_result:
    data = response.document.struct_data
    print(
        'ID: ' + response.id + '\n' +
        'Description: ' + data['description'] + '\n' +
        'Severity rule: ' + data['severity_determination_rule'] + '\n'
        'Processing rule: ' + data['processing_rule'] + '\n\n'
        )

# return page_result
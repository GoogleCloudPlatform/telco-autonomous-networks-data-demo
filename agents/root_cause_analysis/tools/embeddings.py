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

import logging
from google import genai
from google.genai.types import EmbedContentConfig, EmbedContentResponse, \
    HttpOptions
from typing import Optional

from root_cause_analysis.settings import settings

logger = logging.getLogger(__name__)

client = genai.Client(
    location="global",
    project=settings.project_id
)


def generate_embeddings_for_events(events: str) -> Optional[list[float]]:
    try:
        response: EmbedContentResponse = client.models.embed_content(
            model=settings.embeddings_model,
            contents=[events],
            config=EmbedContentConfig(
                http_options=HttpOptions(
                    # 60 seconds
                    timeout=60 * 1000
                ),
                task_type="SEMANTIC_SIMILARITY"
            ),
        )
        return response.embeddings[0].values
    except Exception as e:
        logger.error("Failed to generate embeddings: " + str(e))
        return None

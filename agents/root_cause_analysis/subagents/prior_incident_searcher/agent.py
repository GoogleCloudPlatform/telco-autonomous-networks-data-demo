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

from google.adk import Agent
from google.adk.tools import ToolContext

from root_cause_analysis.constants import KEY_INCIDENT_DATA, KEY_PRIOR_INCIDENTS
from root_cause_analysis.settings import settings
from root_cause_analysis.tools.bigquery_util import execute_query, \
    incidents_table
from root_cause_analysis.tools.embeddings import generate_embeddings_for_events

logger = logging.getLogger(__name__)


def build_prior_incidents_searcher():
    return Agent(
        model=settings.prior_incidents_searcher_model,
        name='prior_incidents_search_agent',
        description='Prior incident search agent',
        instruction='Retrieves the list of prior incidents that are similar to the current incident.',
        output_key=KEY_PRIOR_INCIDENTS,
        tools=[prior_incident_search],
        planner=settings.planner,
        generate_content_config=settings.content_config
    )


async def prior_incident_search(tool_context: ToolContext) -> dict:
    events = tool_context.state[KEY_INCIDENT_DATA]

    events_embeddings = generate_embeddings_for_events(events)
    if not events_embeddings:
        return {
            "status": "error",
            'description': 'Failed to generate embeddings for the event.'
        }

    # TODO: it might be a good idea to filter out based on the status also
    query = f"""
    SELECT distance, base.incident_id, base.start_ts, base.end_ts, base.status, base.description,
        base.events, base.kpi_missed, base.enodeb_id, base.cell_id, base.cause, base.severity, 
        base.final_analysis, base.preliminary_analysis, base.resolution 
        FROM VECTOR_SEARCH( 
        (SELECT * FROM `{incidents_table}` WHERE ARRAY_LENGTH(events_embeddings) > 0), 'events_embeddings', 
        (SELECT {events_embeddings} as embeddings), 'embeddings',
        top_k => {settings.similarity_search_max_number_of_incidents})
        WHERE distance <= {settings.similarity_search_cutoff_distance}
    """

    logger.info("About to do vector search: %s", query)

    result = []
    try:
        rows = execute_query(query)
        # TODO: this formatting is better be done by the LLM or in the model and raw data should be reported by the tool
        for row in rows:
            result.append(
                '*Incident ' + row.incident_id + '*\n' +
                '**Search distance**: ' + str(row.distance) + ' (' + (
                    'likely match' if row.distance < settings.similarity_search_likely_match_distance else 'somewhat similar') + ')\n' +
                '**Events**\n' + row.events + '\n' +
                '**Final analysis**\n' + (
                    row.final_analysis if row.final_analysis else 'Not yet determined') + '\n' +
                '**Cause**\n' + (
                    row.cause if row.cause else 'Not yet determined') + '\n' +
                '**Resolution**\n' + (
                    row.resolution if row.resolution else 'Not yet determined') + '\n'
            )
    except Exception as ex:
        logger.error("Call to find prior incidents failed: %s", str(ex))
        return {
            "status": "error", 'description': 'SQL call failed'
        }

    return {"status": "success", "prior_incidents": result} if (
        len(result) > 0) else {"status": "no similar incidents found"}

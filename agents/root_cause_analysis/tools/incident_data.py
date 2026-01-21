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
from google.adk.tools import ToolContext

from incident_detector.models import Incident
from root_cause_analysis.constants import KEY_INCIDENT_DATA, KEY_INCIDENT_INFO, \
    KEY_SEVERITY_LEVEL
from root_cause_analysis.tools.bigquery_util import incidents_table, \
    execute_query
from root_cause_analysis.tools.embeddings import generate_embeddings_for_events

logger = logging.getLogger(__name__)


async def add_new_incident_data_section(tool_context: ToolContext,
    section_name: str, details: str) -> None:
    incident_data = tool_context.state.get(KEY_INCIDENT_DATA, '')

    incident_data = (incident_data + ('\n\n' if incident_data else '') +
                     '**' + section_name + '**\n'
                     + details)

    tool_context.state[KEY_INCIDENT_DATA] = incident_data


async def update_incident(
    tool_context: ToolContext, report: str) -> dict:
    incident: Incident = Incident.model_validate_json(
        tool_context.state[KEY_INCIDENT_INFO])

    severity: str = tool_context.state[KEY_SEVERITY_LEVEL]

    events: str = tool_context.state[KEY_INCIDENT_DATA]
    event_embeddings: list[float] = generate_embeddings_for_events(events)
    if not event_embeddings:
        return {
            "status": "error",
            'description': 'Failed to generate embeddings for the event.'
        }

    try:
        # TODO: need to escape triple quotes
        query = f"""
        UPDATE `{incidents_table}` SET 
            status = 'ANALYZED',
            preliminary_analysis = r'''{report}''',
            severity = r'''{severity}''',
            events = r'''{events}''',
            events_embeddings = {event_embeddings}
        WHERE incident_id = '{incident.id}'
        """
        logger.debug("About to update an incident: %s", query)
        execute_query(query)
    except Exception as ex:
        logger.error("Call to update an incident failed: %s", str(ex))
        return {
            "status": "error", 'description': 'SQL call failed'
        }

    logger.info("Incident %s successfully updated", incident.id)

    return {'status': 'Success'}

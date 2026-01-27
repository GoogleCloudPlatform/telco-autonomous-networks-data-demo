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
from datetime import datetime
from typing import Optional

from google.adk.tools import ToolContext

from root_cause_analysis.constants import KEY_INCIDENT_INFO
from root_cause_analysis.models import Incident, MissedKPI
from root_cause_analysis.settings import settings
from root_cause_analysis.tools.bigquery_util import execute_query
from root_cause_analysis.tools.incident_data import \
    add_new_incident_data_section

logger = logging.getLogger(__name__)

DATE_FORMAT = "%c"


async def get_incident_info(tool_context: ToolContext,
    incident_id: str) -> dict:
    """
    Retrieve the incident information based on the incident id.

    :param tool_context: tool invocation context
    :param incident_id: ID of the incident

    :return: dictionary which contain the status of the retrieval and the incident info in case the search is successful.
    """

    incident: Optional[Incident] = None

    try:
        incidents_table = f"{settings.bigquery_data_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table_incidents}"

        query = f"""
       SELECT incident_id, enodeb_id, cell_id, start_ts, end_ts, status, description, kpi_missed
        FROM `{incidents_table}` WHERE incident_id = '{incident_id}'
        """

        logger.info("About to run query: %s", query)
        rows = execute_query(query=query)

        incident_start: datetime
        incident_end: datetime
        for row in rows:
            if incident:
                raise ValueError(
                    f'Retrieved more than one row for incident {incident_id}')

            incident_start = row.start_ts
            incident_end = row.end_ts

            missed_kpis = [
                MissedKPI(kpi=next_kpi['kpi'], value=next_kpi['value']) for
                next_kpi in row.kpi_missed]

            incident = Incident(
                id=row.incident_id,
                enodeb_id=row.enodeb_id,
                cell_id=row.cell_id,
                start_time=incident_start.strftime(DATE_FORMAT),
                end_time=incident_end.strftime(DATE_FORMAT) if row.end_ts
                else None,
                status=row.status,
                description=row.description,
                kpi_missed=missed_kpis
            )
    except Exception as ex:
        logger.error("Call to query an incident failed: %s", str(ex))
        return {
            "status": "error", 'description': 'SQL call failed'
        }

    if not incident:
        logger.warning("Couldn't find incident by id: %s", incident_id)
        return {
            "status": "not found",
            'description': f"Couldn't find incident with id {incident_id}"
        }

    logger.info("Incident %s successfully retrieved", incident_id)

    tool_context.state[KEY_INCIDENT_INFO] = incident.model_dump_json()

    await add_new_incident_data_section(
        tool_context, "General info",
        "Missed KPIs: " +
        ', '.join([kpi.to_descriptive_string() for kpi in
                   incident.kpi_missed]) + ". Duration: "
        + str((incident_end - incident_start).total_seconds()) + " seconds.")

    return {'status': 'success', 'incident': incident}

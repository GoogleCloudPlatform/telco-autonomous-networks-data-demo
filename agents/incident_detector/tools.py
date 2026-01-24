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

import logging
import uuid
from datetime import datetime, UTC
from google.adk.tools import ToolContext
from google.api_core.client_info import ClientInfo
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from google.cloud.bigquery.enums import JobCreationMode

from incident_detector.models import Incident, MissedKPI
from incident_detector.settings import settings

logger = logging.getLogger(__name__)

INCIDENTS_ATTR = 'incidents'

bigquery_client = bigquery.Client(client_info=ClientInfo(
    user_agent=settings.user_agent),
    default_job_creation_mode=JobCreationMode.JOB_CREATION_OPTIONAL
)

DATE_FORMAT = "%c"

# TODO: share these conversion utilities across agents.
_RFC3339_MICROS = "%Y-%m-%dT%H:%M:%S.%fZ"


def _timestamp_to_bigquery_format(value: str):
    """Coerce 'value' to an JSON-compatible representation."""
    timestamp = datetime.strptime(value, DATE_FORMAT)
    # For naive datetime objects UTC timezone is assumed, thus we format
    # those to string directly without conversion.
    if timestamp.tzinfo is not None:
        timestamp = timestamp.astimezone(UTC)
    result = timestamp.strftime(_RFC3339_MICROS)
    return result


async def get_potential_incidents(tool_context: ToolContext) -> dict:
    """
    Check for potential incidents and return them as a list.
    :param tool_context:
    :return: dictionary, with "status" attribute denoting the tool call success and "incidents" with the list of potential incidents
    """
    incidents = []
    try:
        performance_kpi_table = f"{settings.bigquery_data_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table_performance_kpi}"
        # This query is a bit simplistic. But for the purpose of this demo it's sufficient.
        # There is no check pointing - it scans all the data.
        # It assumes that the data points of KPIs dropping below the threshold are contiguous in time.
        # It's possible that there are multiple drop/back-to-normal jumps, etc.
        query = f"""
WITH missed_kpis AS (
SELECT 
    enodeb_id, 
    cell_id, 
    'erab_success_rate' as kpi, 
    ARRAY_AGG(measurement_end ORDER BY measurement_end) AS period,
    AVG(erab_success_rate) as kpi_value
  FROM `{performance_kpi_table}` WHERE erab_success_rate < 97
  GROUP BY enodeb_id, cell_id
)
SELECT 
    enodeb_id, cell_id, 
    'ERAB success rate is below 97%' as description,
    kpi, kpi_value,
    ARRAY_FIRST(period) as started, 
    ARRAY_LAST(period) as ended 
    FROM missed_kpis
"""
        logger.info("About to check for incidents: %s", query)
        rows = bigquery_client.query_and_wait(
            project=settings.bigquery_run_project_id,
            location=settings.bigquery_data_location,
            job_config=QueryJobConfig(
                job_timeout_ms=60 * 1000
            ),
            query=query
        )
        for row in rows:
            incidents.append(Incident(
                id=str(uuid.uuid4()),
                status='NEW',
                description=row.description,
                kpi_missed=[MissedKPI(kpi=row.kpi, value=row.kpi_value)],
                enodeb_id=row.enodeb_id,
                cell_id=row.cell_id,
                start_time=row.started.strftime(DATE_FORMAT),
                end_time=row.ended.strftime(DATE_FORMAT)
            )
            )
    except Exception as ex:
        logger.error("Call to retrieve incidents failed: %s", str(ex))
        return {
            "status": "error"
        }

    logger.info("Potential incidents: %s", incidents)
    tool_context.state[INCIDENTS_ATTR] = [incident.model_dump_json() for
                                          incident in incidents]
    return {
        "status": "success",
        "incidents": incidents
    }


async def create_new_incident(tool_context: ToolContext,
    incident_id: str) -> dict:
    incident: Optional[Incident] = None

    incidents: list[Incident] = [Incident.model_validate_json(incident_dict) for
                                 incident_dict in
                                 tool_context.state[INCIDENTS_ATTR]]
    for next_incident in incidents:
        next_incident:Incident
        if next_incident.id == incident_id:
            incident = next_incident
            break

    if not incident:
        logger.error("Unable to find incident by id %s ", incident_id)
        return {'status': "Failed", 'reason': 'Unable to find incident by provided id'}

    try:
        incidents_table = f"{settings.bigquery_data_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table_incidents}"

        missed_kpi_data = '[' + ','.join(
            [missed_kpi.as_bigquery_struct() for missed_kpi in
             incident.kpi_missed]) + ']'

        query = f"""
       INSERT INTO `{incidents_table}` (
        incident_id,
        EnodeB_id,
        cell_id,
        start_ts,
        end_ts,
        status,
        description,
        kpi_missed
        )
        VALUES (
            '{incident.id}',
            '{incident.enodeb_id}',
            '{incident.cell_id}',
            '{_timestamp_to_bigquery_format(incident.start_time)}',
            '{_timestamp_to_bigquery_format(incident.end_time)}',
            '{incident.status}',
            '{incident.description}',
            {missed_kpi_data}
        )"""
        logger.info("About to insert an incident: %s", query)
        bigquery_client.query_and_wait(
            project=settings.bigquery_run_project_id,
            location=settings.bigquery_data_location,
            job_config=QueryJobConfig(
                job_timeout_ms=60 * 1000
            ),
            query=query
        )
    except Exception as ex:
        logger.error("Call to save an incident failed: %s", str(ex))
        return {
            "status": "error", 'description': 'SQL call failed'
        }

    logger.info("Incident %s successfully created", incident_id)

    return {'status': 'Success'}

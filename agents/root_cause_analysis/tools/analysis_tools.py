#  Copyright 2026 Google LLC
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
from typing import override, Optional

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import BaseTool, ToolContext, FunctionTool
from google.adk.tools.base_toolset import BaseToolset

from root_cause_analysis.constants import KEY_INCIDENT_INFO, \
    KEY_ACTIONS
from root_cause_analysis.models import CellTracesStats, Incident, Action
from root_cause_analysis.tools.bigquery_util import \
    timestamp_to_bigquery_format, execute_query, cell_traces_table
from root_cause_analysis.tools.incident_data import \
    add_new_incident_data_section

logger = logging.getLogger(__name__)


async def get_cell_trace_statistics(tool_context: ToolContext) -> list[
    CellTracesStats]:
    """
    Get the cell trace statistics for the current incident.

    This tool doesn't need the details of the incident to passed as parameter.

    :param tool_context:
    :return:
    """
    incident: Incident = Incident.model_validate_json(
        tool_context.state[KEY_INCIDENT_INFO])

    incident_start: str = timestamp_to_bigquery_format(incident.start_time)
    incident_end: str = timestamp_to_bigquery_format(incident.end_time)

    try:
        query = f"""
        SELECT s1_sig_conn_setup_sig_conn_result connection_outcome, COUNT(*) number_of_outcomes 
            FROM `{cell_traces_table}`   
            WHERE start_enodeb_id = '{incident.enodeb_id}' AND start_cell_id = '{incident.cell_id}' AND
                starttime >= '{incident_start}' AND endtime <= '{incident_end}'
            GROUP BY s1_sig_conn_setup_sig_conn_result
        """

        rows = execute_query(query)

        result: list[CellTracesStats] = []
        text_results: list[str] = []
        for row in rows:
            stats = CellTracesStats(connection_outcome=row.connection_outcome,
                                    count=row.number_of_outcomes)
            result.append(stats)
            text_results.append(
                stats.connection_outcome + ': ' +
                str(stats.count))

        await add_new_incident_data_section(
            tool_context, "Cell traces statistics",
            ', '.join(text_results)
        )

    except Exception as ex:
        logger.error("Call to query an incident failed: %s", str(ex))
        return {
            "status": "error", 'description': 'SQL call failed'
        }

    logger.info("Cell trace statistics successfully retrieved: %s", str(result))

    return {'status': 'Success' if result else 'No cell traces found', 'cell_trace_statistics': result}


async def get_uplink_rssi_level(tool_context: ToolContext, enodeb_id: str,
    cell_id: str) -> dict:
    """
    Get the signal strength of the uplink signal for a particular cell
    """

    return {"status": "success", "uplink_signal_strenght": "-100"}


async def get_uplink_configuration(tool_context: ToolContext, enodeb_id: str,
    cell_id: str) -> dict:
    return {"status": "success", "pZeroNominalPucch": "-110",
            "pZeroNominalPusch": "-94"}


async def initiate_uplink_configuration_adjustment(tool_context: ToolContext,
    enodeb_id: str, cell_id: str) -> dict:
    """
    Sends the signal to adjust the uplink configuration.

    :param tool_context: context of the request
    :param enodeb_id: eNode to adjust
    :param cell_id: Cell to adjust
    :return: Confirmation that the adjustment started
    """
    return {"status": "success",
            "details": "Uplink adjustment request has been issued. It can take up to an hour for the changes to take the effect."}


available_tools: list[FunctionTool] = [
    FunctionTool(func=get_cell_trace_statistics),
    FunctionTool(func=get_uplink_configuration),
    FunctionTool(func=get_uplink_rssi_level),
    FunctionTool(func=initiate_uplink_configuration_adjustment),
]


class AnalysisToolset(BaseToolset):
    def __init__(
        self,
        state_key: str
    ):
        super().__init__()
        self.state_key = state_key

    @override
    async def get_tools(
        self,
        readonly_context: Optional[ReadonlyContext] = None,
    ) -> list[BaseTool]:
        if not readonly_context:
            return available_tools

        required_tools = readonly_context.state[self.state_key]

        result = []
        for tool in available_tools:
            if tool.func.__name__ in required_tools:
                result.append(tool)

        return result


class AutomaticActionToolset(BaseToolset):
    @override
    async def get_tools(
        self,
        readonly_context: Optional[ReadonlyContext] = None,
    ) -> list[BaseTool]:
        if not readonly_context:
            return available_tools

        required_tools = [Action.model_validate_json(action_json).tool_name
                          for action_json in
                          readonly_context.state[KEY_ACTIONS]]

        result = []
        for tool in available_tools:
            if tool.func.__name__ in required_tools:
                result.append(tool)

        return result


automatic_action_toolset = AutomaticActionToolset()

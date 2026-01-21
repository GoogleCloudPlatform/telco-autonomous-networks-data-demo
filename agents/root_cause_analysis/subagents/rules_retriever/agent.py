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
from google.adk.agents import BaseAgent, InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from typing import AsyncGenerator, override

from root_cause_analysis.constants import KEY_INCIDENT_INFO, \
    KEY_PROCESSING_RULES, KEY_SEVERITY_DETERMINATION_RULES, \
    KEY_PROCESSING_RULES_TOOLS, KEY_SEVERITY_DETERMINATION_RULES_TOOLS
from root_cause_analysis.models import Incident, Rules
from root_cause_analysis.tools.vertex_ai_search import find_rca_rules


class ProcessingRulesRetrieverAgent(BaseAgent):

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        incident: Incident = Incident.model_validate_json(
            ctx.session.state[KEY_INCIDENT_INFO])
        if not incident:
            yield Event(
                model_version="custom",
                author=self.name,
                content=Content(
                    parts=[Part.from_text(
                        text="Unable to find the incident details.")]
                ),
                invocation_id=ctx.invocation_id,
                branch=ctx.branch
            )
            return

        rules: list[Rules] = await find_rca_rules(incident.kpi_missed)

        processing_rules = [rule.processing_rule for rule in rules]
        severity_determination_rules = [rule.severity_determination_rule for
                                        rule in rules]

        processing_rule_tools = set()
        severity_determination_rule_tools = set()
        for rule in rules:
            [processing_rule_tools.add(tool) for tool in
             rule.processing_rule_tools]
            [severity_determination_rule_tools.add(tool) for tool in
             rule.severity_determination_rule_tools]

        state_changes = {
            KEY_PROCESSING_RULES: processing_rules,
            # Sets are not serializable. Convert to list
            KEY_PROCESSING_RULES_TOOLS: [tool for tool in processing_rule_tools],
            KEY_SEVERITY_DETERMINATION_RULES: severity_determination_rules,
            # Sets are not serializable. Convert to list
            KEY_SEVERITY_DETERMINATION_RULES_TOOLS: [tool for tool in severity_determination_rule_tools]
        }
        event_actions: EventActions = EventActions(state_delta=state_changes)

        yield Event(
            model_version="custom",
            author=self.name,
            content=Content(
                parts=[Part.from_text(
                    text="Successfully retrieved processing rules.")]
            ),
            invocation_id=ctx.invocation_id,
            branch=ctx.branch,
            actions=event_actions
        )


def build_rules_retriever_agent():
    return ProcessingRulesRetrieverAgent(
        name='processing_rules_retriever',
        description="Retrieves rules specific to the current incident"
    )

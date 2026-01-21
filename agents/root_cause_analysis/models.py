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

from pydantic import BaseModel, Field, model_validator
from typing import Optional, Set, Self

class CellTracesStats(BaseModel):
    connection_outcome: Optional[str]
    count: int

    @model_validator(mode='after')
    def set_defaults(self) -> Self:
        if not self.connection_outcome:
            self.connection_outcome = 'OTHER'
        return self

class MissedKPI(BaseModel):
    kpi: str = Field('KPI ID')
    value: float = Field("Value of the KPI")

    def to_descriptive_string(self) -> str:
        return f"{self.kpi} (value={self.value})"

class Incident(BaseModel):
    id: str = Field("Unique incident id")
    description: str = Field("Initial incident assessment")
    severity: Optional[str] = Field("Estimated severity of the incident")
    kpi_missed: list[MissedKPI] = Field("List of KPIs missed")
    enodeb_id: Optional[str] = Field("EnodeB where the KPI failed")
    cell_id: Optional[str] = Field("Cell id where the KPI failed")
    status: str = Field("Status of the incident")
    start_time: str = Field("Start time of the incident")
    end_time: Optional[str] = Field("End time of the incident")

class Document(BaseModel):
    url: str
    title: str

class ExternalSearchResult(BaseModel):
    search_results: str = Field(description="Results of the search")
    references: list[Document] = Field(description="References used in grounding")


class InternalSearchResult(BaseModel):
    queries: list[str] = Field(description="Queries used to search")
    search_result: str = Field(description="Results of an internal search")
    references: list[Document] = Field(description="References used in grounding")

class Rules(BaseModel):
    processing_rule: str
    processing_rule_tools: Set[str]
    severity_determination_rule: str
    severity_determination_rule_tools: Set[str]
    source_document: str


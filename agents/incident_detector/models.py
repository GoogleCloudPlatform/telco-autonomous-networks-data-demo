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
from pydantic import BaseModel, Field
from typing import Optional


class MissedKPI(BaseModel):
    kpi: str = Field('KPI ID')
    value: float = Field("Value of the KPI")

    def as_bigquery_struct(self) -> str:
        return f"STRUCT( '{self.kpi}' as kpi, {self.value} as value)"


class Incident(BaseModel):
    id: str = Field("Unique incident id")
    description: str = Field("Initial incident assessment")
    kpi_missed: list[MissedKPI] = Field("List of KPIs missed")
    enodeb_id: Optional[str] = Field("EnodeB where the KPI failed")
    cell_id: Optional[str] = Field("Cell id where the KPI failed")
    status: str = Field("Status of the incident")
    start_time: str = Field("Start time of the incident")
    end_time: Optional[str] = Field("End time of the incident")

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
from datetime import datetime, UTC

from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from google.cloud.bigquery.enums import JobCreationMode
from google.cloud.bigquery.table import RowIterator

from root_cause_analysis.settings import settings

DATE_FORMAT = "%c"

_RFC3339_MICROS = "%Y-%m-%dT%H:%M:%S.%fZ"


def escape_single_quote(literal: str) -> str:
    return literal.replace("'", "\\'")


def timestamp_to_bigquery_format(value: str):
    """Coerce 'value' to an JSON-compatible representation."""
    timestamp = datetime.strptime(value, DATE_FORMAT)
    # For naive datetime objects UTC timezone is assumed, thus we format
    # those to string directly without conversion.
    if timestamp.tzinfo is not None:
        timestamp = timestamp.astimezone(UTC)
    result = timestamp.strftime(_RFC3339_MICROS)
    return result


incidents_table = f"{settings.bigquery_data_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table_incidents}"
cell_traces_table = f"{settings.bigquery_data_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table_cell_traces}"

bigquery_client = bigquery.Client(
    client_info=settings.api_client_info,
    default_job_creation_mode=JobCreationMode.JOB_CREATION_OPTIONAL
)


def execute_query(query: str) -> RowIterator:
    return bigquery_client.query_and_wait(
        project=settings.bigquery_run_project_id,
        location=settings.bigquery_data_location,
        job_config=QueryJobConfig(
            job_timeout_ms=60 * 1000
        ),
        query=query
    )

#!/usr/bin/env bash

#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -e
set -u

source ./.cloud-env.sh

bq load --source_format=CSV --source_column_match=NAME --ignore_unknown_values=True \
  --timestamp_format="MM/DD/YYYY HH24:MI:SS" \
"${BIGQUERY_DATA_PROJECT_ID}:${BIGQUERY_DATASET}.${BIGQUERY_TABLE_PERFORMANCE}" data/performance.csv
#!/usr/bin/env bash

#
# Copyright 2025 Google LLC
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

for file in data/rca-rules/*.json; do
    if [ -f "$file" ]; then
        echo "Loading rules from: $file"

        filename="${file##*/}"
        name_without_ext="${filename%.*}"
        document_id=$name_without_ext

        curl -X PATCH \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        "https://discoveryengine.googleapis.com/v1beta/projects/${PROJECT_ID}/locations/global/collections/default_collection/dataStores/${VERTEX_AI_DATASTORE_RCA_RULES}/branches/0/documents/${document_id}?allowMissing=true" \
        -d "{
          "structData": $(cat $file)
        }"
    fi
done

exit 0



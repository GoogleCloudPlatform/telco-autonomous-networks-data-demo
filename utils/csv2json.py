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

import csv
import json
import sys


def csv_to_jsonl(csv_filepath, jsonl_filepath):
    """
    Converts a CSV file to a new-line delimited JSON (JSONL) file.

    Args:
        csv_filepath (str): The path to the input CSV file.
        jsonl_filepath (str): The path to the output JSONL file.
    """
    try:
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            with open(jsonl_filepath, mode='w', encoding='utf-8') as outfile:
                for row in reader:
                    json_line = json.dumps(row)
                    outfile.write(json_line + '\n')
        print(f"Successfully converted '{csv_filepath}' to '{jsonl_filepath}'")
    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    csv_to_jsonl(sys.argv[1], sys.argv[2])

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

from google.adk import Agent

from root_cause_analysis.constants import KEY_INCIDENT_INFO, \
    KEY_EXTERNAL_SEARCH_RESULTS, KEY_INTERNAL_SEARCH_RESULTS, \
    KEY_PRIOR_INCIDENTS, KEY_ANALYSIS, KEY_SEVERITY_LEVEL, \
    KEY_SEVERITY_EXPLANATION
from root_cause_analysis.settings import settings


def build_report_generator():
    return Agent(
        model=settings.report_generator_model,
        name='report_generator_agent',
        description='Generates the root cause analysis report based on all the inputs collected in prior steps.',
        instruction=f'''
Produce a report that describes the current incident.

Only use the information below to generate the report.

*Current incident:*: 
{{{KEY_INCIDENT_INFO}}}

*Root cause analysis:*
{{{KEY_ANALYSIS}}}

*Severity:*
{{{KEY_SEVERITY_LEVEL}}}. 

*Why this severity was chosen:*
{{{KEY_SEVERITY_EXPLANATION}}}

*External documentation:*: 
{{{KEY_EXTERNAL_SEARCH_RESULTS}?}}

*Internal documentation:*: 
{{{KEY_INTERNAL_SEARCH_RESULTS}?}}

**Prior incidents:**: 
{{{KEY_PRIOR_INCIDENTS}?}}


**Your instructions:**
    
The report should contain the following sections:
1. Incident description
2. Root cause analysis
3. Severity level
4. Similar prior incidents
5. Internal documentation
6. External documentation
7. Recommendations
8. List of references from the internal and external search results. Present the references as Markdown link tags. Use "url" and "title" values of the reference as the title and the URL of the tag.

You MUST generate all the sections of the report. If there is nothing to state in a particular section, still include it and indicate that there is no relevant information.
    ''',
        planner=settings.planner,
        generate_content_config=settings.content_config
    )

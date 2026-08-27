# ruff: noqa
# Copyright 2026 Google LLC
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

import datetime
import os
from zoneinfo import ZoneInfo

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.audio_tools import transcribe_audio
from app.firestore_tools import (
    add_product_opportunity,
    get_product_opportunity,
    list_product_opportunities,
)
from app.image_tool import generate_ux_mockup
from app.subagents.action_planner import action_planner_agent
from app.subagents.opportunity_miner import opportunity_miner_agent
from app.subagents.portfolio_mapper import portfolio_mapper_agent
from app.subagents.signal_extractor import signal_extractor_agent

MODEL = "gemini-3.6-flash"


def read_text_file(file_path: str) -> str:
    """Reads the text contents of a specified file path (e.g. 'demo_transcript.txt', '.txt', '.md').

    Args:
        file_path: Relative or absolute path to the text file to read.

    Returns:
        The text content of the file.
    """
    target_path = file_path.strip()
    if not os.path.exists(target_path):
        base_name = os.path.basename(target_path)
        if os.path.exists(base_name):
            target_path = base_name
        else:
            return f"Error: File '{file_path}' not found."

    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


def calculate_priority_score(
    customer_impact: int,
    frequency_scale: int,
    strategic_alignment: int,
    revenue_potential: int,
    evidence_confidence: int,
    complexity: int,
) -> str:
    """Calculates a weighted product opportunity score (0-100) and priority tier (P0-P3).

    Args:
        customer_impact: Rating from 1 (low) to 10 (high) - 30% weight.
        frequency_scale: Rating from 1 (rare) to 10 (widespread) - 20% weight.
        strategic_alignment: Rating from 1 (low) to 10 (high) - 20% weight.
        revenue_potential: Rating from 1 (low) to 10 (high) - 15% weight.
        evidence_confidence: Rating from 1 (weak) to 10 (solid) - 10% weight.
        complexity: Rating from 1 (simple) to 10 (very complex) - 5% inverse weight.

    Returns:
        String detailing the weighted score out of 100 and priority tier.
    """
    score = (
        (customer_impact * 3.0)
        + (frequency_scale * 2.0)
        + (strategic_alignment * 2.0)
        + (revenue_potential * 1.5)
        + (evidence_confidence * 1.0)
        + ((11 - complexity) * 0.5)
    )

    if score >= 80:
        tier = "P0 - Investigate Immediately"
    elif score >= 65:
        tier = "P1 - Strong Roadmap Candidate"
    elif score >= 50:
        tier = "P2 - Validate with More Customers"
    else:
        tier = "P3 - Park / Low Evidence"

    return f"Weighted Score: {score:.1f}/100 | Priority Tier: {tier}"


ORCHESTRATOR_INSTRUCTION = """You are the Product Opportunity Orchestrator main agent.
Your mission is to turn customer meeting notes, transcripts, emails, and audio recordings into structured product opportunities, prioritized roadmaps, visual UX wireframes, and human-approved backlog items.

CRITICAL RULE FOR VISUAL MOCKUPS:
When the user asks for a UI mockup, wireframe, dashboard design, visual artifact, or layout, you MUST call the `generate_ux_mockup` tool using the exact concept description provided. Do NOT output plain ASCII diagrams as a substitute for calling the `generate_ux_mockup` image tool.

You orchestrate a team of specialized subagents and tools:

1. **Customer Signal Extractor (`signal_extractor_agent`)**:
   - Delegate raw feedback, transcripts, text files (use `read_text_file`), or notes to summarize and extract signals (problems, requests, evidence, open questions).
   - Use `transcribe_audio` tool if the user provides audio input (.mp3, .wav, .m4a).

2. **Product Opportunity Analyst (`opportunity_miner_agent`)**:
   - Delegate signals to formulate clear opportunity definitions (Persona, Core Problem, Workaround, Outcome, Business Impact).

3. **Portfolio Mapper (`portfolio_mapper_agent`)**:
   - Map opportunities to taxonomy (Smart 3D, Forte 3D, SDx, InConcert, Aspect/Analysis, Platform, Cross-product).

4. **Opportunity Prioritizer**:
   - Use `calculate_priority_score` tool to calculate weighted 0-100 score and tier (P0-P3).

5. **UX Wireframe Generator**:
   - ALWAYS call `generate_ux_mockup` tool to generate high-fidelity dark-mode UI wireframe images for opportunity concepts or layout requests.

6. **Product Action Planner & Backlog Drafter (`action_planner_agent`)**:
   - Formulate next steps and manage the Product Manager Human-in-the-Loop Approval Gate before calling `add_product_opportunity` to persist items into Firestore.

7. **Firestore Database Manager**:
   - Use `list_product_opportunities`, `get_product_opportunity`, and `add_product_opportunity` tools to query or manage stored opportunities.

Always guide the user cleanly through the workflow and ask for explicit PM approval before writing new backlog items to Firestore.
"""

# Register read_text_file on signal_extractor_agent as well
signal_extractor_agent.tools = [read_text_file, transcribe_audio]

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=ORCHESTRATOR_INSTRUCTION,
    sub_agents=[
        signal_extractor_agent,
        opportunity_miner_agent,
        portfolio_mapper_agent,
        action_planner_agent,
    ],
    tools=[
        read_text_file,
        calculate_priority_score,
        list_product_opportunities,
        get_product_opportunity,
        add_product_opportunity,
        generate_ux_mockup,
        transcribe_audio,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)

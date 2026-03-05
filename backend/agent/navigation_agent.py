"""
Navigation Copilot Agent
Built with Google Agent Development Kit (ADK).
"""

import json
import re
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent.prompts import NAVIGATION_AGENT_SYSTEM_PROMPT
from tools.routes import get_route, sample_route_coordinates
from tools.places import (
    search_places,
    search_places_along_route,
    search_places_near_point,
)
from tools.detour import calculate_detour, optimize_stops, suggest_contextual_stops

# ---------------------------------------------------------------------------
# ADK Agent definition
# ---------------------------------------------------------------------------

navigation_agent = Agent(
    name="navigation_copilot",
    model="gemini-2.5-flash",
    instruction=NAVIGATION_AGENT_SYSTEM_PROMPT,
    tools=[
        get_route,
        search_places,
        search_places_along_route,
        search_places_near_point,
        calculate_detour,
        optimize_stops,
        suggest_contextual_stops,
    ],
)

# Shared session service — keeps conversation context across queries
_session_service = InMemorySessionService()

# Counter for unique session IDs when conversation context is not needed
_session_counter = 0


async def run_agent(query: str) -> dict:
    """
    Process a natural-language navigation query through the ADK agent.

    Args:
        query: The user's navigation query
              (e.g. "Find cafes along my route to Lulu Mall")

    Returns:
        Structured dict with keys: summary, places, route, suggestions
    """
    global _session_counter
    _session_counter += 1

    session = await _session_service.create_session(
        app_name="navigation_copilot",
        user_id="web_user",
    )

    runner = Runner(
        agent=navigation_agent,
        app_name="navigation_copilot",
        session_service=_session_service,
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=query)],
    )

    final_text = ""
    async for event in runner.run_async(
        user_id="web_user",
        session_id=session.id,
        new_message=user_message,
    ):
        # Debug: log every event
        print(f"[AGENT EVENT] author={event.author}, is_final={event.is_final_response()}")
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"  [TEXT] {part.text[:200]}")
                if part.function_call:
                    print(f"  [TOOL CALL] {part.function_call.name}({part.function_call.args})")
                if part.function_response:
                    resp_str = str(part.function_response.response)
                    print(f"  [TOOL RESPONSE] {resp_str[:200]}")

        if event.is_final_response():
            for part in event.content.parts:
                if part.text:
                    final_text += part.text

    # Try to extract structured JSON from the agent's text response
    return _parse_agent_response(final_text, query)


def _parse_agent_response(text: str, original_query: str) -> dict:
    """
    Attempt to parse structured JSON from the agent response.
    Falls back to a text-only summary if no JSON is found.
    """
    # Try to find JSON block in the response
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            return {
                "summary": parsed.get("summary", text),
                "places": parsed.get("places", []),
                "route": parsed.get("route"),
                "suggestions": parsed.get("suggestions", []),
            }
        except json.JSONDecodeError:
            pass

    # Fallback: return the text as a summary
    return {
        "summary": text or f"Processed query: {original_query}",
        "places": [],
        "route": None,
        "suggestions": [],
    }

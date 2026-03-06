"""
Navigation Copilot Agent
Built with Google Agent Development Kit (ADK).
Includes throttling, caching, and retry logic per fix.md.
"""

import asyncio
import json
import re
import time

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
    model="gemini-3.1-flash-lite",
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

# Counter for unique session IDs
_session_counter = 0

# ---------------------------------------------------------------------------
# Fix 1: Request throttling — limit concurrent Gemini calls (fix.md §1)
# ---------------------------------------------------------------------------
_gemini_semaphore = asyncio.Semaphore(1)  # Only 1 concurrent agent call

# ---------------------------------------------------------------------------
# Fix 2: Response caching — cache identical queries (fix.md §2)
# ---------------------------------------------------------------------------
_cache: dict[str, tuple[dict, float]] = {}  # {query: (result, timestamp)}
CACHE_TTL_SECONDS = 300  # 5-minute cache


async def run_agent(query: str) -> dict:
    """
    Process a natural-language navigation query through the ADK agent.
    Includes throttling, caching, and retry with exponential backoff.

    Args:
        query: The user's navigation query

    Returns:
        Structured dict with keys: summary, places, route, suggestions
    """
    # --- Cache check ---
    cache_key = query.strip().lower()
    if cache_key in _cache:
        cached_result, cached_time = _cache[cache_key]
        if time.time() - cached_time < CACHE_TTL_SECONDS:
            return cached_result

    # --- Throttled + retried execution ---
    result = await _throttled_run(query)

    # --- Store in cache ---
    _cache[cache_key] = (result, time.time())
    return result


async def _throttled_run(query: str) -> dict:
    """Run the agent with concurrency throttling, cooldown, and retry logic."""
    async with _gemini_semaphore:
        # Proactive 12s cooldown before each call to stay under RPM limits (fix.md §1)
        await asyncio.sleep(12)
        return await _run_with_retry(query, max_retries=3)


# ---------------------------------------------------------------------------
# Fix 5: Automatic retry with exponential backoff (fix.md §5)
# ---------------------------------------------------------------------------
async def _run_with_retry(query: str, max_retries: int = 3) -> dict:
    """Run the agent, retrying on 429 / ResourceExhausted errors."""
    for attempt in range(max_retries + 1):
        try:
            return await _execute_agent(query)
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = "429" in error_str or ("resource" in error_str and "exhausted" in error_str)
            if is_rate_limit and attempt < max_retries:
                delay = 10 * (2 ** attempt)  # 10s, 20s, 40s, 80s, 160s
                print(f"[RETRY] Gemini rate limited. Waiting {delay}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                continue
            # Not a rate limit error, or retries exhausted
            print(f"[ERROR] Agent failed: {e}")
            return {
                "summary": "Sorry, the AI service is temporarily busy. Please try again in a moment.",
                "places": [],
                "route": None,
                "suggestions": [],
            }

    # Should not reach here
    return {
        "summary": "Sorry, something went wrong. Please try again.",
        "places": [],
        "route": None,
        "suggestions": [],
    }


async def _execute_agent(query: str) -> dict:
    """Core agent execution logic — one attempt."""
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

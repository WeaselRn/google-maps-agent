"""
Navigation Copilot Agent
Built with Google Agent Development Kit (ADK).
Includes throttling, caching, retry, session reuse,
and max iteration cap per fix.md.
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

# ---------------------------------------------------------------------------
# Session reuse — one session per user (fix.md: "one session per user")
# ---------------------------------------------------------------------------
_session_service = InMemorySessionService()
_user_sessions: dict[str, str] = {}  # {user_id: session_id}

# Max tool-call iterations per query (fix.md: cap at 2 to prevent loops)
MAX_AGENT_ITERATIONS = 2

# ---------------------------------------------------------------------------
# Fix 1: Request throttling (fix.md)
# ---------------------------------------------------------------------------
_gemini_semaphore = asyncio.Semaphore(1)

# Fix 3: Adaptive cooldown — only wait remaining time since last call
_last_call_time: float = 0
MIN_CALL_INTERVAL = 12  # seconds (60 / 5 RPM)

# ---------------------------------------------------------------------------
# Fix 2: Response caching (fix.md)
# ---------------------------------------------------------------------------
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL_SECONDS = 300


async def run_agent(query: str) -> dict:
    """
    Process a navigation query with throttling, caching, retry,
    session reuse, and iteration capping.
    """
    # --- Cache check (fix.md §2: include user_id in key) ---
    user_id = "web_user"
    cache_key = f"{user_id}:{query.strip().lower()}"
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
    """Throttled execution with adaptive cooldown and global timeout."""
    async with _gemini_semaphore:
        # Fix 3: Adaptive cooldown — only wait the remaining time
        global _last_call_time
        now = time.time()
        wait = max(0, MIN_CALL_INTERVAL - (now - _last_call_time))
        if wait > 0:
            await asyncio.sleep(wait)
        _last_call_time = time.time()

        # Fix 5: Global 30s timeout so agent never hangs
        try:
            return await asyncio.wait_for(
                _run_with_retry(query, max_retries=3),
                timeout=30,
            )
        except asyncio.TimeoutError:
            print("[TIMEOUT] Agent exceeded 30s")
            return {
                "summary": "Request timed out. Please try a simpler query.",
                "places": [],
                "route": None,
                "suggestions": [],
            }


async def _run_with_retry(query: str, max_retries: int = 3) -> dict:
    """Retry on 429 / ResourceExhausted with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return await _execute_agent(query)
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = "429" in error_str or ("resource" in error_str and "exhausted" in error_str)
            if is_rate_limit and attempt < max_retries:
                delay = 10 * (2 ** attempt)
                print(f"[RETRY] Rate limited. Waiting {delay}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                continue
            print(f"[ERROR] Agent failed: {e}")
            return {
                "summary": "Sorry, the AI service is temporarily busy. Please try again in a moment.",
                "places": [],
                "route": None,
                "suggestions": [],
            }

    return {
        "summary": "Sorry, something went wrong. Please try again.",
        "places": [],
        "route": None,
        "suggestions": [],
    }


async def _execute_agent(query: str) -> dict:
    """
    Core agent execution with session reuse and iteration cap.
    Reuses the same session for the same user (fix.md: session reuse).
    Caps tool iterations to MAX_AGENT_ITERATIONS (fix.md: prevent loops).
    """
    user_id = "web_user"

    # Reuse existing session or create one (fix.md: one session per user)
    if user_id not in _user_sessions:
        session = await _session_service.create_session(
            app_name="navigation_copilot",
            user_id=user_id,
        )
        _user_sessions[user_id] = session.id
    session_id = _user_sessions[user_id]

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
    tool_call_count = 0

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        # Fix 1: Count tool calls, return early at limit (fix.md: use >=)
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    tool_call_count += 1
                    if tool_call_count >= MAX_AGENT_ITERATIONS:
                        print(f"[CAP] Tool iteration limit reached ({MAX_AGENT_ITERATIONS})")
                        return _parse_agent_response(final_text, query)

        if event.is_final_response():
            for part in event.content.parts:
                if part.text:
                    final_text += part.text

    return _parse_agent_response(final_text, query)


def _parse_agent_response(text: str, original_query: str) -> dict:
    """Parse structured JSON from agent response, with text fallback."""
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

    return {
        "summary": text or f"Processed query: {original_query}",
        "places": [],
        "route": None,
        "suggestions": [],
    }

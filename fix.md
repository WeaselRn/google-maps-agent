The subtle issue: Agent tool loops

You’re using an agent with multiple tools:

tools=[
    get_route,
    search_places,
    search_places_along_route,
    search_places_near_point,
    calculate_detour,
    optimize_stops,
    suggest_contextual_stops,
]

When an agent like this runs in frameworks similar to what you’re using, the LLM can do:

LLM reasoning
→ call tool
→ tool result
→ LLM reasoning
→ call another tool
→ tool result
→ final answer

Each reasoning step = another model call.

So one user query may become:

1️⃣ plan
2️⃣ call get_route
3️⃣ analyze route
4️⃣ call search_places
5️⃣ analyze results
6️⃣ summarize

That is 4–6 Gemini calls for one request.

Your throttling only wraps:

await _execute_agent(query)

But inside runner.run_async() the agent may call Gemini multiple times.

Evidence in your code

This loop:

async for event in runner.run_async(...)

is where the agent performs multiple model steps internally.

Your semaphore protects one agent run, not each internal model call.

How to dramatically reduce calls

For a navigation copilot, the agent should not decide routing tools dynamically.

Instead use a deterministic pipeline:

User query
↓
Extract intent
↓
Call routing tools directly
↓
Send final context to Gemini once

Example flow:

User: "Find coffee shops along my route to Kochi"

1️⃣ get_route(origin, destination)
2️⃣ search_places_along_route(route, "coffee")
3️⃣ Gemini summarizes results

That becomes 1 Gemini call instead of 5.

Minimal change to your code

Add max tool iterations if the framework supports it.

Example pattern:

navigation_agent = Agent(
    name="navigation_copilot",
    model="gemini-3.1-flash-lite",
    instruction=NAVIGATION_AGENT_SYSTEM_PROMPT,
    tools=[...],
    max_iterations=2
)

This prevents runaway loops.

Another improvement

Your cooldown is very conservative:

await asyncio.sleep(12)

With 5 RPM you only need:

60 / 5 = 12 seconds

So it’s correct — but once you get higher quota you can drop it to 1–2 seconds.

One more hidden issue

You create a new session for every query:

session = await _session_service.create_session(...)

That means the model loses conversation context, so it often:

re-plans

re-calls tools

re-reasons

Which increases calls.

Better:

one session per user
The biggest improvement for your project

For a maps AI agent, the best architecture is:

Frontend
↓
Backend intent parser
↓
Routing + place search tools
↓
Gemini explanation (single call)
Your cooldown timestamp updates before the request finishes:

_last_call_time = time.time()

If the agent runs for 20 seconds, the next request may start immediately, exceeding RPM.

Better:

start = time.time()

result = await asyncio.wait_for(
    _run_with_retry(query, max_retries=3),
    timeout=30,
)

_last_call_time = time.time()
return result

So the interval counts after the call finishes.

⚠️ Cache memory growth

Your cache never expires entries.

You check TTL but don’t delete old keys.

Eventually memory grows.

Add cleanup:

def _cleanup_cache():
    now = time.time()
    expired = [k for k,v in _cache.items() if now - v[1] > CACHE_TTL_SECONDS]
    for k in expired:
        del _cache[k]

Call it occasionally.

⚠️ Parsing JSON from LLM output

This regex can sometimes grab invalid JSON:

re.search(r'\{[\s\S]*\}', text)

Safer pattern:

re.search(r'\{.*\}', text, re.DOTALL)

Or instruct the agent to return strict JSON.
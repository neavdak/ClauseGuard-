"""Fast connectivity check for Nebius Token Factory and Tavily.

Usage:  python scripts/check_keys.py
Makes one tiny call to each service (cheap: a few tokens / one search).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clauseguard import tavily  # noqa: E402
from clauseguard.config import settings  # noqa: E402
from clauseguard.llm import Router  # noqa: E402

print("== Nebius Token Factory ==")
if settings.mock_mode:
    print("  SKIP - no NEBIUS_API_KEY in .env (or MOCK_MODE enabled)")
else:
    try:
        router = Router(force_discover=True)
        print("  OK - connected")
        for tier in ("nano", "super", "ultra", "vl"):
            print(f"    {tier:5s} -> {router.tiers.get(tier) or '(not found)'}")
        reply = router.complete(
            "nano",
            [
                {"role": "system", "content": "Reply with the single word: ok"},
                {"role": "user", "content": "ping"},
            ],
            purpose="connectivity",
            json_mode=False,
            max_tokens=5,
        )
        print(f"  live inference reply: {reply.strip()[:40]!r}")
    except Exception as exc:
        print(f"  FAIL - {exc}")

print("\n== Tavily ==")
if not settings.tavily_key:
    print("  SKIP - no TAVILY_API_KEY in .env")
else:
    results = tavily.search(
        "Indian Contract Act 1872 Section 27 restraint of trade", max_results=2
    )
    if results:
        print(f"  OK - search returned {len(results)} results")
        for item in results:
            print(f"    - {item.get('title', '')[:80]}")
    else:
        print("  FAIL - no results; check the key/quota at https://app.tavily.com")

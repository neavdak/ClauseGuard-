"""Print the Nemotron models Token Factory exposes to this API key.

Usage:  python scripts/list_models.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clauseguard.config import settings  # noqa: E402
from clauseguard.llm import Router  # noqa: E402

if settings.mock_mode:
    print("No NEBIUS_API_KEY found (or MOCK_MODE enabled).")
    print("1. Join https://dev.nebius.com/builders and create a Token Factory API key")
    print("2. Put it in .env as NEBIUS_API_KEY=...")
    print("3. Re-run this script")
    sys.exit(1)

print("Querying Token Factory /v1/models …\n")
router = Router(force_discover=True)
print("Tier mapping:")
for tier in ("nano", "super", "ultra", "vl"):
    print(f"  {tier:6s} -> {router.tiers.get(tier) or '(not found)'}")
print(
    "\nIf a tier is wrong or empty, copy an exact model id from the list above "
    "into .env (NEMOTRON_NANO / NEMOTRON_SUPER / NEMOTRON_ULTRA / NEMOTRON_VL)."
)

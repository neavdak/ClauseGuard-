"""Discover which NVIDIA Nemotron models are served on Token Factory.

GET {base_url}/models returns every model id (OpenAI-compatible format).
We map tiers by keyword, preferring the Nemotron 3 family. Environment
variables (NEMOTRON_NANO / _SUPER / _ULTRA / _VL) always win.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from .config import ROOT, settings

try:
    import requests
except ImportError:  # requests only needed for live discovery
    requests = None  # type: ignore

CACHE_PATH = ROOT / ".model_cache.json"
CACHE_TTL_SECONDS = 6 * 60 * 60


def _load_cached_ids() -> list[str]:
    try:
        data = json.loads(CACHE_PATH.read_text())
        if time.time() - float(data.get("ts", 0)) < CACHE_TTL_SECONDS:
            return list(data.get("ids", []))
    except Exception:
        pass
    return []


def list_remote_models() -> list[str]:
    """Call GET /v1/models and cache the result. Raises on auth/network errors."""
    if requests is None:
        raise RuntimeError("'requests' package is required for model discovery")
    resp = requests.get(
        settings.base_url.rstrip("/") + "/models",
        headers={"Authorization": f"Bearer {settings.api_key}"},
        timeout=30,
    )
    resp.raise_for_status()
    ids = sorted(m.get("id", "") for m in resp.json().get("data", []) if m.get("id"))
    CACHE_PATH.write_text(json.dumps({"ts": time.time(), "ids": ids}, indent=2))
    return ids


def _available_ids(force: bool = False) -> list[str]:
    cached = _load_cached_ids()
    if cached and not force:
        return cached
    if requests is None:
        return cached
    try:
        return list_remote_models()
    except Exception:
        return cached  # fall back to stale cache rather than crashing the app


def _pick(ids: list[str], include: tuple[str, ...], exclude: tuple[str, ...] = ()) -> str | None:
    def ok(mid: str) -> bool:
        m = mid.lower()
        return all(k in m for k in include) and not any(k in m for k in exclude)

    candidates = [i for i in ids if ok(i)]
    candidates.sort(
        key=lambda i: (
            0 if "nemotron-3" in i.lower() else 1 if "nemotron" in i.lower() else 2,
            len(i),
        )
    )
    return candidates[0] if candidates else None


def discover(force: bool = False) -> dict[str, str | None]:
    """Return {'nano': model_id, 'super': ..., 'ultra': ..., 'vl': ...}."""
    tiers: dict[str, str | None] = {
        "nano": settings.model_nano or None,
        "super": settings.model_super or None,
        "ultra": settings.model_ultra or None,
        "vl": settings.model_vl or None,
    }
    ids = _available_ids(force) if not settings.mock_mode else []

    if ids:
        tiers["nano"] = tiers["nano"] or _pick(ids, ("nano",), ("vl", "vision"))
        tiers["super"] = tiers["super"] or _pick(ids, ("super",))
        tiers["ultra"] = tiers["ultra"] or _pick(ids, ("ultra",))
        tiers["vl"] = tiers["vl"] or _pick(ids, ("vl",)) or _pick(ids, ("vision",))

        any_text_nem = _pick(ids, ("nemotron",), ("vl", "vision")) or ids[0]
        tiers["nano"] = tiers["nano"] or any_text_nem
        tiers["super"] = tiers["super"] or any_text_nem
        # Ultra legitimately falls back to Super when Ultra isn't on the account.
        tiers["ultra"] = tiers["ultra"] or tiers["super"]
        tiers["nano"] = tiers["nano"] or tiers["super"]

    return tiers

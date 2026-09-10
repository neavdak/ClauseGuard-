"""Thin Tavily search wrapper — used to surface recent legal context.

Doing live legal-update checks is the project's natural Tavily use case
(there is a $3,000 "Best Use of Tavily" prize).
"""
from __future__ import annotations

try:
    import requests
except ImportError:
    requests = None  # type: ignore

from .checklist import SEVERITY_RANK
from .config import settings

TAVILY_URL = "https://api.tavily.com/search"


def search(query: str, max_results: int = 4) -> list[dict]:
    if not settings.tavily_key or requests is None:
        return []
    payload = {"query": query, "max_results": max_results, "search_depth": "basic"}
    attempts = [
        # newer Tavily keys use a Bearer token ...
        {
            "headers": {
                "Authorization": f"Bearer {settings.tavily_key}",
                "Content-Type": "application/json",
            },
            "json": payload,
        },
        # ... older keys pass api_key in the body
        {"headers": {"Content-Type": "application/json"}, "json": {**payload, "api_key": settings.tavily_key}},
    ]
    for kwargs in attempts:
        try:
            resp = requests.post(TAVILY_URL, timeout=30, **kwargs)
            if resp.status_code == 401:
                continue  # try the other auth style
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception:
            continue
    return []


def legal_updates(analyses: list[dict], max_topics: int = 3) -> list[dict]:
    """For the worst clause categories, pull recent India-focused legal context."""
    worst: dict[str, dict] = {}
    for a in analyses:
        cat = a.get("category", "other")
        if cat in ("boilerplate", "other"):
            continue
        if cat not in worst or SEVERITY_RANK.get(a.get("severity", "low"), 0) > SEVERITY_RANK.get(
            worst[cat].get("severity", "low"), 0
        ):
            worst[cat] = a
    ordered = sorted(worst.values(), key=lambda a: SEVERITY_RANK.get(a.get("severity", "low"), 0), reverse=True)
    out: list[dict] = []
    for a in ordered[:max_topics]:
        label = a.get("category_label", a.get("category", ""))
        query = f"India {label} contract clause enforceability latest legal position"
        results = search(query)
        if results:
            out.append(
                {
                    "category": a.get("category"),
                    "category_label": label,
                    "query": query,
                    "results": [
                        {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
                        for r in results
                    ],
                }
            )
    return out

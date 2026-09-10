"""End-to-end ClauseGuard analysis pipeline.

Stages:
  1. Segmentation ........ Nemotron Super (long-context structural understanding)
  2. Bulk classification .. Nemotron Nano (cheap parallel risk tagging)
  3. Deep escalation ...... Nemotron Ultra (only critical/high clauses)
  4. Legal web check ...... Tavily (recent India legal context)
  5. Executive summary .... Nemotron Super
"""
from __future__ import annotations

from datetime import datetime

from . import prompts, report, tavily
from .llm import Router
from .usage import UsageLog

BATCH_SIZE = 4          # clauses per Nano call
ESCALATE_CAP = 6        # max Ultra calls per document (keeps spend predictable)
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def analyze_document(
    filename: str,
    text: str,
    *,
    use_tavily: bool = True,
    on_stage=None,
) -> dict:
    """Run the full review. `on_stage(done:int, total:int, label:str)` feeds UI progress."""
    usage = UsageLog()
    router = Router(usage=usage)

    def stage(done, total, label):
        if on_stage:
            on_stage(done, total, label)

    if not text or not text.strip():
        raise ValueError("No document text to analyse.")

    # 1. Segment (Super)
    stage(1, 5, "Segmenting contract into clauses (Nemotron Super)…")
    segmented = router.json("super", prompts.segment_messages(filename, text), purpose="segment", max_tokens=8000)
    clauses = segmented.get("clauses", [])
    if not clauses:
        raise ValueError("Segmentation returned no clauses.")

    # 2. Classify in batches (Nano)
    stage(2, 5, f"Reviewing {len(clauses)} clauses (Nemotron Nano, batched)…")
    analyses: list[dict] = []
    for i in range(0, len(clauses), BATCH_SIZE):
        batch = clauses[i : i + BATCH_SIZE]
        result = router.json("nano", prompts.analyze_messages(batch), purpose="analyze", max_tokens=6000)
        rows = result.get("analyses", []) if isinstance(result, dict) else result
        by_id = {r.get("clause_id"): r for r in rows}
        for c in batch:  # make sure every clause survives, even if the model dropped one
            row = by_id.get(c["clause_id"]) or {}
            row.setdefault("clause_id", c["clause_id"])
            row.setdefault("title", c["title"])
            row.setdefault("text", c["text"])
            row.setdefault("severity", "low")
            row.setdefault("category", "other")
            row.setdefault("category_label", c.get("title", "Other"))
            analyses.append(row)

    analyses.sort(key=lambda a: SEVERITY_ORDER.get(a.get("severity", "low"), 9))

    # 3. Escalate worst clauses (Ultra)
    worst = [a for a in analyses if a.get("severity") in ("critical", "high")][:ESCALATE_CAP]
    stage(3, 5, f"Deep-negotiating {len(worst)} risky clauses (Nemotron Ultra)…")
    for a in worst:
        deep = router.json("ultra", prompts.escalate_messages(a), purpose="escalate", max_tokens=2500)
        for key in ("severity_review", "negotiation_strategy", "fallback_positions", "email_draft"):
            if deep.get(key):
                a[key] = deep[key]
        a["escalated"] = True

    # 4. Live legal context (Tavily)
    stage(4, 5, "Checking recent legal context (Tavily)…" if use_tavily else "Skipping web check.")
    legal = tavily.legal_updates(analyses) if use_tavily else []

    # 5. Executive summary (Super)
    stage(5, 5, "Writing executive summary (Nemotron Super)…")
    summary = router.json("super", prompts.summary_messages(analyses), purpose="summary", max_tokens=2000)

    score = report.risk_score(analyses)
    return {
        "filename": filename,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "mock_mode": router.tiers.get("nano") is None,
        "models": router.tiers,
        "risk_score": score,
        "analyses": analyses,
        "summary": summary,
        "legal_updates": legal,
        "usage": usage.to_dict(),
    }

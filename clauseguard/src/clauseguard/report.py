"""Deterministic risk scoring and Markdown report export."""
from __future__ import annotations

from datetime import datetime

SEVERITY_WEIGHTS = {"critical": 25, "high": 12, "medium": 5, "low": 2}


def risk_score(analyses: list[dict]) -> int:
    score = 0
    for a in analyses:
        score += SEVERITY_WEIGHTS.get(a.get("severity", "low"), 2)
    return min(score, 100)


def band(score: int) -> tuple[str, str]:
    if score >= 70:
        return "critical", "Do not sign as drafted"
    if score >= 40:
        return "high", "Negotiate before signing"
    if score >= 15:
        return "medium", "Some points worth raising"
    return "low", "Low heuristic risk"


_BADGE = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}


def to_markdown(report: dict) -> str:
    score = report.get("risk_score", 0)
    score_band, band_label = band(score)
    lines: list[str] = []
    lines.append(f"# ClauseGuard report — {report.get('filename', 'contract')}")
    lines.append(f"_Generated {report.get('created_at', datetime.utcnow().isoformat())} · "
                 f"models: Nano `{report['models'].get('nano')}` · Super `{report['models'].get('super')}` "
                 f"· Ultra `{report['models'].get('ultra')}`_\n")
    lines.append(f"## Risk score: {score}/100 {_BADGE[score_band]} — {band_label}\n")
    summary = report.get("summary", {})
    lines.append(f"**Verdict:** {summary.get('verdict', '')}\n")
    if summary.get("top_issues"):
        lines.append("### Top issues")
        for i, issue in enumerate(summary["top_issues"], 1):
            lines.append(f"{i}. **{issue.get('title','')}** — {issue.get('why','')}")
        lines.append("")
    if summary.get("negotiation_priorities"):
        lines.append("### Negotiation priorities")
        for p in summary["negotiation_priorities"]:
            lines.append(f"- {p}")
        lines.append("")

    lines.append("## Clauses")
    for a in report.get("analyses", []):
        lines.append(f"### {_BADGE.get(a.get('severity'),'•')} {a.get('title','')} _({a.get('category_label','')}, {a.get('severity','')})_")
        lines.append(f"> {a.get('text','').strip()[:1200]}\n")
        lines.append(f"- **In plain English:** {a.get('plain_english','')}")
        if a.get("risk_explanation"):
            lines.append(f"- **Why it is risky:** {a.get('risk_explanation')}")
        if a.get("indian_law_note"):
            lines.append(f"- **Indian legal context:** {a.get('indian_law_note')}")
        if a.get("suggested_redline"):
            lines.append(f"- **Suggested redline:**\n  > {a.get('suggested_redline')}")
        if a.get("email_draft"):
            lines.append(f"- **Negotiation email draft:**\n\n```\n{a.get('email_draft')}\n```")
        lines.append("")

    updates = report.get("legal_updates", [])
    if updates:
        lines.append("## Legal context (live web check via Tavily)")
        for group in updates:
            lines.append(f"### {group.get('category_label')}")
            for r in group.get("results", []):
                lines.append(f"- [{r.get('title')}]({r.get('url')}) — {r.get('content','')[:200]}")
            lines.append("")

    lines.append("---")
    lines.append("_Educational analysis only, not legal advice. Confirm important points with a lawyer._")
    return "\n".join(lines)

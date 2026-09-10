"""Offline heuristic engine.

Lets the ENTIRE app run with no API keys (MOCK_MODE or missing NEBIUS_API_KEY).
It is also a deterministic baseline used when evaluating model quality.
"""
from __future__ import annotations

import json
import re

from . import checklist


def _payload(messages: list[dict]) -> dict | list | None:
    """Pull the INPUT_JSON payload that prompts.py appends to the last user message."""
    text = messages[-1]["content"] if messages else ""
    m = re.search(r"INPUT_JSON:\s*(\{.*\}|\[.*\])\s*$", text, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def _segment_text(text: str) -> list[dict]:
    heading = re.compile(r"^\s*(?:article\s+[ivxlcdm]+\s*[:\-.]?\s*)?(\d{1,2})[\.\)]\s+([A-Z0-9][^\n]{2,80})$", re.M | re.I)
    matches = list(heading.finditer(text))
    clauses: list[dict] = []
    if matches:
        bounds = matches + [None]
        for i, m in enumerate(matches[:-1] if len(matches) > 1 else matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            clauses.append({"clause_id": f"C{i+1:02d}", "title": m.group(2).strip().rstrip("."), "text": body})
    else:
        chunks = [c.strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
        buf = ""
        for chunk in chunks:
            buf = (buf + "\n\n" + chunk).strip()
            if len(buf) > 900:
                title = " ".join(buf.split()[:8])
                clauses.append({"clause_id": f"C{len(clauses)+1:02d}", "title": title, "text": buf})
                buf = ""
        if buf:
            title = " ".join(buf.split()[:8])
            clauses.append({"clause_id": f"C{len(clauses)+1:02d}", "title": title, "text": buf})
    return clauses


def _infer_category(t: str) -> str:
    for key, (_, _meaning) in checklist.CATEGORIES.items():
        if key == "other":
            continue
        if key.replace("_", " ") in t or key.replace("_", "") in t.replace(" ", ""):
            return key
    keyword_map = {
        "payment": "payment_terms", "fee": "payment_terms", "invoice": "payment_terms",
        "terminate": "term_termination", "termination": "term_termination",
        "confidential": "confidentiality", "indemnif": "indemnity",
        "liabilit": "liability_cap", "jurisdiction": "disputes", "arbitrat": "disputes",
        "intellectual property": "ip_assignment", "warrant": "warranties",
        "deposit": "rental_deposit", "renew": "auto_renewal",
    }
    for k, cat in keyword_map.items():
        if k in t:
            return cat
    return "other"


def _analyze_one(clause: dict) -> dict:
    t = clause.get("text", "").lower()
    best: dict | None = None
    for rule in checklist.RISK_RULES:
        if all(k in t for k in rule["match"]):
            if best is None or checklist.SEVERITY_RANK[rule["severity"]] > checklist.SEVERITY_RANK[best["severity"]]:
                best = rule
    if best:
        label, meaning = checklist.CATEGORIES[best["category"]]
        return {
            "clause_id": clause["clause_id"],
            "title": clause["title"],
            "text": clause["text"],
            "category": best["category"],
            "category_label": label,
            "severity": best["severity"],
            "summary": best["title"],
            "plain_english": meaning,
            "risk_explanation": best["risk"],
            "indian_law_note": best["law"],
            "suggested_redline": best["redline"],
        }
    category = _infer_category(t)
    label, meaning = checklist.CATEGORIES[category]
    return {
        "clause_id": clause["clause_id"],
        "title": clause["title"],
        "text": clause["text"],
        "category": category,
        "category_label": label,
        "severity": "low",
        "summary": f"Covers {label.lower()}; the heuristic scan found no high-risk language.",
        "plain_english": meaning,
        "risk_explanation": "",
        "indian_law_note": "",
        "suggested_redline": "",
    }


def _segment(payload: dict) -> dict:
    return {"clauses": _segment_text(payload.get("text", ""))}


def _analyze(payload: dict) -> dict:
    return {"analyses": [_analyze_one(c) for c in payload.get("clauses", [])]}


def _escalate(payload: dict) -> dict:
    clause = payload.get("clause", {})
    label = clause.get("category_label", "this clause")
    title = clause.get("title", "clause")
    return {
        "clause_id": clause.get("clause_id"),
        "severity_review": f"Heuristic review confirms '{title}' as {clause.get('severity', 'high')} risk.",
        "negotiation_strategy": [
            f"Open by acknowledging the purpose behind the {label} clause, then share the specific downside you face.",
            "Propose the concrete redline wording rather than asking vaguely for 'something fair'.",
            "Trade: accept a narrower version of their ask in exchange for a cap, notice period or mutuality.",
        ],
        "fallback_positions": [
            "Mutualise the obligation (apply the same duty to both parties).",
            "Add a monetary cap and a time limit.",
            "If they refuse all changes, add a side letter confirming the narrow interpretation.",
        ],
        "email_draft": (
            "Subject: Proposed wording for the " + title + " clause\n\n"
            "Hi [Name], thanks for sharing the agreement. Overall it looks workable. Before signing, "
            f"I'd like to align on the {label.lower()} clause ({clause.get('clause_id', '')}). As drafted it is "
            "one-sided/unbounded, which creates disproportionate risk for [me/our side].\n\n"
            "I'd propose the following wording:\n\n"
            f"\"{clause.get('suggested_redline', '[insert balanced wording]')}\"\n\n"
            "This still protects your concerns while keeping the obligation reasonable and mutual. "
            "Happy to jump on a quick call. Thanks!\n\nBest,\n[Your name]"
        ),
    }


def _summary(payload: dict) -> dict:
    analyses = payload.get("analyses", [])
    n = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for a in analyses:
        n[a.get("severity", "low")] = n.get(a.get("severity", "low"), 0) + 1
    top = [a for a in analyses if a.get("severity") in ("critical", "high")][:5]
    if n["critical"]:
        verdict = "Do not sign without renegotiation — critical one-sided terms detected."
    elif n["high"]:
        verdict = "Significant issues; negotiate before signing."
    elif n["medium"]:
        verdict = "Mostly acceptable with a handful of points worth raising."
    else:
        verdict = "No major red flags detected by the heuristic scan; standard review still advised."
    return {
        "verdict": verdict,
        "top_issues": [{"title": a.get("title", ""), "why": a.get("risk_explanation", "")} for a in top],
        "negotiation_priorities": [a.get("title", "") for a in top[:3]],
        "good_practices": [
            a["category_label"] for a in analyses if a.get("severity") == "low"
        ][:5],
    }


def respond(purpose: str, messages: list[dict]) -> str:
    payload = _payload(messages)
    if payload is None:
        return json.dumps({"ok": True, "mock": True})
    if purpose == "segment":
        return json.dumps(_segment(payload), ensure_ascii=False)
    if purpose == "analyze":
        return json.dumps(_analyze(payload), ensure_ascii=False)
    if purpose == "escalate":
        return json.dumps(_escalate(payload), ensure_ascii=False)
    if purpose == "summary":
        return json.dumps(_summary(payload), ensure_ascii=False)
    return json.dumps({"ok": True})

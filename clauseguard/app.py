"""ClauseGuard — Streamlit app. Run with:  streamlit run app.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st  # noqa: E402

from clauseguard.config import settings  # noqa: E402
from clauseguard.extract import extract_text  # noqa: E402
from clauseguard.llm import Router  # noqa: E402
from clauseguard.pipeline import analyze_document  # noqa: E402
from clauseguard.report import band, to_markdown  # noqa: E402

st.set_page_config(page_title="ClauseGuard — contract risk copilot", page_icon="⚖️", layout="wide")

BADGE = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# --------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("⚖️ ClauseGuard")
    st.caption("Contract risk copilot · Nebius Token Factory × NVIDIA Nemotron")

    if "router" not in st.session_state:
        with st.spinner("Discovering Nemotron models…"):
            st.session_state.router = Router()
    tiers = st.session_state.router.tiers

    if settings.mock_mode:
        st.warning("**Offline mock mode** — set `NEBIUS_API_KEY` in `.env` to run on Nemotron.")
    else:
        st.success("**Live** — Nebius Token Factory")
    with st.expander("Model routing map"):
        st.caption("Cheap bulk work → Nano; planning & summary → Super; hard negotiation → Ultra")
        st.write("**Nano**", tiers.get("nano") or "—")
        st.write("**Super**", tiers.get("super") or "—")
        st.write("**Ultra**", tiers.get("ultra") or "— (falls back to Super)")
        st.write("**Vision**", tiers.get("vl") or "—")

    if (report := st.session_state.get("report")) and report.get("usage"):
        u = report["usage"]
        with st.expander(f"Routing panel — {u['num_calls']} calls · {u['total_tokens']} tokens", expanded=True):
            for c in u["calls"]:
                st.write(f"**{c['tier']}** · {c['purpose']} · {c['completion_tokens']} tok · {c['latency_s']}s")
            st.caption("This panel proves which model handled each stage and how routing saves credits.")

    st.divider()
    st.caption("Educational assistant, **not legal advice**. Verify important points with a lawyer.")

# --------------------------------------------------------------------------- header
st.title("Read any contract before you sign it")
st.write(
    "Upload an NDA, freelance MSA, vendor agreement or rental contract. ClauseGuard segments it with "
    "**Nemotron Super**, bulk-reviews clauses with the cheap **Nemotron Nano**, escalates the dangerous "
    "ones to **Nemotron Ultra** for negotiation strategy, and checks current legal context via **Tavily**."
)

# --------------------------------------------------------------------------- input
with st.form("upload_form"):
    uploaded = st.file_uploader("Contract file", type=["pdf", "txt", "md", "png", "jpg", "jpeg", "webp"])
    pasted = st.text_area("…or paste the contract text here", height=160)
    do_tavily = st.toggle("Check recent legal context with Tavily", value=True)
    submitted = st.form_submit_button("⚡ Analyse contract", type="primary")

if submitted:
    name, text, warning = "pasted-contract.txt", pasted.strip(), ""
    if uploaded is not None:
        result = extract_text(uploaded.name, uploaded.read(), st.session_state.router)
        name, text, warning = uploaded.name, result["text"], result.get("warning", "")
    if not text:
        st.error(warning or "Please upload a contract file or paste contract text.")
        st.stop()
    if warning:
        st.warning(warning)

    progress = st.progress(0.0)
    status = st.empty()

    def on_stage(done: int, total: int, label: str) -> None:
        progress.progress(done / total)
        status.write(label)

    with st.spinner("Analysing…"):
        st.session_state.report = analyze_document(name, text, use_tavily=do_tavily, on_stage=on_stage)
    status.success("Review complete")
    progress.progress(1.0)
    st.rerun()

report = st.session_state.get("report")
if not report:
    st.info("Tip: try `samples/sample_freelance_msa.txt` — a deliberately one-sided agreement used for demos.")
    st.stop()

analyses = report["analyses"]
score = report["risk_score"]
score_band, band_label = band(score)
summary = report.get("summary", {})

# --------------------------------------------------------------------------- results
c1, c2, c3 = st.columns([1, 1, 3])
c1.metric("Risk score", f"{score}/100")
c2.metric("Band", f"{BADGE[score_band]} {score_band.title()}")
c3.markdown(f"**Verdict:** {summary.get('verdict', '')}  \n_{band_label}._")

tab_overview, tab_clauses, tab_negotiate, tab_web, tab_export = st.tabs(
    ["Overview", f"Clauses ({len(analyses)})", "Negotiation pack", "Legal web check", "Export"]
)

with tab_overview:
    if summary.get("top_issues"):
        st.subheader("Top issues")
        for i, issue in enumerate(summary["top_issues"], 1):
            st.markdown(f"**{i}. {issue.get('title','')}** — {issue.get('why','')}")
    lc, rc = st.columns(2)
    with lc:
        st.subheader("Negotiation priorities")
        for p in summary.get("negotiation_priorities", []):
            st.markdown(f"- {p}")
    with rc:
        st.subheader("Fair clauses worth keeping")
        for p in summary.get("good_practices", []):
            st.markdown(f"- {p}")

with tab_clauses:
    sev = st.multiselect("Severities", list(BADGE), default=list(BADGE), format_func=lambda s: f"{BADGE[s]} {s}")
    shown = [a for a in analyses if a.get("severity") in sev]
    shown.sort(key=lambda a: ORDER.get(a.get("severity", "low"), 9))
    for a in shown:
        title = f"{BADGE.get(a.get('severity'),'•')} {a.get('title','Untitled')} — {a.get('category_label','')}"
        with st.expander(f"{title} · {a.get('severity','low')}"):
            st.caption("What it says")
            st.write(a.get("text", ""))
            st.markdown(f"**In plain English:** {a.get('plain_english','')}")
            if a.get("risk_explanation"):
                st.error(f"**Why risky:** {a.get('risk_explanation')}")
            if a.get("indian_law_note"):
                st.info(f"**Indian legal context:** {a.get('indian_law_note')}")
            if a.get("suggested_redline"):
                st.success("**Suggested redline**")
                st.write(a.get("suggested_redline"))

with tab_negotiate:
    escalated = [a for a in analyses if a.get("email_draft")]
    if not escalated:
        st.write("No clauses were escalated for deep negotiation (no critical/high findings).")
    for a in escalated:
        st.subheader(f"{BADGE.get(a.get('severity'),'•')} {a.get('title')}")
        st.write(a.get("severity_review", ""))
        if a.get("negotiation_strategy"):
            st.markdown("**Strategy**")
            for s in a["negotiation_strategy"]:
                st.markdown(f"- {s}")
        if a.get("fallback_positions"):
            st.markdown("**Fallback positions**")
            for s in a["fallback_positions"]:
                st.markdown(f"- {s}")
        st.markdown("**Ready-to-send email**")
        st.code(a.get("email_draft", ""), language=None)

with tab_web:
    updates = report.get("legal_updates", [])
    if not updates:
        st.write("No web results (set TAVILY_API_KEY in .env to enable live legal-context checks).")
    for group in updates:
        st.subheader(group.get("category_label", ""))
        for r in group.get("results", []):
            st.markdown(f"- [{r.get('title')}]({r.get('url')}) — {r.get('content','')[:240]}")

with tab_export:
    md = to_markdown(report)
    st.download_button("⬇️ Download Markdown report", md, file_name="clauseguard-report.md")
    st.download_button(
        "⬇️ Download raw JSON", json.dumps(report, indent=2, ensure_ascii=False), file_name="clauseguard-report.json"
    )
    with st.expander("How this uses Nebius & NVIDIA"):
        st.markdown(
            """
- **Nebius Token Factory** serves every model call via its OpenAI-compatible API
  (`https://api.tokenfactory.nebius.com/v1/`).
- **NVIDIA Nemotron Super** segments long contracts and writes the executive summary (1M-token context).
- **NVIDIA Nemotron Nano** handles batched clause classification — the cheap, high-volume stage.
- **NVIDIA Nemotron Ultra** is used only for the few critical/high clauses, keeping spend predictable.
- **Nemotron VL** (vision) reads scanned contract images when available.
- **Tavily** performs the live Indian legal-context check.
- *(Planned)* Nebius Serverless Jobs for scheduled renewal/notice-date reminders.
"""
        )

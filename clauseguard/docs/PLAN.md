# ClauseGuard — 50-day execution plan (Sep 10 → Oct 30, 2026)

Hard deadline: **Oct 30, 2026, 10:00 AM PDT** = **Oct 30, 10:30 PM IST**.
Internal submit-by target: **Oct 28 EOD IST** (2-day buffer).

## Team roles (3–4 people)

| Person | Role | Owns |
|---|---|---|
| **A — Agent/backend lead** | Core pipeline | `llm.py`, `models.py`, `pipeline.py`, prompts, routing, evals |
| **B — Product/frontend lead** | UX | `app.py`, report visuals, export, empty/error states, product copy, Devpost page |
| **C — Domain/data lead** | Legal accuracy | `checklist.py` taxonomy, gold contract set, user interviews, Tavily curation |
| **D — DevOps/media (merge into B if 3 people)** | Ship & tell | Deployment, VL/PDF, Serverless Jobs, video recording/editing, FEEDBACK.md |

Everyone tests the app weekly; nobody works in isolation past Wednesday.

## Weekly milestones

### Week 0 — Sep 10–13 · Setup & spike
- [ ] All: follow `docs/SETUP.md` (Builder Program, API keys, GitHub, `.env`).
- [ ] A: `list_models.py` returns Nano/Super/Ultra; smoke test runs LIVE (not mock).
- [ ] C: collect 5 NDAs/MSAs + 2 rental agreements (friends, startups, public templates);
      start gold annotation sheet (clause text → true category → true severity).
- [ ] B: run the mock UI locally; write down 10 UX papercuts.
- [ ] Shared: GitHub project board with columns Backlog / This week / Review / Done.

### Week 1 — Sep 14–20 · Pipeline is real
- [ ] A: live segmentation + classification on 3 contracts; tune prompts until JSON is stable.
- [ ] B: upload flow + progress stages + report Overview/Clauses tabs polished.
- [ ] C: expand checklist to 25 clause types with India notes; cite statute for every rule.
- [ ] **Demo Friday:** live upload → full report on one real MSA.

### Week 2 — Sep 21–27 · Negotiation pack + vision
- [ ] A: Ultra escalation (strategy, fallbacks, email); Nano VL path for photos/scans.
- [ ] B: Negotiation tab, copy-to-clipboard emails, severity filters, routing panel sidebar.
- [ ] C: redline style guide; 10 more gold contracts; define "correct flag" rubric together.
- [ ] **Demo Friday:** scanned NDA photo → report; email draft ready to send.

### Week 3 — Sep 28–Oct 4 · Web checks + export + accuracy hardening
- [ ] D/A: Tavily legal-context tab (queries tuned, citations shown); Markdown/JSON export.
- [ ] A: eval harness — run gold set, print recall/precision per category + token totals.
- [ ] C: blind-rate 20 redlines/emails (1–5), feed top failure prompts back to A.
- [ ] **Go/No-Go (Oct 4):** critical-clause recall ≥ 85% on gold set, else cut features and fix prompts.

### Week 4 — Oct 5–11 · Product polish
- [ ] B: landing/hero copy, sample-contract button, mobile layout, loading/error states.
- [ ] A: DOCX upload, multi-document compare? (only if recall is already green).
- [ ] D: deploy public URL (Streamlit Cloud / HF Spaces) with secrets; custom domain if easy.
- [ ] C: 30-minute Hindi/Kannada plain-language pass on top 6 risk explanations.
- [ ] **Demo Friday:** public URL works end-to-end with no console errors.

### Week 5 — Oct 12–18 · Nebius deepening + user testing
- [ ] D (optional but high-value): Serverless Job for renewal/notice reminders,
      OR a Token Factory dedicated endpoint for the model tier; record setup screenshots.
- [ ] All: 5 real users (freelancers/founders/tenants) watch-and-use sessions, 20 min each;
      collect one quote per user; log every stumble.
- [ ] B/A: fix the top 5 usability issues; add an in-app feedback line.
- [ ] C: keep FEEDBACK.md on Token Factory (delights + rough edges) — $100 award category.

### Week 6 — Oct 19–25 · Freeze & film
- [ ] **Feature freeze Oct 21.** After: fixes, copy, test accounts only.
- [ ] D/B: record demo video (script below), captions, 3:00 max; upload unlisted→public YouTube.
- [ ] B: Devpost project page (outline below); screenshots; tagline; tech stack.
- [ ] A: README pass — setup from clone in <10 minutes on a clean machine; LICENSE visible at top.
- [ ] C: compile sources/citations page; disclaimer review.

### Buffer — Oct 26–30 · Submit & defend
- [ ] Oct 26–27: final QA on fresh browser + mobile; re-record video if needed.
- [ ] Oct 28: **submit**; verify repo public, video public, demo URL alive.
- [ ] Oct 29–30: only emergency fixes; resubmit allowed until deadline.

## 3-minute video script (judges may stop watching at 3:00)

| Time | Shot / voiceover |
|---|---|
| 0:00–0:20 | Problem: freelancer handed a 12-page MSA, can't afford a lawyer; montage of red-flag clauses (uncapped indemnity, 5-year non-compete). "This is what signing without reading costs people in India." |
| 0:20–0:40 | Product intro + one-line architecture: open NVIDIA Nemotron models on Nebius Token Factory. |
| 0:40–1:25 | Live demo: drag the sample MSA → progress stages show **Super segmenting**, **Nano classifying in batches**, **Ultra escalating**; routing panel with calls/tokens/latency visible. |
| 1:25–2:00 | Report walkthrough: risk score 100/100, top issues, plain English + Indian Contract Act/Copyright Act notes; redline wording. |
| 2:00–2:25 | Negotiation email generated; scanned photo read by **Nano VL**; Tavily legal-context results with citations. |
| 2:25–2:50 | Why it's cheap/open: model-routing economics, MIT repo, privacy/zero-retention; (if built) Serverless reminder job; user quote. |
| 2:50–3:00 | Tagline + GitHub/demo URL on screen. |

Rules reminder: no copyrighted music (use YouTube audio-library), public video, must verbally
name Nebius Token Factory and NVIDIA Nemotron.

## Devpost page outline (B owns)

1. **Tagline**: "Know what you're signing — an AI contract copilot built for India, on open models."
2. **Inspiration**: the real stories collected in user interviews.
3. **What it does**: 5 bullets mapping to demo moments.
4. **How we built it**: pipeline + routing table + why Nano/Super/Ultra; cite Token Factory
   OpenAI-compatible API, Tavily, (optional) Serverless.
5. **Challenges & fixes**: JSON reliability, long documents, legal accuracy via gold set.
6. **What's next**: DOCX, vernacular, reminder jobs, fine-tuning.
7. Links: demo URL, GitHub (MIT at top), 3-min YouTube.
8. Track: Best Apps & Agents. City: Bengaluru (if an IRL event was attended).

## Submission asset checklist (mirror of rules)
- [ ] Working public demo URL, free to test, no login (creds provided if gated)
- [ ] Public GitHub repo; MIT license visible in About/header; README runnable in <10 min
- [ ] README explicitly documents Nemotron usage, Token Factory usage, other Nebius services
- [ ] YouTube ≤ 3:00, public, audio explains Nebius + Nemotron
- [ ] Project description: what / why / how
- [ ] Written feedback on Token Factory & NVIDIA tools (FEEDBACK.md)
- [ ] Changelog note if any code predates Aug 26 (ours doesn't)
- [ ] Team: representative + all members added on Devpost
- [ ] Track + optional city award selected

## Top risks & mitigations
1. **Credits/domain approval delay** → build on mock mode (already working); apply to Builder Program today.
2. **Model returns invalid JSON on long docs** → recovery parser exists; fall back to smaller clause batches.
3. **Legal misinformation** → conservative phrasing, statute citations, "not legal advice" everywhere,
   Tavily sources shown, redlines framed as *suggestions*.
4. **Scope creep** (DOCX, auth, payments, multi-language) → park everything post-Oct 21; only items
   that protect the go/no-go recall metric enter weeks 4–5.
5. **Deadline timezone** → deadline is 10:30 PM IST Oct 30; we submit Oct 28 regardless.

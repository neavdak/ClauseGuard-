# Idea Shortlist — Best Apps & Agents Track

All ideas satisfy the hard requirements: runtime calls to **Nebius Token Factory** (OpenAI-compatible API)
using **NVIDIA Nemotron** open models. Every idea uses the *model-routing pattern judges explicitly praise*:
**Nano** for cheap/fast bulk calls → **Super** (120B MoE, 1M context, agentic) for planning/analysis →
**Ultra** only for deep reasoning. A shared "model routing panel" in the UI (which model ran each step,
latency, tokens, cost) is a differentiator for the Technological Implementation criterion.

Beginner-friendly reference stack for ALL ideas:
- Python 3.11 + `openai` SDK pointing at Token Factory
- UI: Streamlit (simplest) or Chainlit (chat-product feel)
- Storage: SQLite + simple file uploads
- Search: Tavily API (free credits via Builder Program)
- Scheduled/background work: Nebius Serverless Jobs (cron-style)
- Demo hosting: Hugging Face Spaces / Streamlit Cloud calling Token Factory (compliant: runtime API call)
- Optional extra: deploy your own Nemotron on a Token Factory dedicated endpoint / Serverless Endpoint

Scoring: 1–5 against the four judging criteria; Effort 1 (easy) – 5 (hard).

---

## Idea 1 — OPPORTUNI: set-and-forget opportunity radar (TOP PICK for feasibility)

**One-liner:** A self-running agent that finds scholarships, internships, hackathons, conference CFPs and
grants matching a student's profile, ranks them, and drafts tailored applications before deadlines.

**Problem:** Students (esp. Indian undergrads) miss hundreds of life-changing opportunities because they're
scattered across portals, PDFs and Twitter; applying one-by-one takes hours.

**How it works:**
1. Onboarding: profile form + resume upload (Super extracts skills via 1M context).
2. A **Nebius Serverless Job runs daily**: Tavily searches curated sources (Devpost, scholarship portals,
   university boards, LinkedIn-like public pages, CFP sites).
3. **Nano** cheaply classifies/ranks hundreds of hits (fit score, deadline extracted).
4. **Super** plans the application checklist; **Ultra** drafts the SOP/cover letter/resume tweaks for
   top matches (the expensive reasoning used sparingly → "credits stretch further" story).
5. Dashboard: ranked feed, deadline calendar, auto-drafted applications, one-click copy; email/WhatsApp
   reminders. Agent re-runs itself and improves drafts from feedback.

**Nebius/NVIDIA showcase:** Serverless Jobs (the workflow literally runs itself), Nano/Ultra routing,
Tavily as core retrieval → natural entry for **$3k Best Use of Tavily**.

**Audience:** engineering/college students across India; later researchers, indie makers.

**Demo moment:** Show a real student profile → "7-day agent run log" → ranked opportunities →
one-click finished SOP draft.

| Implementation | Design | Impact | Idea | Effort |
|---|---|---|---|---|
| 4 | 4 | 4 | 3 | **2** |

**Risks:** generic "AI finder" feel → beat it with a sharp wedge (Indian students + auto-drafted
applications + autonomous daily runs) and real saved-opportunity data in the demo.

---

## Idea 2 — CLAUSEGUARD: contract risk copilot for freelancers & small businesses

**One-liner:** Upload any contract/NDA/rental agreement; get a plain-language risk report with red-flagged
clauses, Indian-contract context, and ready-to-send negotiation replies.

**Problem:** Freelancers, founders and tenants sign one-sided legal papers they can't afford a lawyer to
review; dangerous clauses (unlimited liability, IP grab, one-sided termination, lock-in, arbitration in a
far city) pass unnoticed.

**How it works:**
1. Upload PDF/photo (pdfplumber; Nano 2 VL for scanned images).
2. **Super** (1M context reads even 100-page agreements) segment-clauses; **Nano** classifies each clause
   against a legal checklist in bulk.
3. Risky clauses escalate to **Ultra** for severity reasoning + redline wording.
4. **Tavily** verifies recent Indian law/case updates (e.g. latest Contract Act / consumer court rulings).
5. Output: color-coded report ("what it says / what it means for you / what to do"), negotiation email
   drafts, redline suggestions, shareable PDF. Disclaimer: educational, not legal advice.

**Nebius/NVIDIA showcase:** 1M-token long-document reasoning, Nano/Super/Ultra escalation, VL for scans,
Tavily citations.

| Implementation | Design | Impact | Idea | Effort |
|---|---|---|---|---|
| 4 | 5 | 5 | 4 | **3** |

**Risks:** legal accuracy → citations + disclaimers + "flag for human review" framing. PDF edge cases.

---

## Idea 3 — LABLENS: family health-report interpreter & trend tracker

**One-liner:** Photograph a lab report; get plain-language explanations, longitudinal trend charts for the
whole family, and a smart list of questions to ask the doctor — private by default.

**Problem:** Lab reports are cryptic; values vary lab-to-lab; families (adult children tracking diabetic
parents across cities) never see trends; existing apps harvest health data.

**How it works:**
1. Upload PDF/photo → **Nano 2 VL** extracts markers, values, units, reference ranges.
2. Normalize to standard units; **Nano** explains each marker; **Super** correlates patterns
   (e.g. HbA1c + fasting glucose + lipids over time).
3. Family profiles, trend dashboards, "questions for your doctor" printout, Hinglish/vernacular toggle.
4. Privacy story: open-source code + Token Factory **zero-retention** EU/US endpoints (a real advertised
   Token Factory feature) — data never sold.
5. Optional **Serverless Job**: quarterly re-analysis + reminders to retake tests.

**Nebius/NVIDIA showcase:** Nemotron vision model, zero-retention inference, scheduled jobs.

| Implementation | Design | Impact | Idea | Effort |
|---|---|---|---|---|
| 3 | 4 | 5 | 3 | **3** |

**Risks:** VL extraction accuracy (mitigate with human-editable correction screen + confidence scores);
medical disclaimers; must NOT diagnose.

---

## Idea 4 — STUDYFORGE: adaptive agent for UPSC/JEE/GATE aspirants

**One-liner:** An always-on study coach that turns the syllabus + your materials into a daily adaptive
plan, writes and grades practice answers like an examiner, and pulls daily current-affairs briefs.

**Problem:** Lakhs of serious aspirants have materials but no disciplined plan, no answer-writing feedback
(UPSC Mains answers are the make-or-break skill), and stale current-affairs notes.

**How it works:**
1. Upload syllabus + notes PDFs (1M context) → Super builds a spaced-repetition study schedule.
2. **Serverless Job daily**: generates today's tasks + a **Tavily**-sourced current-affairs mini-brief
   with source links.
3. Student writes Mains answers; **Ultra** scores against an exam-style rubric (structure, keywords,
   examples), **Nano** gives quick MCQ drills.
4. Dashboard: streaks, weak-topic detection, model answers, weekly progress report to email.

| Implementation | Design | Impact | Idea | Effort |
|---|---|---|---|---|
| 4 | 4 | 5 | 3 | **4** |

**Risks:** crowded edtech space → wedge is *answer-evaluation quality + autonomous daily loop*, not content;
bigger build for a beginner team.

---

## Idea 5 — PAPERWORK SAHAY: paperwork & government-scheme navigator (narrow wedge)

**One-liner:** Tell your situation in plain language; the agent finds which government schemes you're
eligible for, pre-fills the right forms/drafts (RTI, rental, police verification, insurance claims), and
gives a deadline checklist in your language.

**Problem:** Migrants, low-income families and even middle-class Indians lose benefits/sign rights because
forms, eligibility and procedures are impenetrable.

**Narrow v1 (must resist scope creep):** pick ONE wedge — e.g. *rental housing in Bengaluru*
(rental agreement drafting + police verification + tenant rights) or *central/state scheme eligibility
checker for students*.

**How it works:** conversational intake (voice-friendly, Hinglish) → Tavily over official portals →
Super determines eligibility/checklist → Nano drafts forms → Ultra handles edge-case reasoning →
trackable task list with document checklist.

| Implementation | Design | Impact | Idea | Effort |
|---|---|---|---|---|
| 3 | 4 | 5 | 5 | **4** |

**Risks:** content verification is labor-heavy and breadth is dangerous; only viable if the team narrows
to a single wedge and validates with 3–5 real users.

---

## Wildcard — PULSEAGENT: weekly "voice of customer" brief for tiny SaaS teams
Ingest app-store reviews / support CSV / social (Tavily), cluster with Token Factory embeddings, Nemotron
writes an evidence-backed weekly pain-point brief with Linear/GitHub issue drafts and competitor checks,
delivered by a Serverless Job. Great agentic story, but many VOC incumbents; differentiation weaker.

---

## Recommendation
- **Best risk-adjusted choice for a beginner team: IDEA 1 (OPPORTUNI).** Lowest technical risk, hits the
  exact language of the track ("a workflow that runs itself"), showcases the most Nebius surfaces
  (Serverless Jobs + routing + Tavily), and a 3-minute demo practically writes itself.
- **Strongest polished-product / impact demo: IDEA 2 (CLAUSEGUARD)** if the team wants a sharper "wow"
  and accepts PDF-parsing work.

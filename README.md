# ⚖️ ClauseGuard — Contract Risk Copilot

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Track-Best%20Apps%20%26%20Agents-7928CA?style=for-the-badge" alt="Hackathon Track">
  <img src="https://img.shields.io/badge/Powered%20By-Nebius%20Token%20Factory-00E599?style=for-the-badge" alt="Nebius">
  <img src="https://img.shields.io/badge/Models-NVIDIA%20Nemotron%203-76B900?style=for-the-badge&logo=nvidia" alt="NVIDIA">
  <img src="https://img.shields.io/badge/Search-Tavily%20API-FF6B6B?style=for-the-badge" alt="Tavily">
  <img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" alt="Streamlit">
</p>

> **Know what you are signing before you sign.**
>
> ClauseGuard turns one-sided NDAs, freelance MSAs, vendor terms, and rental agreements into an actionable plain-language risk report — complete with Indian statutory context, suggested redlines, ready-to-send negotiation emails, and live legal precedent checks.

Built for the **Nebius × NVIDIA Global AI Hackathon** (*Best Apps & Agents* track & competing for *Best Use of Tavily*).

> [!CAUTION]
> **Educational Assistant, Not Legal Advice:** ClauseGuard highlights risky terms and suggests counter-proposals to level the playing field, but does not replace qualified legal counsel.

---

## 🎯 The Problem

Indian freelancers, early-stage founders, indie developers, and tenants regularly sign agreements drafted exclusively by the other party's lawyers. Without in-house legal counsel on retainer, dangerous clauses slip through unchecked:

- ❌ **Uncapped & Unilateral Indemnities:** One third-party claim can bankrupt an independent freelancer.
- ❌ **Perpetual IP Grabs:** Contracts demanding pre-existing code, fonts, tools, and background frameworks forever.
- ❌ **Excessive Non-Competes:** 2-to-5 year post-contract bans (largely void under Section 27 of the Indian Contract Act, 1872, but frequently used to intimidate).
- ❌ **"Sole Discretion" Termination:** Counterparties can terminate on zero notice and forfeit accumulated fees for completed work.
- ❌ **Far-Flung Jurisdiction:** Dispute resolution clauses forcing litigation in distant high courts or prohibitive international arbitration.

---

## ⚡ What ClauseGuard Does

```
                              ┌──────────────────────────────────────────────┐
                              │           ClauseGuard Streamlit UI           │
                              │  Upload / Paste / Load Sample Demo Contract  │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                                     ▼
                              ┌──────────────────────────────────────────────┐
                              │            Orchestration Pipeline            │
                              └──────┬───────────┬───────────┬───────────┬───┘
                                     │           │           │           │
                          1. Segment │ 2. Batch  │ 3. Deep   │ 5. Synth  │ 4. Ground
                                     │    Tag    │    Reason │    Summ   │
                                     ▼           ▼           ▼           ▼
                          ┌──────────────────┐  ┌──────────────────────┐  ┌─────────┐
                          │ Nemotron SUPER   │  │ Nemotron NANO        │  │ Tavily  │
                          │ 120B MoE, 1M Ctx │  │ Fast & cheap tagging │  │ Search  │
                          └──────────────────┘  └──────────────────────┘  └─────────┘
                                                           │ critical/high only
                                                           ▼
                                                ┌──────────────────────┐
                                                │ Nemotron ULTRA       │
                                                │ 550B Deep Reasoner   │
                                                │ Strategy & Redlines  │
                                                └──────────────────────┘
```

1. **Ingests Any Contract Format:** Upload PDF (via `pdfplumber`), DOCX (via `python-docx`), plain text / Markdown, or scanned page photos/screenshots (processed via Vision model `openbmb/MiniCPM-V-4_5` / Nemotron VL).
2. **Structural Segmentation (Nemotron 3 Super):** Leverages Super's 120B MoE architecture and 1M-token context window to ingest entire multi-page contracts in a single pass without brittle chunking.
3. **High-Throughput Bulk Tagging (Nemotron 3 Nano):** Fast, cost-efficient parallel analysis across an 18-category legal checklist (IP rights, indemnities, liability caps, dispute venues, non-competes, payment lock-ins).
4. **Deep Negotiation Escalation (Nemotron 3 Ultra):** Invoked *strictly* for clauses flagged as Critical or High severity. Crafts counter-strategies, fallback positions, and complete copy-paste negotiation emails.
5. **Live Statutory & Case Law Grounding (Tavily):** Searches recent Indian high court rulings and statutory provisions (Indian Contract Act 1872, Copyright Act 1957, DPDP Act 2023) to ground findings with live citations.
6. **Model Telemetry & Routing Panel:** Live dashboard tracking latency, token usage, and exact model tier invoked per stage — proving how dynamic routing maximizes inference budgets.

---

## 🏗️ Model Routing Economics

The hackathon brief explicitly rewards architectural efficiency. ClauseGuard routes tasks dynamically based on reasoning complexity:

| Pipeline Stage | Model Tier | Model ID | Primary Role | Frequency |
|---|---|---|---|---|
| **1. Segmentation** | **Super** | `nvidia/nemotron-3-super-120b-a12b` | Structural contract decomposition across 1M context | 1 call |
| **2. Classification** | **Nano** | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | High-volume risk taxonomy & severity classification (batches of 4) | ⌈N/4⌉ calls |
| **3. Escalation** | **Ultra** | `nvidia/Nemotron-3-Ultra-550b-a55b` | High-order legal reasoning, compromise fallbacks, email drafting | ≤ 6 calls |
| **4. Legal Context** | **Tavily** | `api.tavily.com` | Live statutory verification & case law precedent retrieval | ≤ 3 searches |
| **5. Synthesis** | **Super** | `nvidia/nemotron-3-super-120b-a12b` | Executive verdict, top priorities, and good terms summary | 1 call |
| **6. Scanned OCR** | **Vision** | `openbmb/MiniCPM-V-4_5` | High-fidelity transcription of scanned pages and phone photos | On upload |

> **Result:** A full 20-clause contract review takes ~1 Super + ~5 Nano + ~3 Ultra calls + 3 searches. Heavy reasoning tokens are spent only where negotiation leverage matters.

---

## 🇮🇳 Indian Statutory Context Built-In

ClauseGuard is specifically engineered for Indian legal realities:

- **Section 27, Indian Contract Act, 1872 (Restraint of Trade):** Restrictive non-compete covenants that extend beyond the term of an agreement are generally void under Indian law. ClauseGuard flags these as high-risk scare tactics.
- **Section 19, Indian Copyright Act, 1957 (Assignment of Copyright):** Assignments of future works must specifically identify the works; vague assignments of all future ideas are unenforceable.
- **Digital Personal Data Protection Act (DPDPA), 2023:** Flags unconsented cross-border transfers and ambiguous data retention clauses.
- **Section 73 & 74, Contract Act (Liquidated Damages vs. Penalties):** Disproportionate penalty clauses and unilateral forfeiture of accrued earnings are red-flagged.

---

## 🚀 Quickstart

### 1. Clone & Setup Environment

```bash
git clone https://github.com/neavdak/ClauseGuard-.git
cd ClauseGuard-/clauseguard

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy the example environment file:
```bash
cp .env.example .env
```
Populate `.env` with your credentials:
```env
NEBIUS_API_KEY=your_nebius_api_key_here
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Verify Connectivity

Test your Nebius Token Factory connection, model tier mapping, and Tavily search in under 3 seconds:
```bash
python scripts/check_keys.py
```

### 4. Run the Smoke Test

```bash
# Offline heuristic engine (zero API credits consumed):
python scripts/smoke_test.py --mock

# Live inference against Nemotron Super + Nano + Ultra:
python scripts/smoke_test.py
```

### 5. Launch the Streamlit App

```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.
Click **"📄 Load Demo Contract"** to test a realistic one-sided freelance master services agreement, then click **"⚡ Analyse contract"**.

---

## 📁 Repository Structure

```
.
├── HACKATHON_BRIEF.md          # Hackathon rules, dates, criteria, and progress log
├── IDEAS.md                    # Initial idea scoring & architectural evaluation
├── LICENSE                     # MIT Open-Source License
├── README.md                   # Project overview & documentation
└── clauseguard/
    ├── app.py                  # Streamlit web application & UI
    ├── requirements.txt        # Python dependencies
    ├── .env.example            # Environment configuration template
    ├── docs/
    │   ├── ARCHITECTURE.md     # In-depth architectural blueprint & evaluation plan
    │   ├── PLAN.md             # Execution plan, team milestones, & video script
    │   └── SETUP.md            # Account setup & credential onboarding
    ├── samples/
    │   ├── sample_freelance_msa.txt # Deliberately unbalanced demo contract
    │   └── output/             # Sample exported Markdown & JSON risk reports
    ├── scripts/
    │   ├── check_keys.py       # Fast API ping & model discovery validation
    │   ├── list_models.py      # Inspect all models hosted on Nebius Token Factory
    │   └── smoke_test.py       # End-to-end pipeline verification CLI
    └── src/clauseguard/
        ├── config.py           # Environment settings & options
        ├── models.py           # Token Factory /v1/models dynamic tier discovery
        ├── llm.py              # Router for Nano, Super, Ultra, & VL tiers
        ├── pipeline.py         # 5-stage analysis orchestrator
        ├── prompts.py          # Structured prompt builders with JSON formatting
        ├── checklist.py        # 18-category legal taxonomy & Indian statutory rules
        ├── extract.py          # Multi-format ingestion (PDF, DOCX, TXT, images)
        ├── tavily.py           # Live Indian legal precedent search wrapper
        ├── report.py           # Deterministic risk scoring & Markdown export
        ├── usage.py            # Telemetry logging for routing panel
        └── mock.py             # Deterministic heuristic engine for offline testing
```

---

## 🏆 Hackathon Compliance Checklist

| Requirement | Implementation in ClauseGuard | Status |
|---|---|---|
| **Runtime Nebius Token Factory Call** | `src/clauseguard/llm.py` connects directly to `https://api.tokenfactory.nebius.com/v1/` using the OpenAI SDK. | ✅ Verified |
| **NVIDIA Open Models** | Discovers and invokes `Nemotron-3-Super` (120B), `Nemotron-3-Nano` (30B), and `Nemotron-3-Ultra` (550B). | ✅ Verified |
| **Model Routing Pattern** | Super handles document structure & summary; Nano handles bulk classification; Ultra handles high-stakes negotiation. | ✅ Verified |
| **Tavily Integration** | `src/clauseguard/tavily.py` runs live legal searches for critical and high-risk categories. | ✅ Verified |
| **Open Source License** | Permissive [MIT License](LICENSE) at repository root. | ✅ Verified |
| **Usable Product Experience** | End-to-end working UI with live demo contract loader, copyable email templates, and JSON/Markdown export. | ✅ Verified |

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

# ⚖️ ClauseGuard — contract risk copilot for Indian freelancers, founders & tenants

> Read any contract before you sign it. ClauseGuard turns a one-sided NDA, freelance MSA, vendor agreement
> or rental contract into a plain-language risk report — with Indian legal context, ready-to-send
> negotiation emails and suggested redlines.

Built for the **Nebius × NVIDIA Global AI Hackathon** (Best Apps & Agents track).
ClauseGuard runs entirely on **NVIDIA Nemotron open models served by Nebius Token Factory**.

> ⚠️ Educational assistant, **not legal advice**. Verify important points with a qualified lawyer.

---

## The problem

Indian freelancers, solo founders, small vendors and tenants sign contracts written by the other side's
lawyers. They rarely have a lawyer on retainer, so dangerous clauses slip through — **uncapped indemnities,
perpetual IP grabs, 5-year non-competes (largely void under Indian law), distant exclusive jurisdiction,
"sole discretion" termination and forfeited payments**. These are abstract until someone is sued or never paid.

## What ClauseGuard does

1. **Upload** a PDF / text contract (or screenshot — scanned pages are read by the Nemotron vision model).
2. **Nemotron Super** (120B hybrid MoE, 1M-token context) segments long agreements into clauses.
3. **Nemotron Nano** bulk-classifies every clause against a legal checklist with severity ratings — the cheap, high-volume stage.
4. **Nemotron Ultra** is invoked *only* for critical/high clauses to produce negotiation strategy, fallback positions and a ready-to-send email.
5. **Tavily** checks current India-focused legal context for the worst clause categories.
6. You get a color-coded report: risk score, top issues, plain-English explanations, Indian statute notes, redline wording, negotiation pack, and Markdown/JSON export.

A **model-routing panel** in the app shows exactly which model ran each stage, its latency and token use —
proving the app stays responsive and credits go only where reasoning depth matters.

## Why this architecture wins

- **Model routing by design** — exactly the pattern the track brief describes: Ultra for serious reasoning, Nano/Super for everyday calls.
- **Long-context native** — full 50–100 page agreements analysed in context, no brittle RAG chunking.
- **Open & ownable** — open Nemotron weights, OpenAI-compatible API, MIT-licensed code, no vendor lock-in.
- **Product, not PoC** — upload → report → negotiation email → export, end to end.

## Tech stack

Python · Streamlit · [Nebius Token Factory](https://docs.tokenfactory.nebius.com) (OpenAI-compatible API) ·
NVIDIA Nemotron 3 **Nano / Super / Ultra (+ Nano VL)** · Tavily Search API · pdfplumber.

## Quickstart

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env                # then fill in NEBIUS_API_KEY and (optionally) TAVILY_API_KEY

# 4. See which Nemotron models your key can access
python scripts/list_models.py

# 5. Run the app
streamlit run app.py
# → http://localhost:8501 — drag in samples/sample_freelance_msa.txt
```

**No API key yet?** The app and smoke test run in an offline **mock mode** (heuristic engine) so you can
build the UI with zero credits:

```bash
python scripts/smoke_test.py                 # end-to-end run on the bundled sample contract
streamlit run app.py                          # mock mode banner appears in the sidebar
```

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `NEBIUS_API_KEY` | yes (live) | Token Factory API key |
| `NEBIUS_BASE_URL` | no | defaults to `https://api.tokenfactory.nebius.com/v1/` |
| `NEMOTRON_NANO` / `NEMOTRON_SUPER` / `NEMOTRON_ULTRA` / `NEMOTRON_VL` | no | override automatic model discovery with exact model ids |
| `TAVILY_API_KEY` | recommended | live legal-context web check |
| `MOCK_MODE` | no | `1` forces the offline engine |

## Repository layout

```
app.py                     # Streamlit UI
src/clauseguard/
  config.py                # env / .env settings
  models.py                # Token Factory /v1/models discovery + tier mapping
  llm.py                   # model router (Nano/Super/Ultra/VL), usage logging
  mock.py                  # offline heuristic engine (also the eval baseline)
  prompts.py               # all prompt builders
  checklist.py             # clause taxonomy + India-focused risk rules
  pipeline.py              # segment → classify → escalate → web-check → summarize
  extract.py               # PDF / text / image (Nemotron VL) ingestion
  tavily.py                # legal web-checks
  report.py                # risk scoring + Markdown export
  usage.py                 # routing-panel telemetry
scripts/
  list_models.py           # print available Nemotron models
  smoke_test.py            # end-to-end pipeline test (mock or live)
samples/
  sample_freelance_msa.txt # deliberately one-sided demo contract
docs/
  SETUP.md                 # account & credential setup checklist
  ARCHITECTURE.md          # architecture, routing economics, eval plan
  PLAN.md                  # team roles, 7-week schedule, demo video script
```

## Deployment (public demo URL)

- Easiest: **Streamlit Community Cloud** or **Hugging Face Spaces** (Docker SDK) — put `NEBIUS_API_KEY` /
  `TAVILY_API_KEY` in the host's secrets, deploy from this repo. The app makes runtime calls to Token
  Factory, satisfying the platform requirement.
- *(Planned)* **Nebius Serverless Jobs**: scheduled renewal/notice-date reminders and nightly re-checks
  of stored contracts; optionally a Token Factory **dedicated endpoint** with autoscaling.

## Roadmap

- [x] Core routing pipeline + offline heuristic baseline
- [ ] Live Nemotron prompt tuning against a gold set of annotated contracts
- [ ] Nemotron VL scanned-PDF/image ingestion
- [ ] DOCX support; clause-diff across contract versions
- [ ] Rental agreements (deposit/notice/lock-in) and SaaS vendor T&Os templates
- [ ] Negotiation outcome tracker ("did the counterparty accept the redline?")
- [ ] Serverless Jobs: renewal & notice-date reminders
- [ ] Hindi/Kannada/Tamil plain-language explanations

## License

[MIT](LICENSE) © ClauseGuard contributors.

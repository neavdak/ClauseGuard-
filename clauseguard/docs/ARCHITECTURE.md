# ClauseGuard architecture

## System diagram

```
                         ┌──────────────────────────────────────────────┐
                         │                 Streamlit app                 │
                         │  upload → progress → report → negotiate/export│
                         └───────────────┬──────────────────────────────┘
                                         │
                         ┌───────────────▼──────────────────────────────┐
                         │              pipeline.py (orchestrator)       │
                         └───┬───────────┬───────────┬───────────┬──────┘
                             │           │           │           │
                  1 segment  │ 2 classify│ 3 escalate│ 5 summary │ 4 web
                             ▼           ▼           ▼           ▼
                  ┌──────────────────┐  ┌──────────────────────┐  ┌─────────┐
                  │ Nemotron SUPER   │  │ Nemotron NANO (batch)│  │ Tavily  │
                  │ 120B MoE, 1M ctx │  │ cheap bulk tagging    │  │ search  │
                  └──────────────────┘  └──────────────────────┘  └─────────┘
                                                  │ critical/high only
                                                  ▼
                                       ┌──────────────────────┐
                                       │ Nemotron ULTRA       │
                                       │ negotiation strategy │
                                       └──────────────────────┘

   Optional: Nemotron Nano VL ── scanned pages / photos (extract.py)
   (Planned) Nebius Serverless Jobs ── renewal/notice reminders, nightly law re-checks

   All LLM calls: OpenAI-compatible POST https://api.tokenfactory.nebius.com/v1/chat/completions
```

## Request shape (standard OpenAI SDK, only base_url changes)

```python
from openai import OpenAI
client = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=NEBIUS_API_KEY)
client.chat.completions.create(
    model="<auto-discovered nemotron id>",
    messages=[...],
    response_format={"type": "json_object"},   # structured clause analyses
)
```

## Pipeline stages and routing economics

| Stage | Model | Why this tier | Frequency per contract |
|---|---|---|---|
| Segmentation | **Super** | 1M-token context reads entire agreement; structural accuracy matters most | 1 call |
| Classification + redlines | **Nano** | High-volume, template-style judgement; cheapest per token; batches of 4 clauses | ⌈N/4⌉ calls |
| Deep negotiation pack | **Ultra** | Only critical/high clauses (cap 6/doc); highest reasoning, used sparingly | ≤6 calls |
| Legal web check | **Tavily** | Grounds statute/current-practice claims with citations | ≤3 searches |
| Executive summary | **Super** | Synthesises across all analyses | 1 call |
| OCR (scans/photos) | **Nano VL** | Vision transcription only when no embedded text exists | optional |

Result: a typical 20-clause review is ~1 Super + ~5 Nano + 2–6 Ultra calls + 3 searches.
The routing panel surfaces these counts, latency and tokens — this is the "your credits
stretch further" story the brief explicitly rewards.

## Structured-output contract

- Segment → `{"clauses": [{clause_id, title, text}]}`
- Analyse → `{"analyses": [{clause_id, title, text, category, category_label, severity,
  summary, plain_english, risk_explanation, indian_law_note, suggested_redline}]}`
- Escalate → `{severity_review, negotiation_strategy[], fallback_positions[], email_draft}`
- Summary → `{verdict, top_issues[], negotiation_priorities[], good_practices[]}`

`llm.parse_jsonish()` strips code fences and recovers JSON from prose wrappers.

## Fallback & reliability rules

1. **Discovery**: `GET /v1/models` → keyword match (nemotron-3 preferred); env vars override; cached 6 h.
2. Ultra unavailable on the account → Ultra tier silently maps to Super.
3. JSON response malformed → fence-stripping + regex recovery; call failures raise with a clear message.
4. No API key / credits pending → deterministic **mock engine** (`mock.py` + `checklist.RISK_RULES`)
   lets UI work continue; the same engine is the regression baseline for evals.
5. Clause guarantees: even if the model drops a clause from output, the pipeline reattaches it.

## Risk scoring (deterministic, shown next to the LLM verdict)

`score = min(100, Σ weights)` with weights critical 25 / high 12 / medium 5 / low 2.
Bands: 0–14 🟢 low · 15–39 🟡 medium · 40–69 🟠 high · 70+ 🔴 critical.
Keeping score deterministic prevents model mood-swings between runs and makes evals measurable.

## Evaluation plan (quality is a judged criterion)

- **Gold set**: 15–20 real-ish contracts (NDAs, freelance MSAs, rental agreements, SaaS T&Os),
  each with clauses annotated by the team using a practising lawyer's checklist (friends,
  startup programmes, NSLS/law-school clinics can help review annotations).
- Metrics per stage:
  - Segmentation: clause boundary F1 vs. manual split.
  - Classification: severity agreement (Cohen's κ) and exact category accuracy.
  - Risk recall: did it flag every gold-flagged clause? (false negatives are worst — a missed
    uncapped indemnity is the product's nightmare; optimise recall, then precision.)
  - Redline usefulness: blind 1–5 rating from 3 reviewers on 20 outputs.
- Routing experiment: Nano-only vs Nano+Ultra, record quality delta and token cost; graph it.
- Keep `samples/output/report.json` across runs and diff.

## Privacy

- Documents go only to Token Factory inference (optionally a **zero-retention dedicated
  endpoint** — a real Token Factory feature) and Tavily (query strings only, never full docs).
- No storage server; in the hosted demo the file lives only in the Streamlit session.
- State this on the landing page and in the video — legal documents are sensitive data.

## Future Nebius-native extensions (pick in week 5–6 if time allows)

1. **Serverless Job (cron)**: email/WhatsApp reminder before renewal, notice and payment dates
   extracted from stored contracts.
2. **Dedicated endpoint**: deploy a chosen Nemotron build to an autoscaling endpoint for the demo
   (99.9 SLA story), call it via its routing key.
3. **Fine-tune / post-training**: LoRA on the gold clause set, then one-click deploy —
   demonstrates Token Factory's model-lifecycle story (strong feedback/judging angle).

# Setup checklist — do these once as a team

## 1. Devpost (team rep + every member)
1. Log in to Devpost (you've registered for the hackathon ✅).
2. The team rep clicks **Join Hackathon** and creates the project draft.
3. Each teammate joins Devpost and is invited to the project (Submission → Team).
4. Decide who the **Representative** is (the person who submits).

## 2. Nebius Builder Program — free credits
1. Join the Builder Program: <https://dev.nebius.com/builders>
   (gives Token Factory credits, Tavily credits, Nebius Academy + office hours).
2. Complete onboarding and open the **Token Factory** console.
3. Create an **API key**, copy it immediately (shown once).
4. From the repo root:
   ```bash
   cp .env.example .env
   # paste: NEBIUS_API_KEY=nf_...
   pip install -r requirements.txt
   python scripts/list_models.py
   ```
5. Note the printed model ids for Nano / Super / Ultra (and VL). If discovery
   misses any, paste exact ids into `.env` (`NEMOTRON_SUPER=...` etc.).
6. Sanity check live mode:
   ```bash
   python scripts/smoke_test.py
   ```
   The header should say `Mode: LIVE (Nebius Token Factory)`.

## 3. Tavily (needed for the Best Use of Tavily prize — $3,000)
1. Sign up at <https://tavily.com> (free tier; extra credits may come via Builder Program).
2. Create an API key and add `TAVILY_API_KEY=...` to `.env`.
3. Re-run the smoke test with web checks enabled (set `use_tavily=True`, or
   just run the app and leave the Tavily toggle on).

## 4. GitHub repository
1. Create a **public** GitHub repo, e.g. `clauseguard`.
2. When creating it, pick the **MIT License** template (the license must be
   visible at the top of the repo page per hackathon rules).
3. Push this code; add all teammates as collaborators.
4. Pin the repo topics: `nebius`, `nemotron`, `nvidia`, `llm`, `legaltech`, `streamlit`.
5. Protect nothing complicated: `main` deploys; use feature branches + PRs.

## 5. Local dev environment (each member)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pre-commit sanity check:  python scripts/smoke_test.py
run UI:                   streamlit run app.py
```
Python 3.11+ recommended (3.13 works).

## 6. Hosted demo (aim to have this by Oct 13)
1. Push the repo to GitHub.
2. Deploy on **Streamlit Community Cloud** (Deploy app → pick repo → `app.py`)
   or a **Hugging Face Space** (Streamlit Docker template).
3. Add secrets in the host UI: `NEBIUS_API_KEY`, `TAVILY_API_KEY`.
4. Open the public URL on a phone/laptop, run the sample contract, save the URL.
5. If the host needs allow-listing, the only outbound hosts are
   `api.tokenfactory.nebius.com` and `api.tavily.com`.

## 7. Required submission assets (track in PLAN.md)
- [ ] Public demo URL (login-free; put test creds in Devpost if gated)
- [ ] Public GitHub repo with MIT license at top + this README
- [ ] YouTube video ≤ 3:00, public, with voiceover naming Nebius + Nemotron
- [ ] Project description (what / why / how)
- [ ] Written feedback on Token Factory + Tavily (keep a FEEDBACK.md from day 1)
- [ ] Track selection: **Best Apps & Agents**
- [ ] Bengaluru Builders & Brews attendance? Check <https://luma.com/builderandbrews?k=c>
      ($500 City Winner award)

## Troubleshooting
- **`No model mapped for tier …`** → run `python scripts/list_models.py`; set the
  `NEMOTRON_*` overrides in `.env`.
- **401/403 from Token Factory** → check the key, no quotes/spaces in `.env`.
- **Empty PDF warning** → it's a scanned PDF; upload a page image with a VL model mapped.
- **No legal web results** → Tavily key missing or free quota exhausted.

"""End-to-end smoke test on the sample contract (or any .txt/.md file).

Usage:
  python scripts/smoke_test.py                     # bundled sample; live if a key exists
  python scripts/smoke_test.py path/to/file.txt    # analyse your own text contract
  python scripts/smoke_test.py --no-tavily         # skip the Tavily web check
  python scripts/smoke_test.py --mock              # force the offline heuristic engine
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from clauseguard.config import settings  # noqa: E402
from clauseguard.pipeline import analyze_document  # noqa: E402
from clauseguard.report import band, to_markdown  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="ClauseGuard end-to-end smoke test")
    parser.add_argument("file", nargs="?", default=None, help="path to a .txt/.md contract")
    parser.add_argument("--no-tavily", action="store_true", help="skip the Tavily web check")
    parser.add_argument("--mock", action="store_true", help="force offline mock mode")
    args = parser.parse_args()

    path = Path(args.file) if args.file else ROOT / "samples" / "sample_freelance_msa.txt"
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)
    if path.suffix.lower() not in (".txt", ".md"):
        print(f"This script only reads .txt/.md directly (use the UI for PDF/images): {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="ignore")

    use_tavily = (not args.no_tavily) and bool(settings.tavily_key)
    if args.mock:
        settings.mock_mode = True

    print(f"Mode:           {'MOCK (offline heuristics)' if settings.mock_mode else 'LIVE (Nebius Token Factory)'}")
    print(f"Tavily:         {'ON' if use_tavily else 'OFF' + ('' if args.no_tavily or not settings.tavily_key else '')}")
    print(f"Document:       {path.name} ({len(text)} chars)")
    if not settings.mock_mode:
        print(f"Models:         nano={settings.model_nano or 'auto'}  super={settings.model_super or 'auto'}"
              f"  ultra={settings.model_ultra or 'auto'}")
    print()

    def on_stage(done: int, total: int, label: str) -> None:
        print(f"  [{done}/{total}] {label}")

    started = time.time()
    report = analyze_document(path.name, text, use_tavily=use_tavily, on_stage=on_stage)
    elapsed = time.time() - started

    out_dir = ROOT / "samples" / "output"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "report.md").write_text(to_markdown(report), encoding="utf-8")

    print("\n=== RESULT ===")
    score = report["risk_score"]
    score_band, band_label = band(score)
    print(f"Risk score:     {score}/100 ({score_band} - {band_label})")
    print(f"Verdict:        {report['summary'].get('verdict', '')}")
    counts: dict[str, int] = {}
    for a in report["analyses"]:
        counts[a["severity"]] = counts.get(a["severity"], 0) + 1
    print(f"Clauses:        {len(report['analyses'])}  severities={counts}")
    escalated = [a for a in report["analyses"] if a.get("email_draft")]
    print(f"Escalated:      {len(escalated)} clauses got negotiation packs")
    print(f"Legal updates:  {len(report.get('legal_updates', []))} Tavily topic groups")
    usage = report["usage"]
    print(f"Model calls:    {usage['num_calls']}  |  tokens: {usage['total_tokens']}"
          f"  |  wall time: {elapsed:.1f}s")
    print(f"Calls by tier:  {usage['calls_by_tier']}")
    print(f"\nWritten:        {out_dir / 'report.md'}")
    print(f"Written:        {out_dir / 'report.json'}")


if __name__ == "__main__":
    main()

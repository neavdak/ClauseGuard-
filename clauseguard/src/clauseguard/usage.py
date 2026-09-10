"""Tiny usage ledger — powers the "model routing panel" shown in the UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CallRecord:
    tier: str
    model: str
    purpose: str
    latency_s: float
    prompt_tokens: int = 0
    completion_tokens: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "model": self.model,
            "purpose": self.purpose,
            "latency_s": round(self.latency_s, 2),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }


@dataclass
class UsageLog:
    calls: list[CallRecord] = field(default_factory=list)

    def record(self, rec: CallRecord) -> None:
        self.calls.append(rec)

    @property
    def total_tokens(self) -> int:
        return sum(c.prompt_tokens + c.completion_tokens for c in self.calls)

    @property
    def total_latency_s(self) -> float:
        return round(sum(c.latency_s for c in self.calls), 2)

    def by_tier(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.calls:
            out[c.tier] = out.get(c.tier, 0) + 1
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "calls": [c.to_dict() for c in self.calls],
            "num_calls": len(self.calls),
            "total_tokens": self.total_tokens,
            "total_latency_s": self.total_latency_s,
            "calls_by_tier": self.by_tier(),
        }

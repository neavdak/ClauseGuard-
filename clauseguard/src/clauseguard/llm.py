"""Token Factory model router.

One OpenAI-compatible client pointed at Nebius; three quality/cost tiers
mapped to NVIDIA Nemotron models. Every call is logged for the routing panel.
"""
from __future__ import annotations

import json
import re
import time
from typing import Any

from . import mock, models
from .config import settings
from .usage import CallRecord, UsageLog


class LLMError(RuntimeError):
    pass


def parse_jsonish(text: str) -> Any:
    t = text.strip()
    t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
    t = re.sub(r"```\s*$", "", t).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        earliest: tuple[int, str] | None = None
        for m in re.finditer(r"\{.*\}|\[.*\]", t, re.S):
            if earliest is None or m.start() < earliest[0]:
                earliest = (m.start(), m.group())
        if earliest:
            return json.loads(earliest[1])
        raise


class Router:
    def __init__(self, usage: UsageLog | None = None, force_discover: bool = False):
        self.tiers = models.discover(force=force_discover)
        self.usage = usage or UsageLog()
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:  # pragma: no cover
                raise LLMError("Install dependencies: pip install -r requirements.txt") from exc
            self._client = OpenAI(
                api_key=settings.api_key,
                base_url=settings.base_url,
                timeout=settings.request_timeout,
            )
        return self._client

    def model_for(self, tier: str) -> str:
        model = self.tiers.get(tier)
        if not model:
            raise LLMError(
                f"No model mapped for tier '{tier}'. Run `python scripts/list_models.py` "
                "or set NEMOTRON_NANO / NEMOTRON_SUPER / NEMOTRON_ULTRA in .env"
            )
        return model

    def complete(
        self,
        tier: str,
        messages: list[dict],
        *,
        purpose: str = "",
        json_mode: bool = True,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        started = time.time()
        if settings.mock_mode:
            content = mock.respond(purpose, messages)
            model_name = f"mock-{tier}"
            prompt_tokens = (len(json.dumps(messages))) // 4
            completion_tokens = len(content) // 4
        else:
            model_name = self.model_for(tier)
            kwargs: dict[str, Any] = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            try:
                resp = self._get_client().chat.completions.create(**kwargs)
            except Exception as exc:
                raise LLMError(f"Token Factory call failed ({tier}/{model_name}): {exc}") from exc
            content = resp.choices[0].message.content or ""
            prompt_tokens = getattr(resp.usage, "prompt_tokens", 0) if resp.usage else 0
            completion_tokens = getattr(resp.usage, "completion_tokens", 0) if resp.usage else 0

        self.usage.record(
            CallRecord(
                tier=tier,
                model=model_name,
                purpose=purpose,
                latency_s=time.time() - started,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
        )
        return content

    def json(self, tier: str, messages: list[dict], *, purpose: str = "", **kw: Any) -> Any:
        return parse_jsonish(self.complete(tier, messages, purpose=purpose, json_mode=True, **kw))

    def complete_vision(self, text_prompt: str, image_b64: str, mime: str, *, purpose: str = "") -> str:
        """Single-image call against the Nemotron VL model."""
        started = time.time()
        if settings.mock_mode or not self.tiers.get("vl"):
            self.usage.record(CallRecord("vl", self.tiers.get("vl") or "mock-vl", purpose, time.time() - started))
            return ""
        model_name = self.model_for("vl")
        try:
            resp = self._get_client().chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=4000,
            )
        except Exception as exc:
            raise LLMError(f"Vision call failed ({model_name}): {exc}") from exc
        content = resp.choices[0].message.content or ""
        self.usage.record(
            CallRecord(
                "vl", model_name, purpose, time.time() - started,
                getattr(resp.usage, "prompt_tokens", 0) if resp.usage else 0,
                getattr(resp.usage, "completion_tokens", 0) if resp.usage else 0,
            )
        )
        return content

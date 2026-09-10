"""Runtime configuration, loaded from environment variables / local .env file."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_MD_LINK = re.compile(r"^\[(?P<url>[^\]]+)\]\([^)]*\)$")


def _clean_value(value: str) -> str:
    value = value.strip().strip('"').strip("'").strip()
    m = _MD_LINK.match(value)  # accidentally pasted a Markdown link, e.g. [https://x](https://x)
    if m:
        value = m.group("url").strip()
    return value


def _read_text_lenient(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeError, OSError):
            continue
    return ""


def _parse_env_file(path: Path) -> None:
    """Dependency-free .env reader (also used as a python-dotenv fallback)."""
    raw = _read_text_lenient(path)
    if not raw:
        return
    for line in raw.splitlines():
        line = line.replace("\x00", "").strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), _clean_value(value))


def _load_env() -> None:
    candidates = [Path.cwd() / ".env", ROOT / ".env"]
    existing = [p for p in candidates if p.exists()]
    try:
        from dotenv import load_dotenv

        for env_path in existing:
            load_dotenv(env_path, override=False)
    except Exception:
        pass
    for env_path in existing:  # dependency-free pass fills anything dotenv missed/mangled
        _parse_env_file(env_path)


_load_env()


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass
class Settings:
    api_key: str = field(default_factory=lambda: _get("NEBIUS_API_KEY"))
    base_url: str = field(
        default_factory=lambda: _get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
    )
    tavily_key: str = field(default_factory=lambda: _get("TAVILY_API_KEY"))
    model_nano: str = field(default_factory=lambda: _get("NEMOTRON_NANO"))
    model_super: str = field(default_factory=lambda: _get("NEMOTRON_SUPER"))
    model_ultra: str = field(default_factory=lambda: _get("NEMOTRON_ULTRA"))
    model_vl: str = field(default_factory=lambda: _get("NEMOTRON_VL"))
    request_timeout: int = field(
        default_factory=lambda: int(_get("REQUEST_TIMEOUT", "120") or 120)
    )
    mock_mode: bool = field(init=False)

    def __post_init__(self) -> None:
        forced = _get("MOCK_MODE", "").lower() in {"1", "true", "yes"}
        self.mock_mode = forced or not bool(self.api_key)


settings = Settings()

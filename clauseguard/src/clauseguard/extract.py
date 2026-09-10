"""Document ingestion: .txt/.md, text PDFs, and (via Nemotron VL) scanned images."""
from __future__ import annotations

import base64
import io

from .llm import Router

MAX_CHARS = 900_000  # Nemotron 3 Super supports up to ~1M tokens; keep headroom.


def _decode(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def extract_text(filename: str, data: bytes, router: Router | None = None) -> dict:
    """Returns {'text': str, 'warning': str}. Warning is '' on clean extraction."""
    name = filename.lower()

    if name.endswith((".txt", ".md", ".text")):
        return {"text": _decode(data)[:MAX_CHARS], "warning": ""}

    if name.endswith(".pdf"):
        try:
            import pdfplumber
        except ImportError:
            return {"text": "", "warning": "PDF support needs `pip install pdfplumber`."}
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text = "\n\n".join((page.extract_text() or "") for page in pdf.pages)
        except Exception as exc:  # pragma: no cover
            return {"text": "", "warning": f"Could not read PDF: {exc}"}
        if len(text.strip()) < 100:
            return {
                "text": text,
                "warning": (
                    "This looks like a SCANNED PDF (no embedded text). "
                    "Upload a screenshot/page image (Nemotron VL reads it) or paste the text."
                ),
            }
        return {"text": text[:MAX_CHARS], "warning": ""}

    if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        if router is None or not router.tiers.get("vl"):
            return {
                "text": "",
                "warning": "Image reading needs the Nemotron VL model (set NEMOTRON_VL with a live API key).",
            }
        mime = "image/png" if name.endswith(".png") else "image/jpeg"
        b64 = base64.b64encode(data).decode()
        raw = router.complete_vision(
            "Transcribe every word of this contract page faithfully, preserving headings and numbering. "
            "Return only the transcribed text.",
            b64,
            mime,
            purpose="ocr_scan",
        )
        if not raw.strip():
            return {"text": "", "warning": "Vision model returned no text."}
        return {"text": raw[:MAX_CHARS], "warning": ""}

    return {"text": "", "warning": f"Unsupported file type: {filename}. Use PDF, TXT, PNG or JPG."}

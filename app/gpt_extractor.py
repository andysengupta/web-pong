from __future__ import annotations

import base64
import json
import re
import time
from typing import Any, Dict, Optional

from openai import OpenAI


DEFAULT_SYSTEM_PROMPT = (
    "You are a meticulous document parser. Extract the document structure from the image. "
    "Return ONLY valid minified JSON with keys: headings, paragraphs, tables. "
    "- headings: array of objects: {level: 1|2|3, text: string} in visual order.\n"
    "- paragraphs: array of strings, preserving original paragraph boundaries and order.\n"
    "- tables: array of objects: {caption?: string, headers: string[], rows: string[][]} in visual order.\n"
    "Keep text accurate, fix obvious OCR errors if trivial. Do not invent content."
)


def _data_uri_for_png(image_bytes: bytes) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _extract_json(text: str) -> Dict[str, Any]:
    # Prefer fenced code blocks if present
    fence_match = re.search(r"```(?:json)?\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    candidate = fence_match.group(1).strip() if fence_match else text.strip()

    # If extra prose surrounds JSON, attempt to isolate the first JSON object/array
    if not candidate.lstrip().startswith(("{", "[")):
        brace_start = candidate.find("{")
        bracket_start = candidate.find("[")
        starts = [s for s in (brace_start, bracket_start) if s != -1]
        if starts:
            candidate = candidate[min(starts):]

    # Try direct JSON parse
    try:
        data = json.loads(candidate)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {"headings": [], "paragraphs": [], "tables": data}
    except Exception:
        pass

    # Fallback minimal structure
    return {"headings": [], "paragraphs": [text.strip()], "tables": []}


def extract_page_structure_from_image(
    image_bytes: bytes,
    client: Optional[OpenAI] = None,
    model: str = "gpt-4o-mini",
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    max_retries: int = 3,
    retry_backoff_sec: float = 2.0,
) -> Dict[str, Any]:
    """
    Use GPT Vision to extract structured page content from a rendered page image.

    Returns a dict with keys: headings (list), paragraphs (list), tables (list).
    """
    if client is None:
        client = OpenAI()

    image_url = _data_uri_for_png(image_bytes)

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract structure and return JSON only."},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        },
    ]

    last_error: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            data = _extract_json(content)

            # Normalize fields
            headings = data.get("headings") or []
            paragraphs = data.get("paragraphs") or []
            tables = data.get("tables") or []

            return {
                "headings": headings,
                "paragraphs": paragraphs,
                "tables": tables,
            }
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_retries - 1:
                time.sleep(retry_backoff_sec * (2 ** attempt))
            else:
                raise

    # Unreachable due to raise, but keeps type checkers happy
    raise RuntimeError(f"Failed to extract page after retries: {last_error}")
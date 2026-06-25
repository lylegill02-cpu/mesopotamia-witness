#!/usr/bin/env python3
"""One-off helper: parse King 1902 Enuma Elish from sacred-texts dump into akkadian JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "akkadian" / "_king_enuma_raw.txt"
OUT = ROOT / "data" / "akkadian" / "enuma.elish.json"

TABLET_RE = re.compile(
    r"THE (FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH) TABLET",
    re.I,
)
ROMAN = {
    "FIRST": "I",
    "SECOND": "II",
    "THIRD": "III",
    "FOURTH": "IV",
    "FIFTH": "V",
    "SIXTH": "VI",
    "SEVENTH": "VII",
}


def chunk_text(text: str, tablet: str, chunk_size: int = 450) -> list[dict]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = []
    words = text.split()
    buf: list[str] = []
    n = 0
    for w in words:
        buf.append(w)
        if len(" ".join(buf)) >= chunk_size:
            n += 1
            parts.append(
                {
                    "para_id": f"{tablet}.{n}",
                    "line_range": f"{tablet} §{n}",
                    "line_start": n,
                    "translation": " ".join(buf),
                }
            )
            buf = []
    if buf:
        n += 1
        parts.append(
            {
                "para_id": f"{tablet}.{n}",
                "line_range": f"{tablet} §{n}",
                "line_start": n,
                "translation": " ".join(buf),
            }
        )
    return parts


def main() -> None:
    if not SRC.exists():
        print(f"Skip — no {SRC}")
        return
    raw = SRC.read_text(encoding="utf-8")
    # strip HTML-ish header if present
    idx = raw.find("THE FIRST TABLET")
    if idx > 0:
        raw = raw[idx:]
    markers = list(TABLET_RE.finditer(raw))
    paragraphs = []
    for i, m in enumerate(markers):
        name = m.group(1).upper()
        tablet = ROMAN[name]
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(raw)
        body = raw[start:end]
        # stop at epilogue / alternate version
        for stop in ("END OF THE CREATION EPIC", "THE FIGHT WITH TIAMAT"):
            si = body.find(stop)
            if si > 0:
                body = body[:si]
        paragraphs.extend(chunk_text(body, tablet))
    out = {
        "text_id": "akkadian.enuma.elish",
        "title": "Enuma Elish (The Seven Tablets of Creation)",
        "language": "akkadian",
        "translation_source": "L.W. King, The Seven Tablets of Creation, London 1902 (public domain)",
        "translation_url": "https://www.sacred-texts.com/ane/stc/index.htm",
        "paragraphs": paragraphs,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(paragraphs)} paragraphs)")


if __name__ == "__main__":
    main()

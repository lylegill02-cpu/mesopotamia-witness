#!/usr/bin/env python3
"""Rebuild enuma.elish.json from King 1902 raw with OCR cleanup."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.king_text import ENUMa_LINES, parse_king_raw  # noqa: E402

SRC = ROOT / "data" / "akkadian" / "_king_enuma_raw.txt"
OUT = ROOT / "data" / "akkadian" / "enuma.elish.json"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing {SRC}")

    raw = SRC.read_text(encoding="utf-8")
    paragraphs = parse_king_raw(raw)
    doc = {
        "text_id": "akkadian.enuma.elish",
        "title": "Enuma Elish (The Seven Tablets of Creation)",
        "language": "akkadian",
        "translation_source": "L.W. King, The Seven Tablets of Creation, London 1902 (public domain, cleaned)",
        "translation_url": "https://archive.org/details/seventabletsofc00kinguoft",
        "paragraphs": paragraphs,
        "lines": ENUMa_LINES,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}: {len(paragraphs)} paragraphs, {len(ENUMa_LINES)} lines")


if __name__ == "__main__":
    main()

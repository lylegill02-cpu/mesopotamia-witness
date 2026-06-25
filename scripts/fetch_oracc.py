#!/usr/bin/env python3
"""Fetch ORACC AMGG + ETCSRI HTML and write data/oracc/*.json."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.oracc_html import extract_amgg_entry, extract_etcsri_text  # noqa: E402

ORACC_DIR = ROOT / "data" / "oracc"
CACHE_DIR = ORACC_DIR / "_cache"

SOURCES = {
    "amgg.anunna": {
        "url": "https://oracc.museum.upenn.edu/amgg/Listofdeities/Anunna/index.html",
        "kind": "amgg",
        "text_id": "oracc.amgg.anunna",
        "ref": "AMGG.anunna",
    },
    "etcsri.gudea_sample": {
        "url": "https://oracc.museum.upenn.edu/etcsri/Q004866",
        "kind": "etcsri",
        "text_id": "oracc.etcsri.Q004866",
    },
}


def fetch(url: str, cache_path: Path, force: bool = False) -> str:
    if cache_path.exists() and not force and cache_path.stat().st_size > 500:
        return cache_path.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": "mesopotamia-witness/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(body, encoding="utf-8")
    return body


def build_doc(key: str, spec: dict, html_text: str) -> dict:
    if spec["kind"] == "amgg":
        parsed = extract_amgg_entry(html_text)
        paragraphs = [
            {
                "para_id": f"p{i + 1}",
                "line_range": p.get("heading", ""),
                "translation": p["translation"],
            }
            for i, p in enumerate(parsed["paragraphs"])
        ]
        return {
            "text_id": spec["text_id"],
            "corpus": "oracc",
            "title": parsed["title"],
            "language": "english",
            "translation_source": "ORACC AMGG — CC BY-SA 3.0",
            "source_url": spec["url"],
            "paragraphs": paragraphs,
            "lines": parsed.get("lines", []),
        }

    parsed = extract_etcsri_text(html_text)
    return {
        "text_id": spec["text_id"],
        "corpus": "oracc",
        "title": parsed["title"],
        "language": "sumerian",
        "translation_source": "ORACC ETCSRI — CC BY-SA 3.0",
        "source_url": spec["url"],
        "paragraphs": parsed["paragraphs"],
        "lines": parsed["lines"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch ORACC HTML into JSON corpus files")
    parser.add_argument("--force", action="store_true", help="Re-download cached HTML")
    args = parser.parse_args()

    ORACC_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for key, spec in SOURCES.items():
        cache = CACHE_DIR / f"{key}.html"
        try:
            html_text = fetch(spec["url"], cache, force=args.force)
        except (urllib.error.URLError, TimeoutError) as err:
            out = ORACC_DIR / f"{key}.json"
            if out.exists():
                print(f"Skip {key} (fetch failed, using existing JSON): {err}")
                continue
            raise SystemExit(f"Fetch failed for {key}: {err}") from err

        doc = build_doc(key, spec, html_text)
        out = ORACC_DIR / f"{key}.json"
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"Wrote {out.name}: {len(doc.get('paragraphs', []))} paragraphs, "
            f"{len(doc.get('lines', []))} lines"
        )
        written += 1

    print(f"Done — {written} ORACC text(s)")


if __name__ == "__main__":
    main()

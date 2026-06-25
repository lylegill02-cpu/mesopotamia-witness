#!/usr/bin/env python3
"""Bulk-fetch ETCSRI royal inscriptions from ORACC HTML."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.oracc_html import extract_etcsri_text  # noqa: E402

OUTLINE_URL = "https://oracc.museum.upenn.edu/etcsri/outlined.lst"
OUT_DIR = ROOT / "data" / "oracc" / "etcsri"
CACHE_DIR = ROOT / "data" / "oracc" / "_cache"


def fetch(url: str, cache: Path, force: bool = False) -> str:
    if cache.exists() and not force and cache.stat().st_size > 500:
        return cache.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": "mesopotamia-witness/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(body, encoding="utf-8")
    return body


def parse_qids(html: str) -> list[str]:
    ids = set(re.findall(r'data-iref="(Q\d+)"', html))
    return sorted(ids)


def build_doc(qid: str, parsed: dict) -> dict:
    return {
        "text_id": f"oracc.etcsri.{qid}",
        "corpus": "oracc",
        "title": parsed["title"],
        "language": "sumerian",
        "translation_source": "ORACC ETCSRI — CC BY-SA 3.0",
        "source_url": f"https://oracc.museum.upenn.edu/etcsri/{qid}",
        "paragraphs": parsed["paragraphs"],
        "lines": parsed["lines"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch ETCSRI inscriptions from ORACC")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max texts (0 = all on outline page)")
    parser.add_argument("--delay", type=float, default=0.35, help="Seconds between fetches")
    args = parser.parse_args()

    outline = fetch(OUTLINE_URL, CACHE_DIR / "etcsri_outlined.lst", force=args.force)
    qids = parse_qids(outline)
    if args.limit:
        qids = qids[: args.limit]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = skip = 0
    for qid in qids:
        out = OUT_DIR / f"{qid}.json"
        url = f"https://oracc.museum.upenn.edu/etcsri/{qid}"
        cache = CACHE_DIR / f"etcsri_{qid}.html"
        try:
            html = fetch(url, cache, force=args.force)
            parsed = extract_etcsri_text(html)
            if not parsed.get("lines") and not parsed.get("paragraphs"):
                print(f"Skip {qid} (empty parse)")
                skip += 1
                continue
            doc = build_doc(qid, parsed)
            out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Wrote {out.name}: {len(doc['lines'])} lines, {len(doc['paragraphs'])} paras")
            ok += 1
        except (urllib.error.URLError, TimeoutError) as err:
            if out.exists():
                print(f"Skip {qid} (fetch failed, keeping existing): {err}")
                skip += 1
            else:
                print(f"Failed {qid}: {err}")
                skip += 1
        time.sleep(args.delay)

    index = {
        "corpus": "etcsri",
        "source": OUTLINE_URL,
        "count": len(list(OUT_DIR.glob("Q*.json"))),
        "text_ids": sorted(p.stem for p in OUT_DIR.glob("Q*.json")),
    }
    (ROOT / "data" / "etcsri_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Done — wrote {ok}, skipped {skip}, index {index['count']} texts")


if __name__ == "__main__":
    main()

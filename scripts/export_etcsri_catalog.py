#!/usr/bin/env python3
"""Build etcsri_catalog.json + etcsri_index.json from committed data/oracc/etcsri/Q*.json."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ETCSRI_DIR = ROOT / "data" / "oracc" / "etcsri"
WEB_DATA = ROOT / "web" / "data"
DATA_DIR = ROOT / "data"
CORPUS_URL = "https://oracc.museum.upenn.edu/etcsri/corpus"


def build() -> tuple[dict, dict]:
    texts: list[dict] = []
    text_ids: list[str] = []
    if ETCSRI_DIR.exists():
        for path in sorted(ETCSRI_DIR.glob("Q*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            qid = path.stem
            text_ids.append(qid)
            texts.append(
                {
                    "text_id": doc.get("text_id", f"oracc.etcsri.{qid}"),
                    "title": doc.get("title"),
                    "line_count": len(doc.get("lines", [])),
                }
            )
    catalog = {"corpus": "etcsri", "count": len(texts), "texts": texts}
    index = {
        "corpus": "etcsri",
        "source": CORPUS_URL,
        "count": len(text_ids),
        "text_ids": text_ids,
    }
    return catalog, index


def main() -> None:
    catalog, index = build()
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    for name, obj in (("etcsri_catalog.json", catalog), ("etcsri_index.json", index)):
        raw = json.dumps(obj, ensure_ascii=False, indent=2)
        (WEB_DATA / name).write_text(raw, encoding="utf-8")
        out = DATA_DIR / name
        out.write_text(raw, encoding="utf-8")
    print(f"Wrote etcsri catalog ({catalog['count']} texts) to web/data/")


if __name__ == "__main__":
    main()

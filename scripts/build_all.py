#!/usr/bin/env python3
"""Build unified corpus.db: ETCSL + Akkadian, export catalogs."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WEB_DATA = ROOT / "web" / "data"
AKK_DIR = ROOT / "data" / "akkadian"


def run(name: str) -> None:
    print(f"\n=== {name} ===")
    subprocess.run([sys.executable, str(SCRIPTS / name)], check=True, cwd=ROOT)


def export_akkadian_catalog() -> None:
    texts = []
    for path in sorted(AKK_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        texts.append(
            {
                "text_id": doc["text_id"],
                "title": doc.get("title"),
                "translation_source": doc.get("translation_source"),
                "paragraph_count": len(doc.get("paragraphs", [])),
            }
        )
    catalog = {"corpus": "akkadian", "count": len(texts), "texts": texts}
    out = ROOT / "data" / "akkadian_catalog.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out, WEB_DATA / "akkadian_catalog.json")
    shutil.copy2(ROOT / "data" / "flood_comparison.json", WEB_DATA / "flood_comparison.json")
    print(f"Wrote {out} ({len(texts)} texts)")


def main() -> None:
    run("fetch_etcsl.py")
    run("build_etcsl_index.py")
    run("merge_akkadian_index.py")
    run("export_corpus.py")
    export_akkadian_catalog()
    run("merge_witness_deltas.py")
    run("sync_loci.py")
    for name in (
        "loci_chart.json",
        "corpus.json",
        "etcsl_texts.json",
        "english_glossary.json",
        "flood_comparison.json",
        "akkadian_catalog.json",
    ):
        src = ROOT / "data" / name if (ROOT / "data" / name).exists() else WEB_DATA / name
        if (ROOT / "data" / name).exists():
            shutil.copy2(ROOT / "data" / name, WEB_DATA / name)
    print("\nDone — corpus.db ready; copy web/data/ or push.")


if __name__ == "__main__":
    main()

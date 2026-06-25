#!/usr/bin/env python3
"""Build unified corpus.db: ETCSL + Akkadian + ORACC, export catalogs."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WEB_DATA = ROOT / "web" / "data"
EXTRA_DIRS = (ROOT / "data" / "akkadian", ROOT / "data" / "oracc")


def run(name: str) -> None:
    print(f"\n=== {name} ===")
    subprocess.run([sys.executable, str(SCRIPTS / name)], check=True, cwd=ROOT)


def export_extra_catalogs() -> None:
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    for corpus, directory in (("akkadian", ROOT / "data" / "akkadian"), ("oracc", ROOT / "data" / "oracc")):
        texts = []
        if directory.exists():
            for path in sorted(directory.glob("*.json")):
                if path.name.startswith("_"):
                    continue
                doc = json.loads(path.read_text(encoding="utf-8"))
                texts.append(
                    {
                        "text_id": doc["text_id"],
                        "title": doc.get("title"),
                        "translation_source": doc.get("translation_source"),
                        "paragraph_count": len(doc.get("paragraphs", [])),
                        "line_count": len(doc.get("lines", [])),
                    }
                )
        catalog = {"corpus": corpus, "count": len(texts), "texts": texts}
        out = ROOT / "data" / f"{corpus}_catalog.json"
        out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
        shutil.copy2(out, WEB_DATA / f"{corpus}_catalog.json")
        print(f"Wrote {out} ({len(texts)} texts)")

    shutil.copy2(ROOT / "data" / "flood_comparison.json", WEB_DATA / "flood_comparison.json")


def copy_web_data() -> None:
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    for name in (
        "loci_chart.json",
        "corpus.json",
        "etcsl_texts.json",
        "english_glossary.json",
        "flood_comparison.json",
        "akkadian_catalog.json",
        "oracc_catalog.json",
    ):
        src = ROOT / "data" / name
        if src.exists():
            shutil.copy2(src, WEB_DATA / name)


def main() -> None:
    run("fetch_etcsl.py")
    run("build_etcsl_index.py")
    run("fetch_oracc.py")
    run("merge_extra_corpus.py")
    run("export_corpus.py")
    export_extra_catalogs()
    run("validate_data.py")
    run("merge_witness_deltas.py")
    run("sync_loci.py")
    copy_web_data()
    print("\nDone — corpus.db ready; push web/data/ and publish release.")


if __name__ == "__main__":
    main()

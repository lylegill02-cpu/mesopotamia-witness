#!/usr/bin/env python3
"""Export lightweight JSON from etcsl.db for static site + loci verification."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "etcsl.db"
CORPUS = ROOT / "data" / "corpus.json"
TEXTS = ROOT / "data" / "etcsl_texts.json"
WEB_DATA = ROOT / "web" / "data"

# Loci ref -> ETCSL text_id (Akkadian-only loci stay on starter excerpts)
LOCI_ETCSL = {
    "Inanna.descent": "c.1.4.1",
    "SKL.antediluvian": "c.2.1.1",
    "Eridu.Genesis": "c.1.7.4",
    "Gilgamesh.XI": "c.1.8.1.4",  # Sumerian Gilgamesh/Enkidu/netherworld (not Akkadian XI)
}


def excerpt(conn: sqlite3.Connection, text_id: str, max_paras: int = 2) -> str:
    rows = conn.execute(
        """SELECT translation FROM paragraphs
           WHERE text_id = ? ORDER BY COALESCE(line_start, 9999), id LIMIT ?""",
        (text_id, max_paras),
    ).fetchall()
    return " ".join(r[0] for r in rows)


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"Missing {DB}. Run: python scripts/build_etcsl_index.py")

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    texts = [
        dict(r)
        for r in conn.execute(
            "SELECT text_id, title, has_translation FROM texts ORDER BY text_id"
        )
    ]

    refs = {}
    for ref, text_id in LOCI_ETCSL.items():
        row = conn.execute(
            "SELECT title FROM texts WHERE text_id = ?", (text_id,)
        ).fetchone()
        if not row:
            continue
        refs[ref] = {
            "ref": ref,
            "text_id": text_id,
            "composition": row["title"],
            "translation": excerpt(conn, text_id),
            "layer": "etcsl",
            "source_note": "ETCSL (Oxford) — CC BY 3.0 UK",
        }

    # Starter rows for Akkadian / debunk loci not in ETCSL
    starter_path = ROOT / "data" / "starter_corpus.json"
    if starter_path.exists():
        starter = json.loads(starter_path.read_text(encoding="utf-8"))
        refs.update(starter.get("refs", {}))

    corpus = {
        "meta": {
            "edition": "mesopotamia-witness-v1-etcsl",
            "source": "ETCSL + starter excerpts",
            "text_count": len(texts),
        },
        "refs": refs,
    }
    CORPUS.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")

    catalog = {
        "source": "ETCSL",
        "count": len(texts),
        "texts": texts,
    }
    TEXTS.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (WEB_DATA / "corpus.json").write_text(
        json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (WEB_DATA / "etcsl_texts.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    conn.close()
    print(f"Wrote {CORPUS} ({len(refs)} loci refs)")
    print(f"Wrote {TEXTS} ({len(texts)} texts)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Export lightweight JSON from corpus.db for static site + loci verification."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "corpus.db"
ETCSL_DB = ROOT / "data" / "etcsl.db"
CORPUS = ROOT / "data" / "corpus.json"
TEXTS = ROOT / "data" / "etcsl_texts.json"
WEB_DATA = ROOT / "web" / "data"

# Loci ref -> text_id in unified index
LOCI_TEXT_IDS = {
    "Inanna.descent": "c.1.4.1",
    "SKL.antediluvian": "c.2.1.1",
    "Eridu.Genesis": "c.1.7.4",
    "Enuma.E1": "akkadian.enuma.elish",
    "Enuma.Tiamat": "akkadian.enuma.elish",
    "Atrahasis.1": "akkadian.atrahasis",
    "Atrahasis.Flood": "akkadian.atrahasis",
    "Gilgamesh.XI": "akkadian.gilgamesh.xi",
    "AMGG.anunna": "oracc.amgg.anunna",
}


def db_path() -> Path:
    if DB.exists():
        return DB
    if ETCSL_DB.exists():
        return ETCSL_DB
    raise SystemExit("Missing corpus.db — run: python scripts/build_all.py")


def excerpt(conn: sqlite3.Connection, text_id: str, max_paras: int = 2) -> str:
    rows = conn.execute(
        """SELECT translation FROM paragraphs
           WHERE text_id = ? ORDER BY COALESCE(ord, line_start, 9999), id LIMIT ?""",
        (text_id, max_paras),
    ).fetchall()
    return " ".join(r[0] for r in rows)


def corpus_label(conn: sqlite3.Connection, text_id: str) -> str:
    row = conn.execute(
        "SELECT corpus FROM texts WHERE text_id = ?", (text_id,)
    ).fetchone()
    return (row[0] if row else None) or ("akkadian" if text_id.startswith("akkadian.") else "etcsl")


def main() -> None:
    path = db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row

    all_texts = [dict(r) for r in conn.execute(
        "SELECT text_id, title, has_translation, COALESCE(corpus,'etcsl') AS corpus FROM texts ORDER BY text_id"
    )]
    etcsl_texts = [t for t in all_texts if t["corpus"] == "etcsl"]

    refs = {}
    for ref, text_id in LOCI_TEXT_IDS.items():
        row = conn.execute(
            "SELECT title FROM texts WHERE text_id = ?", (text_id,)
        ).fetchone()
        if not row:
            continue
        layer = corpus_label(conn, text_id)
        note = (
            "ETCSL (Oxford) — CC BY 3.0 UK"
            if layer == "etcsl"
            else "ORACC AMGG — CC BY-SA 3.0"
            if text_id.startswith("oracc.")
            else "Public-domain English translation — see text reader for source"
        )
        refs[ref] = {
            "ref": ref,
            "text_id": text_id,
            "composition": row["title"],
            "translation": excerpt(conn, text_id),
            "layer": layer,
            "source_note": note,
        }

    starter_path = ROOT / "data" / "starter_corpus.json"
    if starter_path.exists():
        starter = json.loads(starter_path.read_text(encoding="utf-8"))
        for ref, entry in starter.get("refs", {}).items():
            if ref not in refs:
                refs[ref] = entry

    corpus = {
        "meta": {
            "edition": "mesopotamia-witness-v3-oracc",
            "source": "ETCSL + Akkadian PD + ORACC",
            "text_count": len(all_texts),
            "etcsl_count": len(etcsl_texts),
            "akkadian_count": len(all_texts) - len(etcsl_texts),
        },
        "refs": refs,
    }
    CORPUS.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")

    catalog = {"source": "ETCSL", "count": len(etcsl_texts), "texts": etcsl_texts}
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
    print(f"Wrote {TEXTS} ({len(etcsl_texts)} ETCSL texts)")


if __name__ == "__main__":
    main()

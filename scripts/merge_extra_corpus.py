#!/usr/bin/env python3
"""Merge data/akkadian/*.json and data/oracc/*.json into corpus.db."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRS = (ROOT / "data" / "akkadian", ROOT / "data" / "oracc")
DB = ROOT / "data" / "corpus.db"
ETCSL_DB = ROOT / "data" / "etcsl.db"


def normalize_search(s: str) -> str:
    import re
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def load_json_corpus() -> list[dict]:
    out: list[dict] = []
    for directory in DIRS:
        if not directory.exists():
            continue
        paths = sorted(directory.glob("*.json"))
        paths += sorted(directory.glob("*/*.json"))
        for path in paths:
            if path.name.startswith("_") or path.name.endswith("_index.json"):
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("text_id"):
                out.append(data)
    return out


def ensure_schema(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(texts)")}
    if "corpus" not in cols:
        conn.execute("ALTER TABLE texts ADD COLUMN corpus TEXT NOT NULL DEFAULT 'etcsl'")
    conn.execute("UPDATE texts SET corpus = 'etcsl' WHERE corpus IS NULL OR corpus = ''")

    pcols = {row[1] for row in conn.execute("PRAGMA table_info(paragraphs)")}
    if "ord" not in pcols:
        conn.execute("ALTER TABLE paragraphs ADD COLUMN ord INTEGER")
        conn.execute("UPDATE paragraphs SET ord = id WHERE ord IS NULL")
    conn.commit()


def merge(db_path: Path) -> dict[str, int]:
    if not db_path.exists():
        raise SystemExit(f"Missing {db_path}. Run build_etcsl_index.py first.")

    texts = load_json_corpus()
    conn = sqlite3.connect(db_path)
    ensure_schema(conn)

    n_para = n_lines = 0
    for doc in texts:
        text_id = doc["text_id"]
        corpus = doc.get("corpus") or ("akkadian" if text_id.startswith("akkadian.") else "oracc")
        conn.execute("DELETE FROM paragraphs WHERE text_id = ?", (text_id,))
        conn.execute("DELETE FROM lines WHERE text_id = ?", (text_id,))
        conn.execute(
            "INSERT OR REPLACE INTO texts(text_id, title, has_translation, corpus) VALUES (?,?,?,?)",
            (text_id, doc.get("title"), 1 if doc.get("paragraphs") else 0, corpus),
        )
        for ord_i, para in enumerate(doc.get("paragraphs", []), start=1):
            conn.execute(
                """INSERT INTO paragraphs(text_id, para_id, line_range, line_start, ord, translation, translation_norm)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    text_id,
                    para["para_id"],
                    para.get("line_range", ""),
                    para.get("line_start"),
                    para.get("ord", ord_i),
                    para["translation"],
                    normalize_search(para["translation"]),
                ),
            )
            n_para += 1
        for ord_i, line in enumerate(doc.get("lines", []), start=1):
            translit = line.get("transliteration") or line.get("text") or ""
            conn.execute(
                """INSERT INTO lines(text_id, line_id, ord, line_label, transliteration, translit_norm, paragraph_id)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    text_id,
                    line.get("line_id", f"L{ord_i}"),
                    ord_i,
                    line.get("line_label", str(ord_i)),
                    translit,
                    normalize_search(translit),
                    line.get("paragraph_id"),
                ),
            )
            n_lines += 1

    conn.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("extra_corpus_texts", str(len(texts))))
    conn.commit()
    conn.close()
    return {"texts": len(texts), "paragraphs": n_para, "lines": n_lines}


def main() -> None:
    src = ETCSL_DB if ETCSL_DB.exists() else DB
    if DB.exists() and DB != src:
        DB.unlink()
    if not DB.exists() and src.exists():
        import shutil
        shutil.copy2(src, DB)
    stats = merge(DB)
    print(
        f"Merged extra corpus into {DB}: {stats['texts']} texts, "
        f"{stats['paragraphs']} paragraphs, {stats['lines']} lines"
    )


if __name__ == "__main__":
    main()

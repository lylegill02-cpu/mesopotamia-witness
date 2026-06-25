#!/usr/bin/env python3
"""Merge data/akkadian/*.json into the SQLite search index."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AKK_DIR = ROOT / "data" / "akkadian"
DB = ROOT / "data" / "corpus.db"
ETCSL_DB = ROOT / "data" / "etcsl.db"


def normalize_search(s: str) -> str:
    import re
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def load_akkadian_files() -> list[dict]:
    files = sorted(AKK_DIR.glob("*.json"))
    out = []
    for path in files:
        if path.name.startswith("_"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("text_id"):
            out.append(data)
    return out


def ensure_corpus_column(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(texts)")}
    if "corpus" not in cols:
        conn.execute("ALTER TABLE texts ADD COLUMN corpus TEXT NOT NULL DEFAULT 'etcsl'")
        conn.commit()
    conn.execute("UPDATE texts SET corpus = 'etcsl' WHERE corpus IS NULL OR corpus = ''")
    conn.commit()


def merge(db_path: Path) -> dict[str, int]:
    if not db_path.exists():
        raise SystemExit(f"Missing {db_path}. Run build_etcsl_index.py first.")

    texts = load_akkadian_files()
    conn = sqlite3.connect(db_path)
    ensure_corpus_column(conn)

    n_para = 0
    for doc in texts:
        text_id = doc["text_id"]
        conn.execute("DELETE FROM paragraphs WHERE text_id = ?", (text_id,))
        conn.execute("DELETE FROM lines WHERE text_id = ?", (text_id,))
        conn.execute(
            "INSERT OR REPLACE INTO texts(text_id, title, has_translation, corpus) VALUES (?,?,?,?)",
            (text_id, doc.get("title"), 1, "akkadian"),
        )
        for para in doc.get("paragraphs", []):
            conn.execute(
                """INSERT INTO paragraphs(text_id, para_id, line_range, line_start, translation, translation_norm)
                   VALUES (?,?,?,?,?,?)""",
                (
                    text_id,
                    para["para_id"],
                    para.get("line_range", ""),
                    para.get("line_start"),
                    para["translation"],
                    normalize_search(para["translation"]),
                ),
            )
            n_para += 1
    conn.execute(
        "INSERT OR REPLACE INTO meta VALUES (?,?)",
        ("akkadian_texts", str(len(texts))),
    )
    conn.commit()
    conn.close()
    return {"texts": len(texts), "paragraphs": n_para}


def main() -> None:
    src = ETCSL_DB if ETCSL_DB.exists() else DB
    if DB.exists() and DB != src:
        DB.unlink()
    if not DB.exists() and src.exists():
        import shutil
        shutil.copy2(src, DB)
    stats = merge(DB)
    print(f"Merged Akkadian into {DB}: {stats['texts']} texts, {stats['paragraphs']} paragraphs")


if __name__ == "__main__":
    main()

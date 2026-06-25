#!/usr/bin/env python3
"""Build SQLite search index from ETCSL TEI/XML zip."""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.etcsl_parse import (  # noqa: E402
    normalize_search,
    parse_title,
    parse_translit,
    parse_translation,
)

DEFAULT_ZIP = ROOT / "data" / "etcsl.zip"
DEFAULT_DB = ROOT / "data" / "etcsl.db"

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);

CREATE TABLE texts (
  text_id TEXT PRIMARY KEY,
  title TEXT,
  has_translation INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE lines (
  id INTEGER PRIMARY KEY,
  text_id TEXT NOT NULL,
  line_id TEXT NOT NULL,
  ord INTEGER NOT NULL,
  line_label TEXT NOT NULL,
  transliteration TEXT NOT NULL,
  translit_norm TEXT NOT NULL,
  paragraph_id TEXT
);

CREATE TABLE paragraphs (
  id INTEGER PRIMARY KEY,
  text_id TEXT NOT NULL,
  para_id TEXT NOT NULL,
  line_range TEXT,
  line_start INTEGER,
  translation TEXT NOT NULL,
  translation_norm TEXT NOT NULL
);

CREATE INDEX idx_lines_text ON lines(text_id, ord);
CREATE INDEX idx_lines_norm ON lines(translit_norm);
CREATE INDEX idx_paragraphs_text ON paragraphs(text_id, line_start);
CREATE INDEX idx_paragraphs_norm ON paragraphs(translation_norm);
CREATE INDEX idx_texts_title ON texts(title);
"""


def build_index(zip_path: Path, db_path: Path, limit: int | None = None) -> dict[str, int]:
    if not zip_path.exists():
        raise SystemExit(f"Missing {zip_path}. Run: python scripts/fetch_etcsl.py")

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;")
    conn.executescript(SCHEMA)

    n_texts = n_lines = n_paragraphs = 0
    t0 = time.monotonic()

    with zipfile.ZipFile(zip_path) as zf:
        translit_files = sorted(
            n for n in zf.namelist() if n.startswith("etcsl/transliterations/c.") and n.endswith(".xml")
        )
        translation_files = {
            n.rsplit("/", 1)[1].removeprefix("t.").removesuffix(".xml"): n
            for n in zf.namelist()
            if n.startswith("etcsl/translations/t.") and n.endswith(".xml")
        }
        if limit:
            translit_files = translit_files[:limit]

        for member in translit_files:
            text_id = "c." + member.rsplit("/", 1)[1].removeprefix("c.").removesuffix(".xml")
            translit_bytes = zf.read(member)
            title = parse_title(translit_bytes)

            line_rows = []
            for line, _words in parse_translit(translit_bytes, text_id):
                line_rows.append(
                    (
                        text_id,
                        line["line_id"],
                        line["ord"],
                        line["line_label"],
                        line["transliteration"],
                        normalize_search(line["transliteration"]),
                        line["paragraph_id"],
                    )
                )

            stripped = text_id.removeprefix("c.")
            t_member = translation_files.get(stripped)
            para_rows = []
            if t_member:
                for para in parse_translation(zf.read(t_member), text_id):
                    para_rows.append(
                        (
                            text_id,
                            para["para_id"],
                            para["line_range"],
                            para["line_start"],
                            para["translation"],
                            normalize_search(para["translation"]),
                        )
                    )

            conn.execute(
                "INSERT INTO texts(text_id, title, has_translation) VALUES (?,?,?)",
                (text_id, title, int(bool(para_rows))),
            )
            if line_rows:
                conn.executemany(
                    """INSERT INTO lines(text_id, line_id, ord, line_label, transliteration,
                       translit_norm, paragraph_id) VALUES (?,?,?,?,?,?,?)""",
                    line_rows,
                )
            if para_rows:
                conn.executemany(
                    """INSERT INTO paragraphs(text_id, para_id, line_range, line_start, translation,
                       translation_norm) VALUES (?,?,?,?,?,?)""",
                    para_rows,
                )
            n_texts += 1
            n_lines += len(line_rows)
            n_paragraphs += len(para_rows)
            if n_texts % 50 == 0:
                conn.commit()

    conn.commit()
    conn.executemany(
        "INSERT INTO meta VALUES (?,?)",
        [
            ("source", "ETCSL bulk corpus, Oxford Text Archive (CC BY 3.0 UK)"),
            ("citation", "Black, J.A., et al., ETCSL, Oxford 1998-2006"),
            ("texts", str(n_texts)),
            ("lines", str(n_lines)),
            ("paragraphs", str(n_paragraphs)),
            ("built_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
        ],
    )
    conn.commit()
    conn.execute("ANALYZE")
    conn.close()
    print(f"Built in {time.monotonic() - t0:.1f}s")
    return {"texts": n_texts, "lines": n_lines, "paragraphs": n_paragraphs}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ETCSL SQLite index")
    parser.add_argument("--zip", type=Path, default=DEFAULT_ZIP)
    parser.add_argument("--output", type=Path, default=DEFAULT_DB)
    parser.add_argument("--limit", type=int, default=None, help="For testing")
    args = parser.parse_args()

    stats = build_index(args.zip, args.output, limit=args.limit)
    size_mb = args.output.stat().st_size / (1024 * 1024)
    print(
        f"Wrote {args.output} — {stats['texts']} texts, "
        f"{stats['lines']:,} lines, {stats['paragraphs']:,} paragraphs ({size_mb:.1f} MB)"
    )


if __name__ == "__main__":
    main()

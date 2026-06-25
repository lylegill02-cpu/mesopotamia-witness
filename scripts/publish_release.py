#!/usr/bin/env python3
"""Publish etcsl.db as a GitHub Release asset for client-side search."""
from __future__ import annotations

import argparse
import gzip
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "etcsl.db"
DIST = ROOT / "dist"


def gzip_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "rb") as f_in, gzip.open(dest, "wb", compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create GitHub release with ETCSL search index")
    parser.add_argument("tag", help='Release tag, e.g. "v1.0.0-search"')
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not DB.exists():
        raise SystemExit("Missing data/etcsl.db — run: python scripts/build_all.py")

    db_gz = DIST / "etcsl.db.gz"
    gzip_file(DB, db_gz)
    mb = db_gz.stat().st_size / (1024 * 1024)
    print(f"Compressed: {db_gz} ({mb:.1f} MB)")

    if args.dry_run:
        return

    subprocess.run(
        [
            "gh",
            "release",
            "create",
            args.tag,
            "--title",
            f"Mesopotamia Witness {args.tag}",
            "--notes",
            "ETCSL search index (~4 MB download). Used by the static site for English + transliteration search.",
            str(db_gz),
        ],
        check=True,
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()

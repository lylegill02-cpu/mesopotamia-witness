#!/usr/bin/env python3
"""Fetch ETCSL, build search index, export corpus, sync loci."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(name: str) -> None:
    path = SCRIPTS / name
    print(f"\n=== {name} ===")
    subprocess.run([sys.executable, str(path)], check=True, cwd=ROOT)


def main() -> None:
    run("fetch_etcsl.py")
    run("build_etcsl_index.py")
    run("export_corpus.py")
    run("merge_witness_deltas.py")
    run("sync_loci.py")
    print("\nDone. Copy web/data/* or push to deploy.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate loci, corpus JSON, and extra-corpus text files."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCI = ROOT / "data" / "loci.json"
CORPUS = ROOT / "data" / "corpus.json"
EXTRA_DIRS = (ROOT / "data" / "akkadian", ROOT / "data" / "oracc")


def check_loci() -> list[str]:
    errors: list[str] = []
    data = json.loads(LOCI.read_text(encoding="utf-8"))
    ids = set()
    for loc in data.get("loci", []):
        lid = loc.get("id")
        if not lid:
            errors.append("Locus missing id")
            continue
        if lid in ids:
            errors.append(f"Duplicate locus id: {lid}")
        ids.add(lid)
        if loc.get("ref") and not loc.get("text_id") and loc.get("layer") == "primary":
            errors.append(f"Primary locus {lid} has ref but no text_id")
    return errors


def check_extra_json() -> list[str]:
    errors: list[str] = []
    for directory in EXTRA_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            if path.name.startswith("_"):
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            if not doc.get("text_id"):
                errors.append(f"{path.name}: missing text_id")
            if not doc.get("paragraphs") and not doc.get("lines"):
                errors.append(f"{path.name}: no paragraphs or lines")
            for i, para in enumerate(doc.get("paragraphs", [])):
                if not para.get("translation"):
                    errors.append(f"{path.name}: paragraph {i} missing translation")
    return errors


def check_corpus_refs() -> list[str]:
    errors: list[str] = []
    if not CORPUS.exists():
        return ["Missing data/corpus.json — run export_corpus.py"]
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    refs = corpus.get("refs", {})
    for loc in json.loads(LOCI.read_text(encoding="utf-8")).get("loci", []):
        ref = loc.get("ref")
        if ref and ref not in refs:
            errors.append(f"Locus ref not in corpus.json: {ref}")
    return errors


def main() -> None:
    errors = check_loci() + check_extra_json() + check_corpus_refs()
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)
    print("Validation OK")


if __name__ == "__main__":
    main()

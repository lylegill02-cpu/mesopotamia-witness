#!/usr/bin/env python3
"""Verify loci and write enriched chart for the static site."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCI = ROOT / "data" / "loci.json"
CORPUS = ROOT / "data" / "corpus.json"
OUT = ROOT / "data" / "loci_chart.json"


def suppression_score(denial: dict) -> int:
    if not denial:
        return 0
    return int(
        round(
            (
                denial.get("print_historical", 0)
                + denial.get("commentary_residue", 0)
                + denial.get("modern_digital", 0)
                + denial.get("in_build", 0)
            )
            / 4
        )
    )


def verify_ref(ref: str | None, corpus: dict) -> dict:
    if not ref:
        return {"present": False, "snippet": ""}
    refs = corpus.get("refs", {})
    entry = refs.get(ref)
    if not entry:
        return {"present": False, "snippet": ""}
    text = entry.get("translation") or entry.get("transliteration") or ""
    return {"present": True, "snippet": text[:280]}


def main() -> None:
    loci_data = json.loads(LOCI.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8")) if CORPUS.exists() else {"refs": {}}
    verified = 0
    for loc in loci_data.get("loci", []):
        v = verify_ref(loc.get("ref"), corpus)
        loc["verified"] = v
        if v.get("present"):
            verified += 1
        denial = loc.get("denial", {})
        loc["suppression_index"] = suppression_score(denial)
        loc["available_now"] = denial.get("in_build", 3) <= 1
    out = {
        **{k: v for k, v in loci_data.items() if k != "loci"},
        "verified_count": verified,
        "loci": loci_data["loci"],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Verified present: {verified}/{len(out['loci'])}")


if __name__ == "__main__":
    main()

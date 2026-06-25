#!/usr/bin/env python3
"""Fetch ORACC JSON editions into data/corpus.json (best-effort)."""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "corpus.json"

# Starter catalog — expand as ORACC endpoints stabilize
CATALOG = [
    {
        "ref": "AMGG.anunna",
        "composition": "Anunna / Anunnaki (AMGG)",
        "oracc": None,
        "translation": (
            "Scholarly usage: Anunna/Anunnaki names Mesopotamian deities — members of the divine "
            "assembly linked to heaven and the underworld. The term appears in Akkadian ritual and "
            "myth; it is not attested as a Sumerian phrase meaning ‘those who from heaven came.’"
        ),
    },
    {
        "ref": "Enuma.E1",
        "composition": "Enuma Elish — Tablet I (opening)",
        "translation": (
            "When on high the heaven had not been named, firm ground below had not been called by name, "
            "naught but primordial Apsu, their begetter, and Mummu-Tiamat, she who bore them all, "
            "had mixed their waters together — before gods had appeared, any one of them."
        ),
    },
    {
        "ref": "Enuma.Tiamat",
        "composition": "Enuma Elish — Marduk vs Tiamat",
        "translation": (
            "Marduk catches Tiamat in his net; winds distend her belly; he splits her like a shellfish "
            "into two halves — with one half he forms the sky, establishes stations for the great gods."
        ),
    },
    {
        "ref": "Atrahasis.1",
        "composition": "Atrahasis — creation of humanity",
        "translation": (
            "Let the goddess create a mortal man so that he may bear the yoke of the gods… "
            "They slaughtered Aw-ilu in their assembly; Nintu mixed clay with his flesh and blood."
        ),
    },
    {
        "ref": "Atrahasis.Flood",
        "composition": "Atrahasis — flood",
        "translation": (
            "Tear down your house, build a boat; abandon possessions and seek life… "
            "Board the boat and save living things — the flood which the king discussed will come."
        ),
    },
    {
        "ref": "Gilgamesh.XI",
        "composition": "Gilgamesh — Utnapishtim’s flood (Tablet XI)",
        "translation": (
            "I tore down my house, I built a boat… the gods smelled the savor, the gods gathered like flies "
            "over the sacrificer — then Enlil came up to the boat and seized my hand, making me and my wife like gods."
        ),
    },
    {
        "ref": "SKL.antediluvian",
        "composition": "Sumerian King List — antediluvian section",
        "translation": (
            "After kingship descended from heaven, Eridug became the seat of kingship… "
            "Alulim reigned 28,800 years; Alalgar 36,000 years — eight kings reigned 241,200 years, then the flood swept over."
        ),
    },
    {
        "ref": "Eridu.Genesis",
        "composition": "Eridu Genesis (fragmentary)",
        "translation": (
            "[Fragmentary] … kingship descends … cities are built … the gods send a flood … "
            "Responsible editions mark many breaks; continuous ‘full text’ online versions often smooth gaps."
        ),
    },
    {
        "ref": "Inanna.descent",
        "composition": "Descent of Inanna",
        "translation": (
            "From the ‘great above’ she set her mind toward the ‘great below’ — Inanna abandoned heaven, "
            "abandoned earth, and descended to the netherworld; at each gate a garment is removed until she stands naked."
        ),
    },
]


def fetch_oracc_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=25) as resp:
            raw = resp.read().decode("utf-8", "replace")
        raw = re.sub(r"[\x00-\x1f]", " ", raw)
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def extract_translation_from_oracc(data: dict) -> str:
    """Best-effort: ORACC JSON is lemmatized transliteration; full translation often absent."""
    parts: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "line" and node.get("text"):
                parts.append(str(node["text"]))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return " ".join(parts)[:500]


def main() -> None:
    refs = {}
    for item in CATALOG:
        ref = item["ref"]
        translation = item.get("translation", "")
        transliteration = ""
        oracc_url = item.get("oracc")
        if oracc_url:
            data = fetch_oracc_json(oracc_url)
            if data:
                transliteration = extract_translation_from_oracc(data)
        refs[ref] = {
            "ref": ref,
            "composition": item["composition"],
            "translation": translation,
            "transliteration": transliteration,
            "layer": "primary",
            "source_note": "Starter excerpt — replace with ORACC/CDLI edition when wired",
        }
    corpus = {
        "meta": {
            "edition": "mesopotamia-witness-v0",
            "note": "Starter corpus for guided loci; not a full ETCSL mirror yet.",
        },
        "refs": refs,
    }
    OUT.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(refs)} refs)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fetch Standard Babylonian Gilgamesh from eBL API (ORACC ATF) into data/oracc/."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "oracc"
CACHE = OUT / "_cache"

# eBL corpus id: Literary / Epic of Gilgameš / Standard Babylonian
TEXT = ("L", "1", "4")
STAGE = "SB"
TABLETS = {
    "XI": "oracc.ebl.gilgamesh.xi",
}
API = "https://www.ebl.lmu.de/api/texts/{genre}/{cat}/{idx}/chapters/{stage}/{name}/display"
SOURCE = "eBL (Electronic Babylonian Library) — ORACC ATF, CC BY 4.0"
SOURCE_URL = "https://www.ebl.lmu.de/corpus/L/1/4/SB/{tablet}"


def fetch_json(url: str, cache: Path, force: bool = False) -> dict:
    if cache.exists() and not force and cache.stat().st_size > 1000:
        return json.loads(cache.read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": "mesopotamia-witness/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(raw, encoding="utf-8")
    return json.loads(raw)


def content_to_text(parts: list | None) -> str:
    if not parts:
        return ""
    out: list[str] = []
    for item in parts:
        if isinstance(item, str):
            out.append(item)
            continue
        if not isinstance(item, dict):
            continue
        if "value" in item:
            out.append(str(item["value"]))
        elif "content" in item:
            out.append(content_to_text(item["content"]))
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def line_translation(line: dict) -> str:
    chunks = line.get("translation") or []
    texts: list[str] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        prefix = chunk.get("prefix") or ""
        body = content_to_text(chunk.get("content"))
        if prefix.startswith("#tr.en"):
            texts.append(body)
        elif body and not prefix.startswith("#"):
            texts.append(body)
    return re.sub(r"\s+", " ", " ".join(texts)).strip()


def variant_transliteration(variant: dict) -> str:
    """Prefer first manuscript line content as transliteration."""
    best = ""
    for ms in variant.get("manuscripts") or []:
        line = ms.get("line") or {}
        prefix = line.get("prefix") or ""
        body = content_to_text(line.get("content"))
        text = f"{prefix}{body}".strip()
        if len(text) > len(best):
            best = text
    if not best:
        best = content_to_text((variant.get("reconstruction") or []))
    return re.sub(r"\s+", " ", best).strip()


def composite_transliteration(line: dict) -> str:
    parts: list[str] = []
    for variant in line.get("variants") or []:
        t = variant_transliteration(variant)
        if t and t not in parts:
            parts.append(t)
    return " / ".join(parts[:3])


def title_text(raw) -> str:
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        return " ".join(content_to_text([x]) for x in raw if x)
    return "Gilgamesh"


def build_doc(tablet: str, payload: dict) -> dict:
    text_id = TABLETS[tablet]
    lines_out: list[dict] = []
    paras_out: list[dict] = []
    for line in payload.get("lines") or []:
        num = line.get("number") or {}
        if isinstance(num, dict):
            n = num.get("number")
            prime = num.get("hasPrime")
            label = f"XI {n}{'′' if prime else ''}" if tablet == "XI" else f"{tablet} {n}"
        else:
            n = line.get("originalIndex", 0) + 1
            label = f"XI {n}"
        translit = composite_transliteration(line)
        translation = line_translation(line)
        line_id = f"{tablet}.{n}"
        if translit:
            lines_out.append(
                {
                    "line_id": line_id,
                    "line_label": label,
                    "transliteration": translit,
                }
            )
        if translation:
            paras_out.append(
                {
                    "para_id": line_id,
                    "line_range": label,
                    "line_start": n,
                    "ord": n,
                    "translation": translation,
                }
            )

    return {
        "text_id": text_id,
        "corpus": "oracc",
        "title": f"Gilgamesh — Tablet {tablet} (eBL Standard Babylonian)",
        "language": "akkadian",
        "translation_source": SOURCE,
        "source_url": SOURCE_URL.format(tablet=tablet),
        "paragraphs": paras_out,
        "lines": lines_out,
        "meta": {
            "ebl_chapter": f"L/1/4/{STAGE}/{tablet}",
            "display_title": title_text(payload.get("title")),
            "line_count": len(lines_out),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch eBL Gilgamesh SB tablets")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--tablets", default="XI", help="Comma-separated tablet names (default XI)")
    args = parser.parse_args()

    genre, cat, idx = TEXT
    OUT.mkdir(parents=True, exist_ok=True)
    for tablet in [t.strip().upper() for t in args.tablets.split(",") if t.strip()]:
        if tablet not in TABLETS:
            print(f"Skip unknown tablet {tablet}", file=sys.stderr)
            continue
        url = API.format(genre=genre, cat=cat, idx=idx, stage=STAGE, name=tablet)
        cache = CACHE / f"ebl_gilgamesh_{tablet}.json"
        try:
            payload = fetch_json(url, cache, force=args.force)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
            raise SystemExit(f"Fetch failed for tablet {tablet}: {err}") from err
        doc = build_doc(tablet, payload)
        out_path = OUT / f"ebl.gilgamesh.{tablet.lower()}.json"
        out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"Wrote {out_path.name}: {len(doc['lines'])} translit lines, "
            f"{len(doc['paragraphs'])} English lines"
        )


if __name__ == "__main__":
    main()

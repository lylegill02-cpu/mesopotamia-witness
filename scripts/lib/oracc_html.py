"""Parse ORACC HTML pages (AMGG deity entries, ETCSRI royal inscriptions)."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser


def strip_tags(raw: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


class _TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._parts.append(data.strip())

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._parts)).strip()


def cell_text(raw: str) -> str:
    parser = _TextCollector()
    parser.feed(raw)
    return parser.text()


def extract_amgg_entry(html_text: str) -> dict:
    title_m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.I | re.S)
    title = strip_tags(title_m.group(1)) if title_m else "AMGG entry"
    inner_m = re.search(r'<div id="innerContent">(.*?)</div>\s*<div id="Authors">', html_text, re.S)
    body = inner_m.group(1) if inner_m else html_text

    paragraphs: list[dict] = []
    first = re.search(r'<p class="firstpara"[^>]*>(.*?)</p>', body, re.S)
    if first:
        text = strip_tags(first.group(1))
        if text:
            paragraphs.append({"heading": "Overview", "translation": text})

    for block in re.findall(r"<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|<a id=\"h_|<div id=\"Authors\"|$)", body, re.S):
        heading = strip_tags(block[0])
        chunks = re.findall(r"<p[^>]*>(.*?)</p>", block[1], re.S)
        for chunk in chunks:
            text = strip_tags(chunk)
            if len(text) > 40:
                paragraphs.append({"heading": heading, "translation": text})

    if not paragraphs:
        for chunk in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S):
            text = strip_tags(chunk)
            if len(text) > 40:
                paragraphs.append({"heading": "Overview", "translation": text})
                break

    lines: list[dict] = []
    written = re.search(r"Written forms:</dt>\s*<dd[^>]*>(.*?)</dd>\s*<dd[^>]*>(.*?)</dd>", body, re.S)
    if written:
        lines.append(
            {
                "line_id": "forms.sumerian",
                "line_label": "Sumerian",
                "transliteration": strip_tags(written.group(1)),
            }
        )
        lines.append(
            {
                "line_id": "forms.akkadian",
                "line_label": "Akkadian",
                "transliteration": strip_tags(written.group(2)),
            }
        )
    normalized = re.search(r"Normalized forms:</dt>\s*<dd[^>]*>(.*?)</dd>", body, re.S)
    if normalized:
        lines.append(
            {
                "line_id": "forms.normalized",
                "line_label": "Normalized",
                "transliteration": strip_tags(normalized.group(1)),
            }
        )

    return {"title": title, "paragraphs": paragraphs, "lines": lines}


def extract_etcsri_text(html_text: str) -> dict:
    title_m = re.search(r'<h1 class="p3h2 heading[^"]*">(.*?)</h1>', html_text, re.S)
    title = strip_tags(title_m.group(1)) if title_m else "ETCSRI text"
    qid_m = re.search(r'data-item="(Q\d+)"', html_text)
    qid = qid_m.group(1) if qid_m else "unknown"

    lines: list[dict] = []
    translations: dict[str, str] = {}
    for row in re.finditer(r'<tr id="(Q\d+\.\d+)" class="l"[^>]*>(.*?)</tr>', html_text, re.S):
        line_id = row.group(1)
        row_html = row.group(2)
        label_m = re.search(r'<span class="xlabel[^"]*">([^<]+)</span>', row_html)
        line_label = strip_tags(label_m.group(1)) if label_m else line_id.split(".")[-1]
        tlit_m = re.search(r'<td class="tlit">(.*?)</td>', row_html, re.S)
        translit = cell_text(tlit_m.group(1)) if tlit_m else ""
        if translit:
            lines.append(
                {
                    "line_id": line_id,
                    "line_label": line_label,
                    "transliteration": translit,
                }
            )
        trans_m = re.search(r'<td class="t1 xtr"[^>]*>(.*?)</td>', row_html, re.S)
        if trans_m:
            translations[line_id] = strip_tags(trans_m.group(1))

    paragraphs: list[dict] = []
    if translations:
        for line_id, translation in translations.items():
            paragraphs.append(
                {
                    "para_id": line_id,
                    "line_range": line_id.split(".")[-1],
                    "translation": translation,
                }
            )
    elif lines:
        paragraphs.append(
            {
                "para_id": "composite",
                "line_range": f"1–{len(lines)}",
                "translation": " ".join(l["transliteration"] for l in lines[:3]),
            }
        )

    return {"qid": qid, "title": title, "lines": lines, "paragraphs": paragraphs}

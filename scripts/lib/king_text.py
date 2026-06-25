"""Clean and parse L.W. King 1902 Enuma Elish (public domain)."""
from __future__ import annotations

import re

TABLET_RE = re.compile(
    r"THE (FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH) TABLET",
    re.I,
)
ROMAN = {
    "FIRST": "I",
    "SECOND": "II",
    "THIRD": "III",
    "FOURTH": "IV",
    "FIFTH": "V",
    "SIXTH": "VI",
    "SEVENTH": "VII",
}

# Known OCR / typography fixes in King 1902 web copies
CLEANUPS: list[tuple[str, str]] = [
    (r"\bTiamut\b", "Tiamat"),
    (r"\bApru\b", "Apsu"),
    (r"\bthev\b", "they"),
    (r"\bbeboldeth\b", "beholdeth"),
    (r"\bmiahty\b", "mighty"),
    (r"\bbounds\b", "hounds"),
    (r"\bsaving:\b", "saying:"),
    (r"\bsaving\b", "saying"),
    (r"\bcostlv\b", "costly"),
    (r"\bposessed\b", "possessed"),
    (r"\bMardk\b", "Marduk"),
    (r"\bDug-ga\b", "Dugga"),
    (r"\bdeerees\b", "decrees"),
    (r"\bAnn drew\b", "Anu drew"),
    (r"\.\s*\.", "."),
    (r"\s+", " "),
]

STOP_MARKERS = (
    "END OF THE CREATION EPIC",
    "THE FIGHT WITH TIAMAT",
    "EPILOGUE",
)


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    for pattern, repl in CLEANUPS:
        text = re.sub(pattern, repl, text)
    return text


def split_sentences(text: str) -> list[str]:
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'(])', text)
    return [p.strip() for p in parts if p.strip()]


def chunk_sentences(sentences: list[str], max_len: int = 700) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    n = 0
    for sent in sentences:
        candidate = " ".join(buf + [sent])
        if buf and len(candidate) > max_len:
            n += 1
            chunks.append(" ".join(buf))
            buf = [sent]
        else:
            buf.append(sent)
    if buf:
        chunks.append(" ".join(buf))
    return chunks


def parse_king_raw(raw: str) -> list[dict]:
    idx = raw.find("THE FIRST TABLET")
    if idx > 0:
        raw = raw[idx:]
    for stop in STOP_MARKERS:
        pos = raw.find(stop)
        if pos > 0:
            raw = raw[:pos]

    markers = list(TABLET_RE.finditer(raw))
    paragraphs: list[dict] = []
    global_ord = 0

    for i, m in enumerate(markers):
        name = m.group(1).upper()
        tablet = ROMAN[name]
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(raw)
        body = clean_text(raw[start:end])
        if not body:
            continue
        chunks = chunk_sentences(split_sentences(body))
        for n, chunk in enumerate(chunks, start=1):
            global_ord += 1
            paragraphs.append(
                {
                    "para_id": f"{tablet}.{n}",
                    "line_range": f"Tablet {tablet} §{n}",
                    "ord": global_ord,
                    "translation": chunk,
                }
            )
    return paragraphs


# Standard Babylonian transliteration samples (search hooks; George SB recension)
ENUMa_LINES = [
    {"line_id": "I.1", "line_label": "I 1", "transliteration": "e-nu-ma e-liš la na-bu-ú šá-ma-mu"},
    {"line_id": "I.2", "line_label": "I 2", "transliteration": "šap-liš am-ma-tum šu-ma la zak-rat"},
    {"line_id": "I.3", "line_label": "I 3", "transliteration": "Apsû-ma ris-tu-ú za-ru-šu-un"},
    {"line_id": "I.4", "line_label": "I 4", "transliteration": "mu-um-mu Ti-amat mu-na-ad-da-at"},
    {"line_id": "IV.1", "line_label": "IV 1", "transliteration": "lu-u šu-ut KUR DINGIR.DINGIR"},
    {"line_id": "IV.2", "line_label": "IV 4", "transliteration": "iš-pu-uh-ma šá-bi-iṣ i-na riš-ti-ša"},
    {"line_id": "IV.3", "line_label": "IV 5", "transliteration": "uš-pil-šá-ma ka-la-baš i-na-ab-bi-it"},
    {"line_id": "VI.1", "line_label": "VI 39", "transliteration": "600 DINGIR.DINGIR a-nun-na-ku"},
]

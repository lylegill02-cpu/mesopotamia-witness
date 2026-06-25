"""Parse ETCSL TEI/XML transliterations and translations."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET

ETCSL_ENTITIES: dict[str, str] = {
    "c": "š",
    "C": "Š",
    "g": "ŋ",
    "G": "Ŋ",
    "h": "ḫ",
    "H": "Ḫ",
    "s": "š",
    "s1": "s₁",
    "s2": "ś",
    "s3": "ṣ",
    "t": "ṭ",
    "aleph": "ʾ",
    "d": "{d}",
    "dug": "{dug}",
    "f": "{f}",
    "gi": "{gi}",
    "id2": "{id₂}",
    "im": "{im}",
    "jic": "{ŋeš}",
    "ki": "{ki}",
    "ku6": "{ku₆}",
    "kuc": "{kuš}",
    "lu2": "{lu₂}",
    "m": "{m}",
    "mu": "{mu}",
    "mucen": "{mušen}",
    "mul": "{mul}",
    "zabar": "{zabar}",
    "na4": "{na₄}",
    "sar": "{sar}",
    "tug2": "{tug₂}",
    "u2": "{u₂}",
    "udu": "{udu}",
    "urud": "{urud}",
    "uzu": "{uzu}",
    "ance": "{anše}",
    "cah2": "{šaḫ₂}",
    "e2": "{e₂}",
    "gud": "{gud}",
    "iku": "{iku}",
    "kac": "{kaš}",
    "kur": "{kur}",
    "ninda": "{ninda}",
    "sa": "{sa}",
    "tum9": "{tum₉}",
    "damb": "⸢",
    "dame": "⸣",
    "suppb": "⟨",
    "suppe": "⟩",
    "times": "×",
    "commat": "@",
    "plus": "+",
    "sect": "§",
    "X": "X",
    "amacr": "ā",
    "Amacr": "Ā",
    "emacr": "ē",
    "Emacr": "Ē",
    "imacr": "ī",
    "Imacr": "Ī",
    "omacr": "ō",
    "Omacr": "Ō",
    "umacr": "ū",
    "Umacr": "Ū",
    "euml": "ë",
    "iuml": "ï",
    "Iuml": "Ï",
    "aacute": "á",
    "eacute": "é",
    "iacute": "í",
    "oacute": "ó",
    "uacute": "ú",
    "Aacute": "Á",
    "Eacute": "É",
    "Iacute": "Í",
    "Oacute": "Ó",
    "Uacute": "Ú",
    "ouml": "ö",
    "auml": "ä",
    "uuml": "ü",
    "Ouml": "Ö",
    "Auml": "Ä",
    "Uuml": "Ü",
    "ccedil": "ç",
    "Ccedil": "Ç",
    "ntilde": "ñ",
    "Ntilde": "Ñ",
    "agrave": "à",
    "egrave": "è",
    "igrave": "ì",
    "ograve": "ò",
    "ugrave": "ù",
    "acirc": "â",
    "ecirc": "ê",
    "icirc": "î",
    "ocirc": "ô",
    "ucirc": "û",
    "szlig": "ß",
    "amp": "&",
    "lt": "<",
    "gt": ">",
    "quot": '"',
    "apos": "'",
    "nbsp": " ",
}

_ENTITY_RE = re.compile(r"&([A-Za-z][A-Za-z0-9_]*);")
_DIGIT_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_ASCII_SUMERIAN = str.maketrans({"j": "ŋ", "J": "Ŋ", "c": "š", "C": "Š"})
_SUBSCRIPT_RE = re.compile(r"(?<=[A-Za-zŋŠšḫṣṭŊḪṢṬ])(\d+)")
_LINE_ID_RE = re.compile(r"^c\d+(?:\.([A-Z]))?\.(\d+)$")


def expand_entities(xml_text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return ETCSL_ENTITIES.get(m.group(1), "")
    return _ENTITY_RE.sub(repl, xml_text)


def normalize_translit(s: str | None) -> str | None:
    if s is None:
        return None
    s = s.translate(_ASCII_SUMERIAN)
    s = _SUBSCRIPT_RE.sub(lambda m: m.group(1).translate(_DIGIT_SUB), s)
    return s


def normalize_search(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def strip_text(elem: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(elem.itertext())).strip()


def line_label(line_id: str, n_attr: str) -> str:
    m = _LINE_ID_RE.match(line_id or "")
    if not m:
        return n_attr or "?"
    section, num = m.groups()
    return f"{section}.{num}" if section else num


def parse_title(xml_bytes: bytes) -> str | None:
    expanded = expand_entities(xml_bytes.decode("utf-8", errors="replace"))
    try:
        root = ET.fromstring(expanded)
    except ET.ParseError:
        return None
    title_el = root.find(".//titleStmt/title")
    if title_el is None:
        return None
    return html.unescape(strip_text(title_el)) or None


def parse_translit(xml_bytes: bytes, text_id: str):
    expanded = expand_entities(xml_bytes.decode("utf-8", errors="replace"))
    try:
        root = ET.fromstring(expanded)
    except ET.ParseError:
        return
    body = root.find(".//body")
    if body is None:
        return
    ord_counter = 0
    for line_el in body.iter("l"):
        line_id = line_el.get("id", "")
        if not line_id:
            continue
        words = []
        for pos, w in enumerate(line_el.iter("w")):
            form = normalize_translit(w.get("form"))
            if not form:
                continue
            words.append(
                {
                    "text_id": text_id,
                    "line_id": line_id,
                    "word_pos": pos,
                    "form": form,
                    "lemma": normalize_translit(w.get("lemma")),
                    "label": w.get("label"),
                }
            )
        translit = " ".join(w["form"] for w in words)
        if not translit:
            continue
        ord_counter += 1
        yield (
            {
                "text_id": text_id,
                "line_id": line_id,
                "ord": ord_counter,
                "line_label": line_label(line_id, line_el.get("n", "")),
                "transliteration": translit,
                "paragraph_id": line_el.get("corresp"),
            },
            words,
        )


def parse_translation(xml_bytes: bytes, text_id: str):
    expanded = expand_entities(xml_bytes.decode("utf-8", errors="replace"))
    try:
        root = ET.fromstring(expanded)
    except ET.ParseError:
        return
    body = root.find(".//body")
    if body is None:
        return
    for p in body.iter("p"):
        para_id = p.get("id")
        if not para_id:
            continue
        line_range = p.get("n", "")
        line_start = None
        if line_range:
            m = re.match(r"^(\d+)", line_range)
            if m:
                line_start = int(m.group(1))
        text = html.unescape(strip_text(p))
        if text:
            yield {
                "text_id": text_id,
                "para_id": para_id,
                "line_range": line_range,
                "line_start": line_start,
                "translation": text,
            }

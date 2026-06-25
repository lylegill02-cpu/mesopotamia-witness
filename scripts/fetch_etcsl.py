#!/usr/bin/env python3
"""Download ETCSL bulk zip from Oxford Text Archive (CC BY 3.0 UK)."""
from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ZIP = ROOT / "data" / "etcsl.zip"
ETCSL_ZIP_URL = (
    "https://ota.bodleian.ox.ac.uk/repository/xmlui/bitstream/handle/"
    "20.500.12024/2518/etcsl.zip?sequence=11&isAllowed=y"
)


def fetch(dest: Path = DEFAULT_ZIP, force: bool = False) -> Path:
    if dest.exists() and dest.stat().st_size > 1_000_000 and not force:
        print(f"Using existing {dest} ({dest.stat().st_size / 1024 / 1024:.1f} MB)")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading ETCSL from Oxford OTA…")
    req = urllib.request.Request(ETCSL_ZIP_URL, headers={"User-Agent": "mesopotamia-witness/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as out:
        while chunk := resp.read(256 * 1024):
            out.write(chunk)
    print(f"Wrote {dest} ({dest.stat().st_size / 1024 / 1024:.1f} MB)")
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="Download ETCSL bulk zip")
    parser.add_argument("--output", type=Path, default=DEFAULT_ZIP)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    fetch(args.output, force=args.force)


if __name__ == "__main__":
    main()

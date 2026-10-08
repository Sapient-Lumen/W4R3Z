#!/usr/bin/env python3
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = ROOT / "docs" / "adr"
INDEX = ADR_DIR / "INDEX.md"
STATUS_RE = re.compile(r"^Status:\s*(\w+)\s*$", re.MULTILINE)
DATE_RE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
VALID_STATUS = {"proposed", "accepted", "superseded", "retired"}


def fail(msg: str) -> None:
    print(f"adr: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not ADR_DIR.exists():
        fail(f"missing dir: {ADR_DIR}")
    if not INDEX.exists():
        fail(f"missing index: {INDEX}")

    adrs = sorted(p for p in ADR_DIR.glob("ADR-*.md") if p.is_file())
    if not adrs:
        fail("no ADR files")

    index_text = INDEX.read_text(encoding="utf-8")

    for adr in adrs:
        if adr.name not in index_text:
            fail(f"index missing entry for {adr.name}")

        text = adr.read_text(encoding="utf-8")
        status_match = STATUS_RE.search(text)
        if not status_match:
            fail(f"missing Status in {adr.name}")
        status = status_match.group(1).lower()
        if status not in VALID_STATUS:
            fail(f"invalid status in {adr.name}: {status}")

        if not DATE_RE.search(text):
            fail(f"missing Date in {adr.name}")

    listed = set(re.findall(r"ADR-\d{4}-[\w-]+\.md", index_text))
    actual = {p.name for p in adrs}
    missing_files = listed - actual
    if missing_files:
        fail(f"index references missing files: {sorted(missing_files)}")

    print(f"adr: ok ({len(adrs)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

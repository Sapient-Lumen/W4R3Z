#!/usr/bin/env python3

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "INDEX.md"
PROPOSALS_DIR = ROOT / "proposals"
ENTRIES_DIR = ROOT / "entries"

REQUIRED_KEYS = ["id", "title", "status", "domains", "last_reviewed", "evidence"]

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def parse_front_matter(text: str, path: Path) -> dict:
    # Very small YAML-ish parser: only supports "key: value" and "key:" with "- item" lists.
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing front matter starting '---'")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        # handle alternative end marker
        m = re.search(r"^---\s*$", text, flags=re.M)
        # if only one marker, fail
        raise ValueError(f"{path}: front matter must end with a line containing '---'")
    fm = parts[0].splitlines()[1:]
    data = {}
    key = None
    for line in fm:
        if not line.strip():
            continue
        if re.match(r"^\s+-\s+", line) and key:
            data.setdefault(key, []).append(line.split("-",1)[1].strip())
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            # simple list
            inner = val[1:-1].strip()
            data[key] = [x.strip() for x in inner.split(",") if x.strip()]
        elif val == "":
            data[key] = []
        else:
            data[key] = val
    return data

def main() -> int:
    errors = []

    # proposals
    ids = {}
    proposal_files = sorted(PROPOSALS_DIR.glob("*.md"))
    if not proposal_files:
        errors.append("No proposal files found.")
    for p in proposal_files:
        text = read_text(p)
        try:
            fm = parse_front_matter(text, p)
        except Exception as e:
            errors.append(str(e))
            continue

        for k in REQUIRED_KEYS:
            if k not in fm or (isinstance(fm[k], list) and len(fm[k]) == 0) or (isinstance(fm[k], str) and not fm[k].strip()):
                errors.append(f"{p}: missing or empty '{k}'")
        pid = fm.get("id")
        if pid:
            if pid in ids:
                errors.append(f"Duplicate proposal id {pid}: {p} and {ids[pid]}")
            ids[pid] = p

        evidence = fm.get("evidence", [])
        if isinstance(evidence, list) and len(evidence) < 2:
            errors.append(f"{p}: evidence must include at least 2 links (prefer 3+)")

    # entries
    entry_files = sorted(ENTRIES_DIR.glob("*.md"))
    # INDEX completeness
    index_text = read_text(INDEX)
    for p in proposal_files:
        rel = f"proposals/{p.name}"
        if rel not in index_text:
            errors.append(f"INDEX.md missing proposal link: {rel}")
    for e in entry_files:
        rel = f"entries/{e.name}"
        if rel not in index_text:
            errors.append(f"INDEX.md missing entry link: {rel}")

    if errors:
        print("Archive validation FAILED:\n", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("Archive validation OK.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

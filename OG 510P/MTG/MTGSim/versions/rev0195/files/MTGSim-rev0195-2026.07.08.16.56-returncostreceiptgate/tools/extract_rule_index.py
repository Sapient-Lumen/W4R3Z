#!/usr/bin/env python3
"""Extract a metadata-only rule index from a local Comprehensive Rules TXT file.

Input is a privately fetched official TXT file. Output contains rule identifiers and
hashes of local paragraphs, not redistributed rule text. The hashes make future rule
updates auditable without storing Wizards IP in the repo/datacube.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import time
from typing import Any

# Reports should use the project/user timezone for readable revision artifacts.
os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

RULE_START = re.compile(r"^(?P<id>\d{3}(?:\.\d+[a-z]?)?)\.\s+(?P<body>.*)$")
GLOSSARY_START = re.compile(r"^Glossary\s*$", re.IGNORECASE)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_rules(text: str) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    current_id: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_lines
        if current_id is None:
            return
        body = "\n".join(current_lines).strip()
        rules.append({
            "rule_id": current_id,
            "paragraph_sha256": sha256_text(body),
            "bytes_utf8": len(body.encode("utf-8")),
            "lines": len(current_lines),
        })
        current_id = None
        current_lines = []

    for line in text.splitlines():
        match = RULE_START.match(line.strip())
        if match:
            flush()
            current_id = match.group("id")
            current_lines = [match.group("body")]
        elif current_id is not None:
            current_lines.append(line)
    flush()
    return rules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("txt", type=pathlib.Path, help="Local official Comprehensive Rules TXT file")
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()

    text = args.txt.read_text(encoding="utf-8", errors="replace")
    report = {
        "schema": "mtgsim.rule_index.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_file": str(args.txt),
        "source_sha256": sha256_text(text),
        "rules": extract_rules(text),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"extracted {len(report['rules'])} rule paragraphs -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Small shared I/O harness for deterministic generated benchmark artifacts.

Scientific calculations, acceptance criteria, and interpretation remain local
to each benchmark.  This module only centralizes the repeated write/check/CLI
mechanics so generated JSON and Markdown cannot drift through copy-paste edits.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def parse_write_check_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write generated artifacts (default)")
    mode.add_argument("--check", action="store_true", help="verify generated artifacts and acceptance checks")
    return parser.parse_args()


def canonical_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n"


def generated_texts(
    output_json: str,
    output_markdown: str,
    result: Mapping[str, Any],
    markdown: str,
) -> dict[str, str]:
    return {
        output_json: canonical_json(result),
        output_markdown: markdown,
    }


def write_generated_texts(root: Path, texts: Mapping[str, str]) -> None:
    for relative_path, text in texts.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def check_generated_texts(
    root: Path,
    texts: Mapping[str, str],
    initial_failures: Iterable[str] = (),
) -> list[str]:
    failures = list(initial_failures)
    for relative_path, expected_text in texts.items():
        path = root / relative_path
        if not path.exists():
            failures.append(f"missing generated artifact: {relative_path}")
        elif path.read_text() != expected_text:
            failures.append(f"stale generated artifact: {relative_path}")
    return failures

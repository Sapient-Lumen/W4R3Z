#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable


def cell(value: object) -> str:
    """Markdown-table cell escaping used by generated metadata reader surfaces."""
    text = "" if value is None else str(value)
    return text.replace("|", "\\|") or "—"


def sorted_counts(counter: Counter) -> dict:
    return {k: v for k, v in sorted(counter.items())}


def append_count_table(lines: list[str], title: str, rows: dict, key_header: str, value_header: str = "Count") -> None:
    lines.extend(["", title, "", f"| {key_header} | {value_header} |", "| --- | ---: |"])
    for key, value in rows.items():
        lines.append(f"| `{key}` | {value} |")


def write_json_and_markdown(generated_dir: Path, stem: str, data: dict, markdown: str) -> None:
    generated_dir.mkdir(exist_ok=True)
    (generated_dir / f"{stem}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (generated_dir / f"{stem}.md").write_text(markdown, encoding="utf-8")


def count_many(rows: Iterable[Iterable[object]]) -> Counter:
    counter: Counter = Counter()
    for row in rows:
        counter.update(row)
    return counter

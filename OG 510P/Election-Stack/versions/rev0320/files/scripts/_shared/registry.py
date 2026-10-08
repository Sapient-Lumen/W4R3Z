"""scripts/_shared/registry.py

Tiny helpers for CSV registries.

Why this exists:
- Several drift-firewall scripts validate CSV "registries".
- Copy/paste parsing code is a common source of inconsistency.

Policy:
- stdlib-only
- keep semantics explicit (no magic inference)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CSVTable:
    path: Path
    headers: list[str]
    rows: list[dict[str, str]]


def read_csv(path: Path) -> CSVTable:
    """Read a CSV registry as trimmed strings."""

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no headers")
        headers = [h.strip() for h in reader.fieldnames]
        rows: list[dict[str, str]] = []
        for r in reader:
            rows.append({k: (v or "").strip() for k, v in r.items()})
        return CSVTable(path=path, headers=headers, rows=rows)


def require_headers(table: CSVTable, required: set[str]) -> list[str]:
    """Return missing required headers (empty list means OK)."""

    present = set(table.headers)
    return sorted(required - present)


def split_semicolon(cell: str) -> list[str]:
    """Split a semicolon-separated list cell."""

    if not cell:
        return []
    return [p.strip() for p in cell.split(";") if p.strip()]

"""Helpers for voter-facing public-answer surface registry lookups."""

from __future__ import annotations

from pathlib import Path

from _shared.registry import read_csv, require_headers, split_semicolon

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "artifacts" / "tables" / "voter-facing-public-answer-surfaces.csv"


def load_surface_registry():
    table = read_csv(REG)
    required = {
        "doc_id",
        "doc_path",
        "template_path",
        "checklist_path",
        "control_tags",
    }
    missing = require_headers(table, required)
    if missing:
        raise ValueError(f"missing required registry headers: {missing}")
    return table


def surface_doc_ids(table) -> set[int]:
    out: set[int] = set()
    for row in table.rows:
        if not any(row.values()):
            continue
        try:
            out.add(int(row["doc_id"]))
        except ValueError as exc:
            raise ValueError(f"invalid doc_id in {table.path}: {row['doc_id']!r}") from exc
    return out


def tagged_surface_doc_ids(table, tag: str) -> set[int]:
    out: set[int] = set()
    for row in table.rows:
        if tag in split_semicolon(row.get("control_tags", "")):
            try:
                out.add(int(row["doc_id"]))
            except ValueError as exc:
                raise ValueError(f"invalid doc_id in {table.path}: {row['doc_id']!r}") from exc
    return out


def compact_doc_id_ranges(doc_ids: set[int]) -> list[str]:
    if not doc_ids:
        return []
    ordered = sorted(doc_ids)
    ranges: list[str] = []
    start = prev = ordered[0]
    for n in ordered[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append(f"{start}–{prev}" if start != prev else str(start))
        start = prev = n
    ranges.append(f"{start}–{prev}" if start != prev else str(start))
    return ranges

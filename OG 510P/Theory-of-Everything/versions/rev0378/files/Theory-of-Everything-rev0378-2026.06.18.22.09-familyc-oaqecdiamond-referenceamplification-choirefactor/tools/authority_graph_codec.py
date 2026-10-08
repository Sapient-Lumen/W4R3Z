#!/usr/bin/env python3
"""Compact, deterministic serializer for the authority dependency graph.

The logical graph is still the expanded list of edge rows used by archive lint
and generated summaries. The stored representation is columnar dictionary JSON
so the release does not carry a 27 MB pretty-printed audit artifact.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import copy
import hashlib
import json

COMPACT_REPRESENTATION = "columnar-dictionary-v1"
EDGE_FIELDS = [
    "edge_id",
    "source_kind",
    "source_id",
    "dependent_kind",
    "dependent_id",
    "dependency_kind",
    "required_for",
    "failure_effect",
    "max_credit_transmitted",
]
VALUE_FIELDS = [field for field in EDGE_FIELDS if field != "edge_id"]
COMPACT_KEYS = {
    "representation",
    "edge_row_fields",
    "edge_ids",
    "dictionaries",
    "columns",
    "row_count",
    "expanded_sha256",
}


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def expanded_graph_sha256(graph: dict[str, Any]) -> str:
    """Digest the logical expanded graph, independent of stored formatting."""
    expanded = expand_authority_graph(graph)
    return hashlib.sha256(_canonical_bytes(expanded)).hexdigest()


def expand_authority_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Return a graph with `edge_rows`, accepting expanded or compact input."""
    if isinstance(graph.get("edge_rows"), list):
        # Expanded authority graphs are tens of megabytes when materialized.
        # Lint/package replay treats expanded inputs as read-only, so avoid a
        # deep copy on the hot path and only normalize edge_count / compact keys.
        out = {key: value for key, value in graph.items() if key not in COMPACT_KEYS}
        out["edge_count"] = len(out["edge_rows"])
        return out

    if graph.get("representation") != COMPACT_REPRESENTATION:
        raise ValueError("authority graph is neither expanded nor columnar-dictionary-v1 compact JSON")

    fields = graph.get("edge_row_fields")
    if fields != VALUE_FIELDS:
        raise ValueError(f"unexpected authority graph compact field order: {fields!r}")
    edge_ids = graph.get("edge_ids")
    dictionaries = graph.get("dictionaries")
    columns = graph.get("columns")
    row_count = graph.get("row_count", graph.get("edge_count"))
    if not isinstance(edge_ids, list) or not isinstance(dictionaries, dict) or not isinstance(columns, dict):
        raise ValueError("malformed authority graph compact payload")
    if len(edge_ids) != row_count:
        raise ValueError("authority graph edge_ids length does not match row_count")

    rows: list[dict[str, str]] = []
    for field in VALUE_FIELDS:
        if field not in dictionaries or field not in columns:
            raise ValueError(f"authority graph compact payload is missing {field!r}")
        if len(columns[field]) != row_count:
            raise ValueError(f"authority graph column {field!r} length does not match row_count")

    for idx, edge_id in enumerate(edge_ids):
        row: dict[str, str] = {"edge_id": edge_id}
        for field in VALUE_FIELDS:
            dictionary = dictionaries[field]
            code = columns[field][idx]
            try:
                row[field] = dictionary[code]
            except (IndexError, TypeError) as exc:
                raise ValueError(f"authority graph column {field!r} has invalid dictionary code at row {idx}") from exc
        rows.append(row)

    out = {key: copy.deepcopy(value) for key, value in graph.items() if key not in COMPACT_KEYS}
    out["edge_rows"] = rows
    out["edge_count"] = len(rows)
    return out


def compact_authority_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Return the deterministic compact JSON representation of a graph."""
    expanded = expand_authority_graph(graph)
    rows = expanded.get("edge_rows", [])
    if not isinstance(rows, list):
        raise ValueError("expanded authority graph has no edge_rows list")

    edge_ids: list[str] = []
    dictionaries: dict[str, list[str]] = {field: [] for field in VALUE_FIELDS}
    dictionary_indexes: dict[str, dict[str, int]] = {field: {} for field in VALUE_FIELDS}
    columns: dict[str, list[int]] = {field: [] for field in VALUE_FIELDS}

    for idx, row in enumerate(rows):
        missing = [field for field in EDGE_FIELDS if field not in row]
        if missing:
            raise ValueError(f"authority graph row {idx} missing fields: {', '.join(missing)}")
        edge_ids.append(str(row["edge_id"]))
        for field in VALUE_FIELDS:
            value = str(row.get(field, ""))
            mapping = dictionary_indexes[field]
            if value not in mapping:
                mapping[value] = len(dictionaries[field])
                dictionaries[field].append(value)
            columns[field].append(mapping[value])

    out = {key: copy.deepcopy(value) for key, value in expanded.items() if key not in {"edge_rows", *COMPACT_KEYS}}
    out["representation"] = COMPACT_REPRESENTATION
    out["edge_count"] = len(rows)
    out["row_count"] = len(rows)
    out["edge_row_fields"] = VALUE_FIELDS
    out["edge_ids"] = edge_ids
    out["dictionaries"] = dictionaries
    out["columns"] = columns
    out["expanded_sha256"] = expanded_graph_sha256(expanded)
    return out


def load_authority_graph(path: str | Path) -> dict[str, Any]:
    return expand_authority_graph(json.loads(Path(path).read_text()))


def load_authority_graph_stored(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def write_authority_graph(path: str | Path, graph: dict[str, Any], *, compact: bool = True) -> None:
    payload = compact_authority_graph(graph) if compact else expand_authority_graph(graph)
    text = json.dumps(payload, ensure_ascii=False, sort_keys=False, separators=(",", ":"))
    Path(path).write_text(text + "\n")


def edge_rows_from_authority_graph(graph: dict[str, Any]) -> list[dict[str, str]]:
    return expand_authority_graph(graph)["edge_rows"]

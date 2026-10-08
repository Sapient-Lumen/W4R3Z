#!/usr/bin/env python3
"""Shared source-role event helpers for lint, freshness replay, and negative tests.

This module is intentionally small.  It is not a registry of scientific routes;
it only centralizes the event-shape vocabulary and row-local checks that were
otherwise duplicated across the executable guards added in rev0346-rev0351.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Iterator

SOURCE_ROLE_VALUES: set[str] = {
    "acquired_support",
    "denominator_pressure",
    "forecast_runway",
    "operational_status",
    "metadata_wrapper",
}
SOURCE_REF_DISPOSITIONS: set[str] = {
    "excluded_from_acquired_source_refs",
    "forbidden_on_metadata_wrapper",
    "retained_as_acquired_support",
    "retained_as_forecast_runway",
    "retained_as_operational_status",
    "retained_on_denominator_row_only",
    "historical_source_role_normalization",
    "route_local_handoff_only",
}
RETAINED_SOURCE_REF_DISPOSITIONS: set[str] = {
    "retained_as_acquired_support",
    "retained_as_forecast_runway",
    "retained_as_operational_status",
    "retained_on_denominator_row_only",
}
SOURCE_CUSTODY_ROLES: set[str] = {
    "denominator_pressure",
    "forecast_runway",
    "operational_status",
    "metadata_wrapper",
}
CREDIT_CAP_VALUES: set[str] = {"S0", "S1", "S2", "S3", "S4", "S5", "no-new-credit"}
CREDIT_CAP_SCOPE_VALUES: set[str] = {
    "source_role_event_no_new_route_credit",
    "freshness_event_no_incremental_route_credit",
}
REV_NOTE_KEY_RE = re.compile(r"^rev\d{4}_.*note$")


def is_metadata_wrapper_row_id(row_id: Any) -> bool:
    return "METADATA-PROVENANCE-WRAPPER" in str(row_id)


def row_id_for_event_row(row: dict[str, Any]) -> str:
    for key, value in row.items():
        if (key.endswith("_id") or key == "route_id") and isinstance(value, str):
            return value
    return "<row>"


def iter_source_role_events(row: dict[str, Any]) -> Iterable[dict[str, Any]]:
    events = row.get("source_role_events", [])
    if not isinstance(events, list):
        return []
    return (event for event in events if isinstance(event, dict))


def collect_source_role_event_refs(
    row: dict[str, Any],
    *,
    disposition: str | None = None,
    role: str | None = None,
) -> set[str]:
    refs: set[str] = set()
    for event in iter_source_role_events(row):
        if disposition is not None and event.get("source_ref_disposition") != disposition:
            continue
        if role is not None and event.get("source_role") != role:
            continue
        refs.update(event.get("source_refs", []) or [])
    return refs


def covered_source_role_event_refs(
    row: dict[str, Any],
    target_refs: set[str],
    *,
    source_role: str,
    dispositions: set[str],
    credit_cap: str = "",
) -> tuple[set[str], list[str], bool]:
    """Return target refs covered by matching events plus cap failures.

    The boolean is true when at least one matching event overlapped the target
    set.  Callers still compare the returned refs with their required ref set.
    """
    events = row.get("source_role_events", [])
    if not isinstance(events, list):
        return set(), ["source_role_events is not a list"], False
    covered: set[str] = set()
    cap_failures: list[str] = []
    matched_event = False
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("source_role") != source_role:
            continue
        if event.get("source_ref_disposition") not in dispositions:
            continue
        overlap = set(event.get("source_refs", []) or []) & target_refs
        if not overlap:
            continue
        matched_event = True
        covered.update(overlap)
        if credit_cap and event.get("credit_cap") != credit_cap:
            cap_failures.append(f"{event.get('event_id', '<event>')} credit_cap `{event.get('credit_cap')}` != `{credit_cap}`")
    return covered, cap_failures, matched_event


def walk_rev_note_keys(obj: Any, trail: tuple[str, ...] = ()) -> list[str]:
    failures: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if REV_NOTE_KEY_RE.match(str(key)):
                failures.append(".".join(trail + (str(key),)))
            failures.extend(walk_rev_note_keys(value, trail + (str(key),)))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            failures.extend(walk_rev_note_keys(value, trail + (str(idx),)))
    return failures



def iter_source_role_event_rows(root: Path) -> Iterator[tuple[str, str, str, dict[str, Any], dict[str, Any]]]:
    """Yield ``(ledger_file, collection, row_id, row, event)`` for row-level events.

    This helper is intentionally structural: it discovers rows already carrying
    ``source_role_events`` without becoming a source or route registry.
    """
    for ledger_path in sorted(root.glob("*.json")):
        try:
            data = json.loads(ledger_path.read_text())
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        top_events = data.get("source_role_events")
        if isinstance(top_events, list):
            top_row = {"ledger_id": ledger_path.stem, "source_role_events": top_events, "source_refs": data.get("source_refs", []) or []}
            for event in top_events:
                if isinstance(event, dict):
                    yield ledger_path.name, "<top-level>", ledger_path.stem, top_row, event
        for collection, rows in data.items():
            if collection == "source_role_events":
                continue
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                events = row.get("source_role_events")
                if not isinstance(events, list):
                    continue
                row_id = row_id_for_event_row(row)
                for event in events:
                    if isinstance(event, dict):
                        yield ledger_path.name, str(collection), row_id, row, event


def source_event_credit_cap_failures(row: dict[str, Any], event: dict[str, Any], *, row_id: str | None = None) -> list[str]:
    """Return row-local failures for source-role credit-cap semantics.

    ``S0`` means the event itself creates no route credit. ``no-new-credit`` is
    narrower: it is allowed only for freshness replay events that retain already
    acquired public-record custody without adding incremental route authority.
    """
    failures: list[str] = []
    rid = row_id or row_id_for_event_row(row)
    eid = event.get("event_id", "<event>")
    role = event.get("source_role")
    disposition = event.get("source_ref_disposition")
    cap = event.get("credit_cap")
    scope = event.get("credit_cap_scope")
    refs = event.get("source_refs", []) or []

    if cap == "no-new-credit":
        if role != "acquired_support" or disposition != "retained_as_acquired_support":
            failures.append(f"{rid}/{eid}: no-new-credit is reserved for retained acquired-support freshness custody")
        if scope != "freshness_event_no_incremental_route_credit":
            failures.append(f"{rid}/{eid}: no-new-credit requires freshness_event_no_incremental_route_credit scope")
        if not refs:
            failures.append(f"{rid}/{eid}: no-new-credit event must name retained public source refs")
    elif disposition == "retained_as_acquired_support":
        failures.append(f"{rid}/{eid}: retained acquired-support custody must use no-new-credit")

    if disposition == "retained_as_forecast_runway":
        if role != "forecast_runway":
            failures.append(f"{rid}/{eid}: retained forecast-runway custody must use forecast_runway role")
        if cap != "S0":
            failures.append(f"{rid}/{eid}: retained forecast-runway custody must be S0-capped")
        if scope != "source_role_event_no_new_route_credit":
            failures.append(f"{rid}/{eid}: retained forecast-runway custody requires source_role_event_no_new_route_credit scope")
        if not refs:
            failures.append(f"{rid}/{eid}: retained forecast-runway event must name retained source refs")

    if disposition == "retained_as_operational_status":
        if role != "operational_status":
            failures.append(f"{rid}/{eid}: retained operational-status custody must use operational_status role")
        if cap != "S0":
            failures.append(f"{rid}/{eid}: retained operational-status custody must be S0-capped")
        if scope != "source_role_event_no_new_route_credit":
            failures.append(f"{rid}/{eid}: retained operational-status custody requires source_role_event_no_new_route_credit scope")
        if not refs:
            failures.append(f"{rid}/{eid}: retained operational-status event must name retained source refs")

    return failures

def source_event_failures_for_row(row: dict[str, Any]) -> list[str]:
    """Row-local source_role_event shape/leakage checks used by replay tests.

    Archive-wide checks such as duplicate event ids and bibliography membership
    remain in lint_archive.py.  This helper covers the mutation classes that are
    safe to test in isolation.
    """
    failures: list[str] = []
    row_refs = set(row.get("source_refs", []) or [])
    row_id = row_id_for_event_row(row)
    events = row.get("source_role_events", []) or []
    if not isinstance(events, list):
        return [f"{row_id}: source_role_events not list"]
    for event in events:
        if not isinstance(event, dict):
            failures.append(f"{row_id}: non-object source_role_event")
            continue
        eid = event.get("event_id", "<event>")
        role = event.get("source_role")
        disposition = event.get("source_ref_disposition")
        refs = set(event.get("source_refs", []) or [])
        if role not in SOURCE_ROLE_VALUES:
            failures.append(f"{row_id}/{eid}: unknown source_role {role}")
        if disposition not in SOURCE_REF_DISPOSITIONS:
            failures.append(f"{row_id}/{eid}: unknown disposition {disposition}")
        cap = event.get("credit_cap")
        if cap not in CREDIT_CAP_VALUES:
            failures.append(f"{row_id}/{eid}: bad credit_cap {cap}")
        failures.extend(source_event_credit_cap_failures(row, event, row_id=row_id))
        if role in SOURCE_CUSTODY_ROLES and disposition != "historical_source_role_normalization" and cap != "S0":
            failures.append(f"{row_id}/{eid}: non-S0 source-custody credit_cap {cap}")
        if disposition in {"excluded_from_acquired_source_refs", "forbidden_on_metadata_wrapper"} and refs & row_refs:
            failures.append(f"{row_id}/{eid}: forbidden/excluded refs leaked into row source_refs")
        if disposition in RETAINED_SOURCE_REF_DISPOSITIONS and refs - row_refs:
            failures.append(f"{row_id}/{eid}: retained source refs missing from row source_refs")
    return failures

def load_json(root: Path, rel: str) -> Any:
    """Load a top-level ledger/control JSON file relative to an archive root."""
    return json.loads((root / rel).read_text())


def find_ledger_row(root: Path, rel: str, collection: str, id_field: str, row_id: str) -> dict[str, Any] | None:
    """Return one row from a ledger collection without making a route registry.

    Many source-role policy modules need this identical structural lookup before
    applying route-local science checks.  Keeping it here prevents each policy
    from growing its own slightly different row-discovery semantics.
    """
    rows = load_json(root, rel).get(collection, [])
    if not isinstance(rows, list):
        return None
    return next((row for row in rows if isinstance(row, dict) and row.get(id_field) == row_id), None)


def missing_source_refs(row: dict[str, Any] | None, refs: list[str]) -> list[str]:
    present = row.get("source_refs", []) if isinstance(row, dict) else []
    return [ref for ref in refs if ref not in present]


def present_source_refs(row: dict[str, Any] | None, refs: list[str]) -> list[str]:
    present = row.get("source_refs", []) if isinstance(row, dict) else []
    return [ref for ref in refs if ref in present]


def duplicate_source_refs(row: dict[str, Any] | None) -> list[str]:
    refs = row.get("source_refs", []) if isinstance(row, dict) else []
    seen: set[str] = set()
    dup: list[str] = []
    for ref in refs:
        if ref in seen and ref not in dup:
            dup.append(ref)
        seen.add(ref)
    return dup


def text_from_fields(row: dict[str, Any] | None, keys: list[str]) -> str:
    """Flatten selected row fields for policy-token checks.

    This keeps route-local token checks unchanged while avoiding copy-pasted
    string/list/dict flatteners across policy modules.
    """
    if not isinstance(row, dict):
        return ""
    parts: list[str] = []
    for key in keys:
        value = row.get(key, "")
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
    return " ".join(parts).lower()


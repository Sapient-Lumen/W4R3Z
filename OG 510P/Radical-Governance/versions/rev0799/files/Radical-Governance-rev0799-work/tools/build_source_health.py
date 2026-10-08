#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date, timedelta

from archive_meta import GENERATED, METADATA_DIR, ROOT, SOURCES_DIR, current_notes_from_index, current_revision, generated_at_utc

SOURCE_HEALTH_INPUT = METADATA_DIR / "source_health.json"
SOURCE_HEALTH_TAXONOMY_INPUT = METADATA_DIR / "source_health_taxonomy.json"
SOURCE_KEYS_INPUT = SOURCES_DIR / "source_keys.json"
SOURCE_CATALOG_INPUT = SOURCES_DIR / "source_catalog.json"
NOTE_METADATA_INPUT = METADATA_DIR / "note_metadata.json"
CLAIMS_INPUT = METADATA_DIR / "claims.json"
CASE_PACKETS_INPUT = METADATA_DIR / "case_packets.json"


VOLATILITY_WEIGHTS = {
    "live_dashboard": 30,
    "volatile": 28,
    "event_triggered": 26,
    "implementation_clock": 24,
    "current": 22,
    "periodic": 18,
    "annual": 16,
    "supersession_risk": 20,
    "stable_with_order_followup": 12,
    "stable_with_data_gap_context": 10,
    "stable": 6,
    "unclassified": 8,
}


def volatility_weight(value: str | None) -> int:
    return VOLATILITY_WEIGHTS.get(value or "unclassified", 8)


def normalize_by_taxonomy(value: str | None, field: str, taxonomy: dict) -> str:
    text = str(value or "").lower()
    default = taxonomy.get("default_labels", {}).get(field, "unclassified_or_other")
    if not text:
        return default
    for normalized_label, spec in taxonomy.get("fields", {}).get(field, {}).items():
        match_terms = [str(term).lower() for term in spec.get("match_any", [])]
        if any(term and term in text for term in match_terms):
            return normalized_label
    return default


def triage_reason(*, current_note_count: int, case_packet_count: int, claim_count: int, dependent_count: int, expected_volatility: str, manual_present: bool) -> str:
    if current_note_count:
        return "current_note_dependency"
    if case_packet_count:
        return "case_packet_dependency"
    if claim_count:
        return "claim_dependency"
    if dependent_count >= 5:
        return "high_dependency_surface"
    if expected_volatility in {"live_dashboard", "volatile", "event_triggered", "implementation_clock", "supersession_risk", "current"}:
        return "volatile_or_supersession_prone"
    if not manual_present:
        return "unclassified_dependency"
    return "routine"


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def cell(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|") or "—"


def collect_dependents(source_keys: set[str]) -> dict[str, dict[str, list[str]]]:
    dependents: dict[str, dict[str, set[str]]] = {
        key: {"notes": set(), "claims": set(), "case_packets": set()} for key in source_keys
    }
    catalog = json.loads(SOURCE_CATALOG_INPUT.read_text(encoding="utf-8"))
    for note_file, payload in catalog.get("notes", {}).items():
        for group in payload.get("groups", []):
            key = group.get("source_key")
            if key in dependents:
                dependents[key]["notes"].add(note_file)

    note_metadata = json.loads(NOTE_METADATA_INPUT.read_text(encoding="utf-8"))
    for note_file, note in note_metadata.get("notes", {}).items():
        for key in note.get("source_keys", []):
            if key in dependents:
                dependents[key]["notes"].add(note_file)

    claims = json.loads(CLAIMS_INPUT.read_text(encoding="utf-8"))
    for claim_id, claim in claims.get("claims", {}).items():
        for key in claim.get("source_keys", []):
            if key in dependents:
                dependents[key]["claims"].add(claim_id)
                note_file = claim.get("note_file")
                if note_file:
                    dependents[key]["notes"].add(note_file)

    case_packets = json.loads(CASE_PACKETS_INPUT.read_text(encoding="utf-8"))
    for case_id, case in case_packets.get("cases", {}).items():
        for key in case.get("source_keys", []):
            if key in dependents:
                dependents[key]["case_packets"].add(case_id)
                note_file = case.get("file")
                if note_file:
                    dependents[key]["notes"].add(note_file)

    return {
        key: {name: sorted(values, key=lambda v: (len(v), v)) for name, values in maps.items()}
        for key, maps in dependents.items()
    }


def source_row(key: str, registry_entry: dict, manual: dict | None, dependents: dict[str, list[str]], review_date: date | None, current_notes: set[str], taxonomy: dict) -> dict:
    manual = manual or {}
    last_checked = parse_date(manual.get("last_checked"))
    cadence = manual.get("review_cadence_days")
    next_review_due = None
    review_due = False
    if last_checked and isinstance(cadence, int) and cadence > 0:
        due = last_checked + timedelta(days=cadence)
        next_review_due = due.isoformat()
        if review_date:
            review_due = due <= review_date
    note_count = len(dependents.get("notes", []))
    claim_count = len(dependents.get("claims", []))
    case_packet_count = len(dependents.get("case_packets", []))
    dependent_count = note_count + claim_count + case_packet_count
    current_note_count = sum(1 for note in dependents.get("notes", []) if note in current_notes)
    expected_volatility = manual.get("expected_volatility", "unclassified")
    triage_score = (
        current_note_count * 60
        + case_packet_count * 35
        + claim_count * 20
        + note_count * 10
        + volatility_weight(expected_volatility)
    )
    reason = triage_reason(
        current_note_count=current_note_count,
        case_packet_count=case_packet_count,
        claim_count=claim_count,
        dependent_count=dependent_count,
        expected_volatility=expected_volatility,
        manual_present=bool(manual),
    )
    return {
        "source_key": key,
        "title": registry_entry.get("title", ""),
        "publisher": registry_entry.get("publisher", ""),
        "url": registry_entry.get("url", ""),
        "manual_health_present": bool(manual),
        "source_class": manual.get("source_class", "unclassified"),
        "publisher_class": manual.get("publisher_class", "unclassified"),
        "jurisdiction": manual.get("jurisdiction", "unclassified"),
        "expected_volatility": expected_volatility,
        "normalized_expected_volatility": normalize_by_taxonomy(expected_volatility, "expected_volatility", taxonomy),
        "first_added_revision": manual.get("first_added_revision"),
        "last_checked": manual.get("last_checked"),
        "check_method": manual.get("check_method"),
        "retrieval_result": manual.get("retrieval_result"),
        "health_status": manual.get("health_status", "unclassified"),
        "normalized_health_status": normalize_by_taxonomy(manual.get("health_status", "unclassified"), "health_status", taxonomy),
        "redirect_target": manual.get("redirect_target"),
        "supersedes": manual.get("supersedes", []),
        "superseded_by": manual.get("superseded_by", []),
        "fallback_source_keys": manual.get("fallback_source_keys", []),
        "review_cadence_days": cadence,
        "next_review_due": next_review_due,
        "review_due": review_due,
        "risk_flags": manual.get("risk_flags", []),
        "source_reliance_tier": manual.get("source_reliance_tier"),
        "manual_notes": manual.get("notes", ""),
        "dependents": dependents,
        "dependent_count": dependent_count,
        "dependent_note_count": note_count,
        "dependent_claim_count": claim_count,
        "dependent_case_packet_count": case_packet_count,
        "current_note_dependent_count": current_note_count,
        "triage_score": triage_score,
        "triage_reason": reason,
    }


def compact_source_row(row: dict) -> dict:
    """Keep SOURCE_HEALTH.json as a summary surface.

    Canonical title / URL data remain in sources/source_keys.json, manual health
    prose remains in metadata/source_health.json, and full dependent membership is
    derivable from source_catalog, claims, case_packets, and note_metadata. The
    generated JSON should carry enough to sort risk without duplicating every
    upstream catalog row.
    """

    fields = [
        "source_key",
        "manual_health_present",
        "source_class",
        "publisher_class",
        "jurisdiction",
        "expected_volatility",
        "normalized_expected_volatility",
        "first_added_revision",
        "last_checked",
        "check_method",
        "retrieval_result",
        "health_status",
        "normalized_health_status",
        "redirect_target",
        "supersedes",
        "superseded_by",
        "fallback_source_keys",
        "review_cadence_days",
        "next_review_due",
        "review_due",
        "risk_flags",
        "source_reliance_tier",
        "dependent_count",
        "dependent_note_count",
        "dependent_claim_count",
        "dependent_case_packet_count",
        "current_note_dependent_count",
        "triage_score",
        "triage_reason",
    ]
    return {field: row.get(field) for field in fields if row.get(field) not in (None, [], "")}


def render_markdown(data: dict) -> str:
    lines = [
        "# Source health",
        "",
        f"Generated for `{data['revision']}` from `metadata/source_health.json`, `metadata/source_health_taxonomy.json`, and `sources/source_keys.json`.",
        "",
        "This is an offline dependency and currentness surface. It does not prove a URL is live; it shows which source keys are checked, unchecked, volatile, supersession-prone, and depended on by notes, claims, and case packets.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Source keys | {data['source_key_count']} |",
        f"| Manual health entries | {data['manual_health_entry_count']} |",
        f"| Manual health coverage | {data['manual_health_coverage_percent']:.2f}% |",
        f"| Direct-review entries | {data.get('direct_review_entry_count', 0)} |",
        f"| Direct-review coverage | {data.get('direct_review_coverage_percent', 0):.2f}% |",
        f"| Clean direct-review entries | {data.get('clean_direct_review_entry_count', 0)} |",
        f"| Clean direct-review coverage | {data.get('clean_direct_review_coverage_percent', 0):.2f}% |",
        f"| Limited-reliance direct-review entries | {data.get('limited_reliance_entry_count', 0)} |",
        f"| Limited-reliance share | {data.get('limited_reliance_percent', 0):.2f}% |",
        f"| Follow-up capture entries | {data.get('followup_capture_entry_count', 0)} |",
        f"| Follow-up capture share | {data.get('followup_capture_percent', 0):.2f}% |",
        f"| Catalog-triage entries awaiting direct refresh | {data.get('catalog_triage_entry_count', 0)} |",
        f"| Catalog-triage share | {data.get('catalog_triage_percent', 0):.2f}% |",
        f"| Unclassified / unchecked keys | {data['unchecked_source_key_count']} |",
        f"| Review-due checked keys | {data['review_due_count']} |",
        "",
        "## Health status counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in data.get("health_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Taxonomy-pressure audit", "", "| Field | Raw unique labels | Normalized labels |", "| --- | ---: | ---: |"])
    for row in data.get("taxonomy_pressure", []):
        lines.append(f"| `{row['field']}` | {row['raw_unique_count']} | {row['normalized_unique_count']} |")
    lines.extend(["", "### Normalized volatility counts", "", "| Normalized volatility | Count |", "| --- | ---: |"])
    for status, count in data.get("normalized_expected_volatility_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "### Normalized health-status counts", "", "| Normalized status | Count |", "| --- | ---: |"])
    for status, count in data.get("normalized_health_status_counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Largest dependent surfaces", "", "| Source key | Dependents | Volatility | Status | Risk flags |", "| --- | ---: | --- | --- | --- |"])
    for row in sorted(data.get("sources", []), key=lambda item: (-item.get("dependent_count", 0), item.get("source_key", "")))[:30]:
        flags = ", ".join(f"`{flag}`" for flag in row.get("risk_flags", [])) or "—"
        lines.append(f"| `{row['source_key']}` | {row.get('dependent_count', 0)} | `{row.get('expected_volatility')}` | `{row.get('health_status')}` | {flags} |")
    lines.extend(["", "## Catalog-triage direct-refresh priority sources", "", "These source keys have a manual catalog posture but were not directly network-checked in the offline build. They are sorted by dependency and volatility so future refresh passes start where stale evidence would be most consequential.", "", "| Source key | Score | Dependents | Volatility | Status | Publisher | Title |", "| --- | ---: | ---: | --- | --- | --- | --- |"])
    if data.get("catalog_triage_refresh_priority_sources"):
        for row in data.get("catalog_triage_refresh_priority_sources", [])[:30]:
            lines.append(f"| `{row['source_key']}` | {row.get('triage_score', 0)} | {row.get('dependent_count', 0)} | `{row.get('expected_volatility')}` | `{row.get('health_status')}` | {cell(row.get('publisher'))} | {cell(row.get('title'))} |")
    else:
        lines.append("| — | 0 | 0 | — | — | — | — |")
    lines.extend(["", "## Limited-reliance direct-review sources", "", "These source keys have an official or primary route identified, but the route is intentionally limited: legal section-level, quote-level, supersession, page/PDF, or outcome reliance still needs extra evidence. They are no longer capture-required rows, but they are not clean outcome proof.", "", "| Source key | Score | Dependents | Volatility | Status | Reliance tier | Result | Publisher | Title |", "| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |"])
    if data.get("limited_reliance_priority_sources"):
        for row in data.get("limited_reliance_priority_sources", [])[:30]:
            lines.append(f"| `{row['source_key']}` | {row.get('triage_score', 0)} | {row.get('dependent_count', 0)} | `{row.get('expected_volatility')}` | `{row.get('health_status')}` | `{row.get('source_reliance_tier') or '—'}` | `{row.get('retrieval_result') or '—'}` | {cell(row.get('publisher'))} | {cell(row.get('title'))} |")
    else:
        lines.append("| — | 0 | 0 | — | — | — | — | — | — |")

    lines.extend(["", "## Follow-up capture priority sources", "", "These source keys have been moved out of catalog-only posture but still require a page-level, PDF, blocked-route, or direct-capture follow-up before quote-level or legal reliance. They are direct-refresh attempts, not clean reliance-ready checks.", "", "| Source key | Score | Dependents | Volatility | Status | Result | Publisher | Title |", "| --- | ---: | ---: | --- | --- | --- | --- | --- |"])
    if data.get("followup_capture_priority_sources"):
        for row in data.get("followup_capture_priority_sources", [])[:30]:
            lines.append(f"| `{row['source_key']}` | {row.get('triage_score', 0)} | {row.get('dependent_count', 0)} | `{row.get('expected_volatility')}` | `{row.get('health_status')}` | `{row.get('retrieval_result') or '—'}` | {cell(row.get('publisher'))} | {cell(row.get('title'))} |")
    else:
        lines.append("| — | 0 | 0 | — | — | — | — | — |")
    lines.extend(["", "## Unchecked priority sources", "", "These unchecked keys are sorted by source-health triage score, which prioritizes current notes, case packets, claims, dependency count, and volatility before routine source-health expansion.", "", "| Source key | Score | Dependents | Reason | Publisher | Title |", "| --- | ---: | ---: | --- | --- | --- |"])

    if data.get("unchecked_priority_sources"):
        for row in data.get("unchecked_priority_sources", [])[:30]:
            lines.append(f"| `{row['source_key']}` | {row.get('triage_score', 0)} | {row.get('dependent_count', 0)} | `{row.get('triage_reason', 'routine')}` | {cell(row.get('publisher'))} | {cell(row.get('title'))} |")
    else:
        lines.append("| — | 0 | 0 | — | — | — |")
    lines.extend(["", "## Manual health entries", "", "| Source key | Publisher | Last checked | Result | Next review | Dependents |", "| --- | --- | --- | --- | --- | ---: |"])
    for row in [r for r in data.get("sources", []) if r.get("manual_health_present")]:
        lines.append(f"| `{row['source_key']}` | {cell(row.get('publisher'))} | {row.get('last_checked') or '—'} | `{row.get('retrieval_result') or row.get('health_status')}` | {row.get('next_review_due') or '—'} | {row.get('dependent_count', 0)} |")
    lines.extend(["", "## Unclassified source keys", ""])
    if data.get("unchecked_source_keys"):
        for key in data.get("unchecked_source_keys", [])[:80]:
            lines.append(f"- `{key}`")
        if len(data.get("unchecked_source_keys", [])) > 80:
            lines.append(f"- … {len(data['unchecked_source_keys']) - 80} more")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    registry = json.loads(SOURCE_KEYS_INPUT.read_text(encoding="utf-8"))
    manual_health = json.loads(SOURCE_HEALTH_INPUT.read_text(encoding="utf-8"))
    taxonomy = json.loads(SOURCE_HEALTH_TAXONOMY_INPUT.read_text(encoding="utf-8"))
    source_keys = registry.get("keys", {})
    manual_entries = manual_health.get("entries", {})
    review_date = parse_date(manual_health.get("review_date"))
    dependents = collect_dependents(set(source_keys))
    current_notes = set(current_notes_from_index())

    rows = [source_row(key, entry, manual_entries.get(key), dependents.get(key, {"notes": [], "claims": [], "case_packets": []}), review_date, current_notes, taxonomy) for key, entry in sorted(source_keys.items())]
    status_counts: Counter[str] = Counter(row["health_status"] for row in rows)
    volatility_counts: Counter[str] = Counter(row["expected_volatility"] for row in rows)
    normalized_health_status_counts: Counter[str] = Counter(row["normalized_health_status"] for row in rows)
    normalized_expected_volatility_counts: Counter[str] = Counter(row["normalized_expected_volatility"] for row in rows)
    publisher_class_counts: Counter[str] = Counter(row["publisher_class"] for row in rows)
    risk_flags: Counter[str] = Counter(flag for row in rows for flag in row.get("risk_flags", []))
    unchecked = [row["source_key"] for row in rows if not row.get("manual_health_present")]
    review_due = [row["source_key"] for row in rows if row.get("review_due")]
    unchecked_priority_rows = sorted(
        [row for row in rows if not row.get("manual_health_present")],
        key=lambda row: (-row.get("triage_score", 0), -row.get("dependent_count", 0), row.get("source_key", "")),
    )[:50]
    manual_health_coverage_percent = round((len(manual_entries) / len(source_keys)) * 100, 2) if source_keys else 100.0

    def is_catalog_triage(row: dict) -> bool:
        return str(row.get("check_method") or "").startswith("catalog_dependency_backfill")

    def needs_followup_capture(row: dict) -> bool:
        """Return True only when the source still needs capture work.

        Earlier revisions treated any ``followup`` token as a capture warning,
        which pulled stable rows such as ``stable_report_with_followup_clock``
        into the same queue as blocked pages and PDF/search-only routes. That
        blurred two different risks: ordinary review clocks versus missing
        page-level capture. Keep the warning queue reserved for sources that
        still need capture, blocked-route, search-only, or PDF-level work before
        quote-level or legal reliance.
        """

        values = [
            row.get("check_method"),
            row.get("retrieval_result"),
            row.get("health_status"),
            " ".join(row.get("risk_flags", [])),
        ]
        text = " ".join(str(value or "").lower() for value in values)
        capture_terms = (
            "followup-capture-needed",
            "follow-up-capture-needed",
            "needs_followup_capture",
            "needs_follow-up_capture",
            "direct_refresh_attempted_needs_followup_capture",
            "page_level_capture",
            "page-level capture",
            "blocked",
            "search_only",
            "search-only",
            "pdf_search",
            "pdf-only",
            "pdf or search",
        )
        return any(term in text for term in capture_terms)

    def is_limited_reliance(row: dict) -> bool:
        values = [
            row.get("source_reliance_tier"),
            row.get("check_method"),
            row.get("retrieval_result"),
            row.get("health_status"),
            " ".join(row.get("risk_flags", [])),
        ]
        text = " ".join(str(value or "").lower() for value in values)
        return "reliance_limited" in text or "reliance-limited" in text or "quote_limited" in text or "outcome_limited" in text or "status_limited" in text

    catalog_triaged_rows = [row for row in rows if row.get("manual_health_present") and is_catalog_triage(row)]
    directly_reviewed_rows = [row for row in rows if row.get("manual_health_present") and not is_catalog_triage(row)]
    followup_capture_rows = [row for row in directly_reviewed_rows if needs_followup_capture(row)]
    limited_reliance_rows = [row for row in directly_reviewed_rows if not needs_followup_capture(row) and is_limited_reliance(row)]
    clean_direct_review_rows = [row for row in directly_reviewed_rows if not needs_followup_capture(row) and not is_limited_reliance(row)]
    catalog_triage_refresh_priority_rows = sorted(
        catalog_triaged_rows,
        key=lambda row: (-row.get("triage_score", 0), -row.get("dependent_count", 0), row.get("source_key", "")),
    )[:50]
    followup_capture_priority_rows = sorted(
        followup_capture_rows,
        key=lambda row: (-row.get("triage_score", 0), -row.get("dependent_count", 0), row.get("source_key", "")),
    )[:50]
    limited_reliance_priority_rows = sorted(
        limited_reliance_rows,
        key=lambda row: (-row.get("triage_score", 0), -row.get("dependent_count", 0), row.get("source_key", "")),
    )[:50]
    direct_review_coverage_percent = round((len(directly_reviewed_rows) / len(source_keys)) * 100, 2) if source_keys else 100.0
    clean_direct_review_coverage_percent = round((len(clean_direct_review_rows) / len(source_keys)) * 100, 2) if source_keys else 100.0
    limited_reliance_percent = round((len(limited_reliance_rows) / len(source_keys)) * 100, 2) if source_keys else 0.0
    followup_capture_percent = round((len(followup_capture_rows) / len(source_keys)) * 100, 2) if source_keys else 0.0
    catalog_triage_percent = round((len(catalog_triaged_rows) / len(source_keys)) * 100, 2) if source_keys else 0.0

    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "source_health_source": str(SOURCE_HEALTH_INPUT.relative_to(ROOT)),
        "source_health_taxonomy_source": str(SOURCE_HEALTH_TAXONOMY_INPUT.relative_to(ROOT)),
        "source_key_registry": str(SOURCE_KEYS_INPUT.relative_to(ROOT)),
        "source_catalog_source": str(SOURCE_CATALOG_INPUT.relative_to(ROOT)),
        "note_metadata_source": str(NOTE_METADATA_INPUT.relative_to(ROOT)),
        "claims_source": str(CLAIMS_INPUT.relative_to(ROOT)),
        "case_packet_source": str(CASE_PACKETS_INPUT.relative_to(ROOT)),
        "json_compaction_policy": "SOURCE_HEALTH.json stores sortable source-health summaries only; canonical titles/URLs live in sources/source_keys.json, manual prose in metadata/source_health.json, and dependency detail is derivable from source_catalog, claims, case_packets, and note_metadata.",
        "review_date": manual_health.get("review_date"),
        "default_policy": manual_health.get("default_policy", {}),
        "source_key_count": len(source_keys),
        "manual_health_entry_count": len(manual_entries),
        "manual_health_coverage_percent": manual_health_coverage_percent,
        "direct_review_entry_count": len(directly_reviewed_rows),
        "direct_review_coverage_percent": direct_review_coverage_percent,
        "clean_direct_review_entry_count": len(clean_direct_review_rows),
        "clean_direct_review_coverage_percent": clean_direct_review_coverage_percent,
        "limited_reliance_entry_count": len(limited_reliance_rows),
        "limited_reliance_percent": limited_reliance_percent,
        "followup_capture_entry_count": len(followup_capture_rows),
        "followup_capture_percent": followup_capture_percent,
        "catalog_triage_entry_count": len(catalog_triaged_rows),
        "catalog_triage_percent": catalog_triage_percent,
        "unchecked_source_key_count": len(unchecked),
        "review_due_count": len(review_due),
        "health_status_counts": dict(sorted(status_counts.items())),
        "expected_volatility_counts": dict(sorted(volatility_counts.items())),
        "normalized_health_status_counts": dict(sorted(normalized_health_status_counts.items())),
        "normalized_expected_volatility_counts": dict(sorted(normalized_expected_volatility_counts.items())),
        "taxonomy_alias_fields": sorted(taxonomy.get("fields", {})),
        "taxonomy_pressure": [
            {
                "field": "health_status",
                "raw_unique_count": len(status_counts),
                "normalized_unique_count": len(normalized_health_status_counts),
            },
            {
                "field": "expected_volatility",
                "raw_unique_count": len(volatility_counts),
                "normalized_unique_count": len(normalized_expected_volatility_counts),
            },
        ],
        "publisher_class_counts": dict(sorted(publisher_class_counts.items())),
        "risk_flag_counts": dict(sorted(risk_flags.items())),
        "unchecked_source_keys": unchecked,
        "unchecked_priority_sources": [
            {
                "source_key": row["source_key"],
                "dependent_count": row.get("dependent_count", 0),
                "triage_score": row.get("triage_score", 0),
                "triage_reason": row.get("triage_reason", "routine"),
                "current_note_dependent_count": row.get("current_note_dependent_count", 0),
                "dependent_claim_count": row.get("dependent_claim_count", 0),
                "dependent_case_packet_count": row.get("dependent_case_packet_count", 0),
                "publisher": row.get("publisher", ""),
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "dependent_notes": row.get("dependents", {}).get("notes", [])[:12],
                "dependent_claims": row.get("dependents", {}).get("claims", [])[:12],
                "dependent_case_packets": row.get("dependents", {}).get("case_packets", [])[:12],
            }
            for row in unchecked_priority_rows
        ],
        "catalog_triage_refresh_priority_sources": [
            {
                "source_key": row["source_key"],
                "dependent_count": row.get("dependent_count", 0),
                "triage_score": row.get("triage_score", 0),
                "triage_reason": row.get("triage_reason", "routine"),
                "expected_volatility": row.get("expected_volatility", "unclassified"),
                "health_status": row.get("health_status", "unclassified"),
                "publisher": row.get("publisher", ""),
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "dependent_notes": row.get("dependents", {}).get("notes", [])[:12],
                "dependent_claims": row.get("dependents", {}).get("claims", [])[:12],
                "dependent_case_packets": row.get("dependents", {}).get("case_packets", [])[:12],
            }
            for row in catalog_triage_refresh_priority_rows
        ],
        "followup_capture_priority_sources": [
            {
                "source_key": row["source_key"],
                "dependent_count": row.get("dependent_count", 0),
                "triage_score": row.get("triage_score", 0),
                "triage_reason": row.get("triage_reason", "routine"),
                "expected_volatility": row.get("expected_volatility", "unclassified"),
                "health_status": row.get("health_status", "unclassified"),
                "retrieval_result": row.get("retrieval_result", ""),
                "publisher": row.get("publisher", ""),
                "title": row.get("title", ""),
                "url": row.get("url", ""),
                "dependent_notes": row.get("dependents", {}).get("notes", [])[:12],
                "dependent_claims": row.get("dependents", {}).get("claims", [])[:12],
                "dependent_case_packets": row.get("dependents", {}).get("case_packets", [])[:12],
            }
            for row in followup_capture_priority_rows
        ],
        "review_due_source_keys": review_due,
        "sources": [compact_source_row(row) for row in rows],
    }
    # SOURCE_HEALTH is the largest generated JSON surface; keep it compact so
    # substantive revisions do not pay a repeated pretty-print tax.
    (GENERATED / "SOURCE_HEALTH.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    markdown_data = {**data, "sources": rows}
    (GENERATED / "SOURCE_HEALTH.md").write_text(render_markdown(markdown_data), encoding="utf-8")
    print("OK: wrote generated/SOURCE_HEALTH.json and generated/SOURCE_HEALTH.md")


if __name__ == "__main__":
    main()

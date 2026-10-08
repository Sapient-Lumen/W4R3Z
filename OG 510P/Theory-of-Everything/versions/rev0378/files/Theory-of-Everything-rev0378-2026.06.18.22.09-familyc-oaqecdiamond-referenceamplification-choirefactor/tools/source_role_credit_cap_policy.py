#!/usr/bin/env python3
"""Audit source-role event credit-cap semantics.

This is not a new scientific registry.  It is a compact guard for a recurring
post-migration ambiguity: ``S0`` means the source-role event creates no route
credit, while ``no-new-credit`` is reserved for freshness replay events that
retain already-acquired public-record custody without granting incremental
route authority.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from source_role_event_utils import (
    CREDIT_CAP_VALUES,
    iter_source_role_event_rows,
    source_event_credit_cap_failures,
)

sys.dont_write_bytecode = True

GENERATED_AUDIT = "docs/30-program/source-role-credit-cap-audit.generated.md"


def evaluate_source_role_credit_cap(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    cap_counts: Counter[str] = Counter()
    disposition_counts: Counter[str] = Counter()
    role_disposition_cap_counts: Counter[tuple[str, str, str]] = Counter()
    scope_counts: Counter[str] = Counter()
    no_new_credit_events: list[dict[str, str]] = []
    history_only_nonzero_events: list[dict[str, str]] = []
    retained_runway_status_events = 0
    retained_acquired_events = 0
    event_rows = 0
    ledgers: set[str] = set()

    for ledger_file, collection, row_id, row, event in iter_source_role_event_rows(root):
        event_rows += 1
        ledgers.add(ledger_file)
        event_id = str(event.get("event_id", "<event>"))
        role = str(event.get("source_role", "<missing>"))
        disposition = str(event.get("source_ref_disposition", "<missing>"))
        cap = str(event.get("credit_cap", "<missing>"))
        scope = str(event.get("credit_cap_scope", "<missing>"))
        refs = event.get("source_refs", []) or []

        cap_counts[cap] += 1
        disposition_counts[disposition] += 1
        role_disposition_cap_counts[(role, disposition, cap)] += 1
        scope_counts[scope] += 1

        for failure in source_event_credit_cap_failures(row, event, row_id=row_id):
            failures.append(f"{ledger_file}:{collection}:{failure}")

        if cap == "no-new-credit":
            no_new_credit_events.append({
                "ledger": ledger_file,
                "row_id": row_id,
                "event_id": event_id,
                "role": role,
                "disposition": disposition,
                "scope": scope,
                "ref_count": str(len(refs)),
            })
        if disposition == "retained_as_acquired_support":
            retained_acquired_events += 1
        if disposition in {"retained_as_forecast_runway", "retained_as_operational_status"}:
            retained_runway_status_events += 1
        if disposition == "historical_source_role_normalization" and cap not in {"S0", "<missing>"}:
            history_only_nonzero_events.append({
                "ledger": ledger_file,
                "row_id": row_id,
                "event_id": event_id,
                "role": role,
                "cap": cap,
                "ref_count": str(len(refs)),
            })
            if refs:
                failures.append(
                    f"{ledger_file}:{collection}:{row_id}/{event_id}: historical non-S0 normalization event must not carry source_refs"
                )

    unknown_caps = sorted(set(cap_counts) - CREDIT_CAP_VALUES)
    for cap in unknown_caps:
        failures.append(f"unknown source-role credit_cap `{cap}` appears {cap_counts[cap]} times")

    return {
        "audit_file": GENERATED_AUDIT,
        "event_rows": event_rows,
        "ledger_count": len(ledgers),
        "cap_counts": dict(sorted(cap_counts.items())),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "scope_counts": dict(sorted(scope_counts.items())),
        "role_disposition_cap_counts": {
            " / ".join(key): value for key, value in sorted(role_disposition_cap_counts.items())
        },
        "no_new_credit_events": no_new_credit_events,
        "retained_acquired_events": retained_acquired_events,
        "retained_runway_status_events": retained_runway_status_events,
        "history_only_nonzero_events": history_only_nonzero_events,
        "failures": failures,
    }


def write_source_role_credit_cap_audit(root: Path) -> None:
    result = evaluate_source_role_credit_cap(root)
    lines = [
        "# Source-role credit-cap audit (generated)",
        "",
        "Generated from row-level and ledger-level `source_role_events`. Do not edit directly; run `make index` after changing source-role events or credit-cap wording.",
        "",
        f"- Source-role events checked: `{result['event_rows']}`",
        f"- Ledgers with source-role events: `{result['ledger_count']}`",
        f"- Retained acquired-support freshness events: `{result['retained_acquired_events']}`",
        f"- Retained forecast/status custody events: `{result['retained_runway_status_events']}`",
        f"- Historical non-S0 normalization events: `{len(result['history_only_nonzero_events'])}`",
        f"- Credit-cap semantic failures: `{len(result['failures'])}`",
        "",
        "## Rule",
        "",
        "`S0` means the event itself creates no route credit. `no-new-credit` is narrower: it is allowed only when a freshness replay event retains already-acquired public-record custody with `source_ref_disposition: retained_as_acquired_support`, `source_role: acquired_support`, and `credit_cap_scope: freshness_event_no_incremental_route_credit`. Forecast runway and operational-status retentions must stay `S0` with `source_role_event_no_new_route_credit` scope.",
        "",
        "## Credit-cap counts",
        "",
        "| Credit cap | Events |",
        "|---|---:|",
    ]
    for cap, count in result["cap_counts"].items():
        lines.append(f"| `{cap}` | `{count}` |")
    lines += ["", "## Credit-cap scopes", "", "| Scope | Events |", "|---|---:|"]
    for scope, count in result["scope_counts"].items():
        lines.append(f"| `{scope}` | `{count}` |")
    lines += ["", "## Role / disposition / cap combinations", "", "| Combination | Events |", "|---|---:|"]
    for combo, count in result["role_disposition_cap_counts"].items():
        lines.append(f"| `{combo}` | `{count}` |")

    lines += [
        "",
        "## `no-new-credit` custody events",
        "",
        "These rows retain existing public-record support custody for freshness replay. They do not grant incremental route authority beyond the owning row's already-declared support state.",
        "",
        "| Ledger | Row | Events |",
        "|---|---|---:|",
    ]
    grouped: dict[tuple[str, str], int] = defaultdict(int)
    for item in result["no_new_credit_events"]:
        grouped[(item["ledger"], item["row_id"])] += 1
    for (ledger, row_id), count in sorted(grouped.items()):
        lines.append(f"| `{ledger}` | `{row_id}` | `{count}` |")

    if result["history_only_nonzero_events"]:
        lines += ["", "## Historical non-S0 normalization events", ""]
        for item in result["history_only_nonzero_events"]:
            lines.append(
                f"- `{item['ledger']}` / `{item['row_id']}` / `{item['event_id']}` keeps historical row-context cap `{item['cap']}` and carries `{item['ref_count']}` source refs."
            )

    lines += ["", "## Failures", ""]
    if result["failures"]:
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("None.")
    lines += [
        "",
        "## Compression note",
        "",
        "The evaluator scans every event but retains only counts, grouped no-new-credit rows, historical non-S0 exceptions, and failures. This avoids another large all-pass table while keeping the risky credit-cap boundary visible.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_source_role_credit_cap_audit(root)
    outcome = evaluate_source_role_credit_cap(root)
    if outcome["failures"]:
        print("SOURCE-ROLE CREDIT-CAP POLICY FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("SOURCE-ROLE CREDIT-CAP POLICY OK")

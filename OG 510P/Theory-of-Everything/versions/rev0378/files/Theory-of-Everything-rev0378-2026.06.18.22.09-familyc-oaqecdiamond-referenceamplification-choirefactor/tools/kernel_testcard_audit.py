#!/usr/bin/env python3
"""Generate and validate the positive candidate-kernel testcard.

The testcard is deliberately not another route/ledger family.  It is a compact
restart surface that asks every current route row to state its primitive object,
dynamical rule, redundancy quotient, coarse-graining map, public-record map, and
three discriminator-bearing observables.  This tool keeps that surface exact
against the executable route ledger and fails closed if a route is missing or a
cell quietly exceeds its current route cap.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

TESTCARD_PATH = "KERNEL-TESTCARD.json"
MODEL_DOC_PATH = "docs/40-model/positive-kernel-testcard.md"
AUDIT_DOC_PATH = "docs/30-program/kernel-testcard-audit.generated.md"
ROUTE_LEDGER_PATH = "CANDIDATE-ROUTE-STATE-LEDGER.json"
REQUIRED_TEXT_FIELDS = [
    "primitive_objects",
    "dynamical_rule",
    "redundancy_quotient",
    "coarse_graining_map",
    "observer_public_record_map",
    "first_negative_control",
    "dominant_unpaid_debt",
    "next_kernel_work",
    "non_promotion_cap",
]
REQUIRED_ROW_FIELDS = [
    "testcard_id",
    "route_id",
    "candidate_family",
    "route_authority_state_at_import",
    "testcard_authority_cap",
    *REQUIRED_TEXT_FIELDS,
    "discriminator_observables",
]
STATE_ORDER = {f"S{i}": i for i in range(6)}
BANNED_PROMOTION_PHRASES = [
    "theory of everything is proven",
    "route closure",
    "candidate-native identifiability closure",
    "promotes the route",
    "upgrades authority",
]


def load_json(root: Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text())


def state_value(state: str) -> int:
    return STATE_ORDER.get(str(state).strip(), -1)


def validate(root: Path) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    manifest = load_json(root, "RELEASE-MANIFEST.json")
    testcard = load_json(root, TESTCARD_PATH)
    route_ledger = load_json(root, ROUTE_LEDGER_PATH)
    failures: list[str] = []

    if testcard.get("revision") != manifest.get("revision"):
        failures.append("KERNEL-TESTCARD.json revision drifted from RELEASE-MANIFEST.json")
    if testcard.get("source_route_ledger") != ROUTE_LEDGER_PATH:
        failures.append("KERNEL-TESTCARD.json source_route_ledger must point at CANDIDATE-ROUTE-STATE-LEDGER.json")
    if testcard.get("target_open_question_id") != "OQ-0057":
        failures.append("KERNEL-TESTCARD.json must remain scoped to OQ-0057")

    route_rows = route_ledger.get("route_rows", [])
    route_by_id = {row.get("route_id"): row for row in route_rows}
    rows = testcard.get("testcard_rows", [])
    testcard_by_route = {row.get("route_id"): row for row in rows}

    duplicate_routes = sorted(
        rid for rid in set(row.get("route_id") for row in rows)
        if sum(1 for row in rows if row.get("route_id") == rid) > 1
    )
    if duplicate_routes:
        failures.append(f"duplicate testcard route rows: {', '.join(duplicate_routes)}")

    missing = sorted(set(route_by_id) - set(testcard_by_route))
    extra = sorted(set(testcard_by_route) - set(route_by_id))
    if missing:
        failures.append(f"missing route rows in KERNEL-TESTCARD.json: {', '.join(missing)}")
    if extra:
        failures.append(f"testcard references unknown route rows: {', '.join(extra)}")

    id_pattern = re.compile(r"^KT-OQ0057-[A-Z0-9-]+$")
    for row in rows:
        rid = row.get("route_id", "<missing-route>")
        for field in REQUIRED_ROW_FIELDS:
            if field not in row:
                failures.append(f"{rid} missing required testcard field: {field}")
        tid = str(row.get("testcard_id", ""))
        if not id_pattern.match(tid):
            failures.append(f"{rid} has malformed testcard_id: {tid}")
        for field in REQUIRED_TEXT_FIELDS:
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"{rid} has empty required text field: {field}")
        observables = row.get("discriminator_observables")
        if not isinstance(observables, list) or len(observables) < 3:
            failures.append(f"{rid} must name at least three discriminator_observables")
        elif any(not isinstance(item, str) or not item.strip() for item in observables):
            failures.append(f"{rid} has an empty discriminator observable")

        owned_artifacts = row.get("owned_kernel_artifacts")
        if owned_artifacts is not None:
            if not isinstance(owned_artifacts, list) or not owned_artifacts:
                failures.append(f"{rid} owned_kernel_artifacts must be a non-empty list when present")
            else:
                for relative_path in owned_artifacts:
                    if not isinstance(relative_path, str) or not relative_path.strip():
                        failures.append(f"{rid} has an empty owned_kernel_artifact path")
                        continue
                    artifact_path = Path(relative_path)
                    if artifact_path.is_absolute() or ".." in artifact_path.parts:
                        failures.append(f"{rid} owned artifact escapes archive root: {relative_path}")
                    elif not (root / artifact_path).is_file():
                        failures.append(f"{rid} owned artifact is missing: {relative_path}")
            if not isinstance(row.get("owned_result_summary"), str) or not row.get("owned_result_summary", "").strip():
                failures.append(f"{rid} declares owned artifacts without owned_result_summary")

        result_rel = row.get("owned_result_artifact")
        if result_rel is not None:
            if not isinstance(result_rel, str) or not result_rel.strip():
                failures.append(f"{rid} owned_result_artifact must be a non-empty path")
            elif not isinstance(owned_artifacts, list) or result_rel not in owned_artifacts:
                failures.append(f"{rid} owned_result_artifact must appear in owned_kernel_artifacts")
            else:
                result_path = root / result_rel
                if result_path.is_file():
                    try:
                        owned_result = json.loads(result_path.read_text())
                    except Exception as exc:
                        failures.append(f"{rid} owned result is not valid JSON: {exc}")
                    else:
                        if owned_result.get("route_id") != rid:
                            failures.append(f"{rid} owned result route_id drifted: {owned_result.get('route_id')}")
                        if owned_result.get("revision") != manifest.get("revision"):
                            failures.append(f"{rid} owned result revision drifted from manifest")
                        if owned_result.get("validation_failures"):
                            failures.append(f"{rid} owned result carries validation failures")
                        result_cap = str(owned_result.get("authority_cap", ""))
                        row_cap = str(row.get("testcard_authority_cap", ""))
                        if state_value(result_cap) < 0 or state_value(result_cap) > state_value(row_cap):
                            failures.append(f"{rid} owned result cap {result_cap} exceeds or evades testcard cap {row_cap}")

        route = route_by_id.get(rid)
        if route:
            if row.get("candidate_family") != route.get("candidate_family"):
                failures.append(f"{rid} candidate_family drifted from route ledger")
            if row.get("route_authority_state_at_import") != route.get("authority_state"):
                failures.append(f"{rid} route_authority_state_at_import drifted from route ledger")
            cap = str(row.get("testcard_authority_cap", ""))
            authority = str(route.get("authority_state", ""))
            ceiling = str(route.get("promotion_ceiling", authority))
            if state_value(cap) < 0:
                failures.append(f"{rid} has unknown testcard_authority_cap: {cap}")
            if state_value(cap) > state_value(authority):
                failures.append(f"{rid} testcard cap {cap} exceeds current authority state {authority}")
            if state_value(cap) > state_value(ceiling):
                failures.append(f"{rid} testcard cap {cap} exceeds promotion ceiling {ceiling}")

        flattened = json.dumps(row, ensure_ascii=False).lower()
        for phrase in BANNED_PROMOTION_PHRASES:
            if phrase in flattened:
                failures.append(f"{rid} contains banned promotion phrase: {phrase}")

    summary = {
        "revision": manifest.get("revision", "<missing>"),
        "route_rows": len(route_rows),
        "testcard_rows": len(rows),
        "missing_routes": missing,
        "extra_routes": extra,
        "owned_result_rows": sum(1 for row in rows if row.get("owned_result_artifact")),
        "failures": failures,
    }
    return testcard, failures, summary


def md_escape(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def first_sentence(text: str, max_len: int = 120) -> str:
    text = " ".join(str(text).split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def render_model_doc(testcard: dict[str, Any], summary: dict[str, Any]) -> str:
    rows = testcard.get("testcard_rows", [])
    lines: list[str] = [
        "# Positive kernel testcard",
        "",
        f"Revision: `{testcard.get('revision', '<missing>')}`",
        "",
        "Generated from `KERNEL-TESTCARD.json` and `CANDIDATE-ROUTE-STATE-LEDGER.json`. Do not edit this file by hand; run `make index` after changing the testcard JSON.",
        "",
        "## Purpose",
        "",
        "This is the compact positive surface that rev0366 deliberately left as followthrough. It asks every current OQ-0057 route to say what its kernel would be if it were forced to make a constructive bid: primitive object, dynamics, quotient, coarse-graining, public-record map, negative control, and discriminator-bearing observables.",
        "",
        "It is not a router, not a new ledger family, and not an authority upgrade. Its job is to make candidate comparison substance-visible before the archive adds more control vocabulary.",
        "",
        "## Invariant rule",
        "",
        "A filled cell is a restart aid only. It can reveal a sharper missing experiment, proof, quotient, or public-record obligation, but it cannot promote a route beyond its current `CANDIDATE-ROUTE-STATE-LEDGER.json` authority state.",
        "",
        "## Coverage summary",
        "",
        f"- Route rows checked: `{summary.get('route_rows')}`",
        f"- Testcard rows: `{summary.get('testcard_rows')}`",
        f"- Missing routes: `{len(summary.get('missing_routes', []))}`",
        f"- Extra routes: `{len(summary.get('extra_routes', []))}`",
        f"- Owned executable result rows: `{summary.get('owned_result_rows', 0)}`",
        f"- Validation failures: `{len(summary.get('failures', []))}`",
        "",
        "## Route kernel cards",
        "",
    ]
    for row in rows:
        lines.extend([
            f"### `{row.get('route_id')}`",
            "",
            f"- **Family:** {row.get('candidate_family')}",
            f"- **Current cap:** `{row.get('testcard_authority_cap')}`; imported route state `{row.get('route_authority_state_at_import')}`.",
            f"- **Primitive objects:** {row.get('primitive_objects')}",
            f"- **Dynamical rule:** {row.get('dynamical_rule')}",
            f"- **Redundancy / quotient:** {row.get('redundancy_quotient')}",
            f"- **Coarse-graining map:** {row.get('coarse_graining_map')}",
            f"- **Observer / public-record map:** {row.get('observer_public_record_map')}",
            f"- **First negative control:** {row.get('first_negative_control')}",
            f"- **Dominant unpaid debt:** {row.get('dominant_unpaid_debt')}",
            f"- **Next kernel work:** {row.get('next_kernel_work')}",
        ])
        if row.get("owned_result_artifact"):
            lines.append(f"- **Owned executable result:** `{row.get('owned_result_artifact')}`")
            lines.append(f"- **Owned result summary:** {row.get('owned_result_summary')}")
            lines.append("- **Owned artifacts:**")
            for artifact in row.get("owned_kernel_artifacts", []):
                lines.append(f"  - `{artifact}`")
        lines.append("- **Top discriminator observables:**")
        for obs in row.get("discriminator_observables", []):
            lines.append(f"  - {obs}")
        lines.append("")

    lines.extend([
        "## One-line deficit map",
        "",
        "| Route | Cap | Dominant unpaid debt | First next work |",
        "|---|---:|---|---|",
    ])
    for row in rows:
        lines.append(
            f"| `{md_escape(row.get('route_id'))}` | `{md_escape(row.get('testcard_authority_cap'))}` | {md_escape(first_sentence(row.get('dominant_unpaid_debt', '')))} | {md_escape(first_sentence(row.get('next_kernel_work', '')))} |"
        )
    lines.extend([
        "",
        "## Non-promotion boundary",
        "",
        testcard.get("non_promotion_boundary", "This testcard creates no route authority."),
        "",
    ])
    return "\n".join(lines)


def render_audit_doc(testcard: dict[str, Any], summary: dict[str, Any]) -> str:
    rows = testcard.get("testcard_rows", [])
    lines = [
        "# Kernel testcard audit (generated)",
        "",
        "Generated from `KERNEL-TESTCARD.json`, `CANDIDATE-ROUTE-STATE-LEDGER.json`, and `RELEASE-MANIFEST.json`. Do not edit directly; run `make index` after changing route rows or the positive testcard.",
        "",
        f"- Revision: `{summary.get('revision')}`",
        f"- Route rows checked: `{summary.get('route_rows')}`",
        f"- Testcard rows: `{summary.get('testcard_rows')}`",
        f"- Missing routes: `{len(summary.get('missing_routes', []))}`",
        f"- Extra routes: `{len(summary.get('extra_routes', []))}`",
        f"- Owned executable result rows: `{summary.get('owned_result_rows', 0)}`",
        f"- Validation failures: `{len(summary.get('failures', []))}`",
        "",
        "## Compact route coverage",
        "",
        "| Route | Cap | Discriminator count | Owned executable | Dominant debt present | Next work present |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{md_escape(row.get('route_id'))}` | `{md_escape(row.get('testcard_authority_cap'))}` | `{len(row.get('discriminator_observables', []))}` | `{str(bool(row.get('owned_result_artifact'))).lower()}` | `{str(bool(str(row.get('dominant_unpaid_debt', '')).strip())).lower()}` | `{str(bool(str(row.get('next_kernel_work', '')).strip())).lower()}` |"
        )
    if summary.get("failures"):
        lines.extend(["", "## Failures", ""])
        for failure in summary["failures"]:
            lines.append(f"- {failure}")
    lines.extend([
        "",
        "## Rule",
        "",
        "The positive kernel testcard is a compression target, not a promotion mechanism. A row is valid only when it covers an existing route, names at least three discriminator observables, and keeps its testcard cap at or below the route's current authority state and promotion ceiling.",
        "",
    ])
    return "\n".join(lines)


def write_if_changed(path: Path, text: str) -> bool:
    rendered = text.rstrip() + "\n"
    if path.exists() and path.read_text() == rendered:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered)
    return True


def check_file(path: Path, expected: str) -> list[str]:
    rendered = expected.rstrip() + "\n"
    if not path.exists():
        return [f"missing generated kernel-testcard surface: {path.as_posix()}"]
    if path.read_text() != rendered:
        return [f"generated kernel-testcard surface drifted: {path.as_posix()}; run make index"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated surfaces are missing/stale or validation fails")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    testcard, failures, summary = validate(root)
    model_doc = render_model_doc(testcard, summary)
    audit_doc = render_audit_doc(testcard, summary)
    if args.check:
        check_failures = list(failures)
        check_failures.extend(check_file(root / MODEL_DOC_PATH, model_doc))
        check_failures.extend(check_file(root / AUDIT_DOC_PATH, audit_doc))
        if check_failures:
            print("KERNEL TESTCARD AUDIT FAIL")
            for failure in check_failures:
                print(f"- {failure}")
            return 1
        print(f"KERNEL TESTCARD AUDIT OK rows={summary.get('testcard_rows')} revision={summary.get('revision')}")
        return 0
    changed = []
    if write_if_changed(root / MODEL_DOC_PATH, model_doc):
        changed.append(MODEL_DOC_PATH)
    if write_if_changed(root / AUDIT_DOC_PATH, audit_doc):
        changed.append(AUDIT_DOC_PATH)
    print("KERNEL TESTCARD AUDIT wrote " + (", ".join(changed) if changed else "no changes"))
    if failures:
        print("KERNEL TESTCARD AUDIT validation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

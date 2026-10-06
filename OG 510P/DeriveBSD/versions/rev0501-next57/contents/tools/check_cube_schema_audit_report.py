#!/usr/bin/env python3
"""Audit the cube's schema posture and keep the report live.

r522 introduces a small cube-wide audit beside the removable-media work.  The
point is not to force every old schema to become runtime-shaped immediately;
it is to make the drift visible and deterministic: fixture-heavy schemas,
missing canonical examples for base/helper schemas, runtime-contract-shaped
schemas, and exact fixture schemas are all counted from the live tree.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r533"
SCHEMA = "spec/cube.schema.audit.report.schema.json"
EXAMPLE = "spec/examples/cube.schema.audit.report.json"
CONST_HEAVY_THRESHOLD = 50

REQUIRED_TEXT_TOKENS = {
    "CHANGELOG.md": [VERSION, "cube.schema.audit.report", "tools/check_cube_schema_audit_report.py"],
    "README.md": [VERSION, "cube-schema-audit", "tools/check_cube_schema_audit_report.py"],
    "docs/00-index.md": [VERSION, "docs/current/cube-schema-audit.md"],
    "docs/98-archive-hygiene.md": ["check_cube_schema_audit_report.py"],
    "docs/99-llm-runbook.md": ["check_cube_schema_audit_report.py"],
    "docs/current/cube-schema-audit.md": ["cube.schema.audit.report", "const-heavy", "runtime-contract"],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def singleton_kind(schema: dict[str, Any]) -> str | None:
    if schema.get("type") != "object":
        return None
    req = schema.get("required")
    props = schema.get("properties")
    if not isinstance(req, list) or "kind" not in req or not isinstance(props, dict):
        return None
    k = props.get("kind")
    if not isinstance(k, dict):
        return None
    if isinstance(k.get("const"), str):
        return k["const"]
    enum = k.get("enum")
    if isinstance(enum, list) and len(enum) == 1 and isinstance(enum[0], str):
        return enum[0]
    return None


def count_patterns(node: Any) -> int:
    if isinstance(node, dict):
        return (1 if "pattern" in node else 0) + sum(count_patterns(v) for v in node.values())
    if isinstance(node, list):
        return sum(count_patterns(v) for v in node)
    return 0


def build_report() -> dict[str, Any]:
    schema_paths = sorted((ROOT / "spec").glob("*.schema.json"))
    example_paths = sorted((ROOT / "spec" / "examples").glob("*.json"))

    root_kind_count = 0
    with_example: list[str] = []
    without_example: list[str] = []
    const_heavy: list[dict[str, Any]] = []
    runtime_contract: list[str] = []
    exact_fixture: list[str] = []
    mismatches: list[str] = []

    for path in schema_paths:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        try:
            schema = json.loads(text)
        except Exception:
            # Other checks catch invalid JSON. Keep the audit deterministic.
            schema = {}

        base = path.name.removesuffix(".schema.json")
        if (ROOT / "spec" / "examples" / f"{base}.json").exists():
            with_example.append(rel)
        else:
            without_example.append(rel)

        kind = singleton_kind(schema) if isinstance(schema, dict) else None
        if kind:
            root_kind_count += 1
            if "." in kind and kind != base:
                mismatches.append(rel)

        const_count = text.count('"const"')
        if const_count > CONST_HEAVY_THRESHOLD:
            const_heavy.append({"schema": rel, "const_count": const_count})

        if path.name.endswith(".fixture.schema.json"):
            exact_fixture.append(rel)

        pattern_count = count_patterns(schema)
        if isinstance(schema, dict) and "$defs" in schema and pattern_count >= 2 and const_count <= CONST_HEAVY_THRESHOLD:
            runtime_contract.append(rel)

    const_heavy.sort(key=lambda x: (-int(x["const_count"]), x["schema"]))
    runtime_contract.sort()
    exact_fixture.sort()
    without_example.sort()

    next_targets = [x["schema"] for x in const_heavy if "post_detach" in x["schema"] and not x["schema"].endswith(".fixture.schema.json")][:8]

    return {
        "kind": "cube.schema.audit.report",
        "schema_version": "1.0",
        "report_id": "cube-schema-audit-20260530-r532",
        "generated_for_version": VERSION,
        "scope": {
            "schema_glob": "spec/*.schema.json",
            "example_glob": "spec/examples/*.json",
            "invalid_examples_included": False,
            "audit_generated_at": "release-build-time-deterministic",
        },
        "audit_policy": {
            "const_heavy_threshold": CONST_HEAVY_THRESHOLD,
            "runtime_contract_rule": "has-$defs-and-patterns-and-not-const-heavy",
            "schema_without_example_policy": "allowed-for-base-helper-schemas-but-reported",
        },
        "counts": {
            "schemas_total": len(schema_paths),
            "examples_total": len(example_paths),
            "root_kind_schema_count": root_kind_count,
            "schemas_with_canonical_example_count": len(with_example),
            "schemas_without_canonical_example_count": len(without_example),
            "const_heavy_schema_count": len(const_heavy),
            "runtime_contract_shaped_schema_count": len(runtime_contract),
            "exact_fixture_schema_count": len(exact_fixture),
            "dotted_kind_filename_mismatch_count": len(mismatches),
        },
        "posture_buckets": {
            "runtime_contract_shaped_schemas": runtime_contract,
            "exact_fixture_schemas": exact_fixture,
            "const_heavy_schema_sample": const_heavy[:25],
            "schemas_without_canonical_example": without_example,
        },
        "findings": [
            {
                "finding_id": "const-heavy-post-detach-history-remains",
                "severity": "medium",
                "summary": "Several older post-detach schemas are still exact or near-exact fixture contracts rather than dynamic runtime contracts.",
                "action": "Continue the r520 production/fixture split pattern on the highest const-count post-detach schemas first.",
            },
            {
                "finding_id": "helper-schemas-without-examples-are-reported-not-blocked",
                "severity": "info",
                "summary": "Base/helper schemas without canonical examples are allowed today, but their count is now visible in a release artifact.",
                "action": "Do not make helper schemas invisible; either add examples when they become artifacts or keep them listed as base helpers.",
            },
            {
                "finding_id": "runtime-contract-shaped-surface-is-growing",
                "severity": "info",
                "summary": "The runtime-contract bucket now includes the r521-r523 post-detach schemas, the cube audit report, and the hygiene checkset manifest.",
                "action": "Use the same $defs plus pattern plus semantic-check style for future lifecycle receipts.",
            },
        ],
        "refactor_policy": {
            "canonical_digest_helper": "tools/cube_digest_lib.py",
            "checker_refactor_target": "post-detach-and-cube-audit-checkers-use-shared-canonical-digest-rule",
            "next_schema_split_targets": next_targets,
        },
        "negative_fixture_policy": "schema-audit-report-must-match-live-cube-scan",
    }


def validate_report(obj: dict[str, Any]) -> list[str]:
    schema = load_json(ROOT, SCHEMA)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require_text_tokens() -> None:
    for rel, tokens in REQUIRED_TEXT_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required surface: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for tok in tokens:
            if tok not in text:
                fail(f"{rel} missing required audit token {tok!r}")


def require_hygiene_wiring() -> None:
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8")
    if "check_cube_schema_audit_report.py" not in hygiene:
        fail("tools/hygiene.py missing check_cube_schema_audit_report.py")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write the live audit report example")
    args = ap.parse_args()

    expected = build_report()
    if args.write:
        out = ROOT / EXAMPLE
        out.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {EXAMPLE}")
        return 0

    observed = load_json(ROOT, EXAMPLE)
    errs = validate_report(observed)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    if observed != expected:
        print("cube schema audit report is stale; regenerate with:", file=sys.stderr)
        print("  python3 tools/check_cube_schema_audit_report.py --write", file=sys.stderr)
        # Show a compact first-difference hint.
        if observed.get("counts") != expected.get("counts"):
            print(f"observed counts: {observed.get('counts')}", file=sys.stderr)
            print(f"expected counts: {expected.get('counts')}", file=sys.stderr)
        raise SystemExit(1)
    if observed["counts"]["dotted_kind_filename_mismatch_count"] != 0:
        fail("dotted kind filename mismatch count must stay zero")
    if "tools/cube_digest_lib.py" != observed["refactor_policy"]["canonical_digest_helper"]:
        fail("canonical digest helper must remain tools/cube_digest_lib.py")
    require_hygiene_wiring()
    require_text_tokens()
    print("cube schema audit report check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

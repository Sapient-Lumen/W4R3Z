#!/usr/bin/env python3
"""Validate the live r524 cube schema refactor backlog.

r522 made const-heavy schemas visible. r524 turns that audit into an actionable
backlog: every live const-heavy schema gets a prioritized item, the post-detach
runtime-lane targets are promoted first, and the one already-split fixture schema
is recorded as completed rather than silently counted as unfinished work.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cube_check_lib import (
    fail,
    require_generated_artifact_id_consistency,
    release_token,
    require_text_tokens as require_text_token_map,
    validation_errors as cube_validation_errors,
)
from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-06-18r630"
SCHEMA = "spec/cube.schema.refactor.backlog.schema.json"
EXAMPLE = "spec/examples/cube.schema.refactor.backlog.json"
AUDIT_EXAMPLE = "spec/examples/cube.schema.audit.report.json"
CONST_HEAVY_THRESHOLD = 50

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "cube.schema.refactor.backlog", "check_cube_schema_refactor_backlog.py"],
    "README.md": [VERSION, "schema-refactor-backlog", "denial-reason-registry"],
    "docs/00-index.md": [VERSION, "docs/current/cube-schema-refactor-backlog.md"],
    "docs/98-archive-hygiene.md": ["check_cube_schema_refactor_backlog.py"],
    "docs/99-llm-runbook.md": ["check_cube_schema_refactor_backlog.py"],
    "docs/current/cube-schema-refactor-backlog.md": ["cube.schema.refactor.backlog", "const-heavy", "generic-runtime-schema-plus-exact-fixture-schema"],
    "docs/779-removable-media-local-fallback-post-detach-denial-reason-registry-and-schema-refactor-backlog.md": [
        "cube.schema.refactor.backlog",
        "check_cube_schema_refactor_backlog.py",
    ],
}


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    return cube_validation_errors(ROOT, schema_rel, obj)


def const_count(path: Path) -> int:
    return path.read_text(encoding="utf-8", errors="replace").count('"const"')


def domain_for(rel: str) -> str:
    if "post_detach" in rel:
        return "post-detach"
    if rel == "spec/net.publish.session.schema.json":
        return "network-publish"
    if rel.startswith("spec/content.import."):
        return "content-import"
    if rel == "spec/preopen.map.schema.json":
        return "preopen"
    return "other"


def status_for(rel: str) -> str:
    if rel == "spec/net.publish.session.schema.json":
        return "audited-runtime-policy-const-mesh"
    completed_fixture_splits = (
        "removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.fixture.schema.json",
        "removable.media.local.post_detach.launch.evidence.fixture.schema.json",
        "removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.fixture.schema.json",
        "removable.media.local.post_detach.reader.use.ledger.retention.receipt.fixture.schema.json",
        "removable.media.local.post_detach.denial.receipt.fixture.schema.json",
        "removable.media.local.post_detach.recovery.evidence.fixture.schema.json",
        "removable.media.local.post_detach.reader.use.ledger.receipt.fixture.schema.json",
        "removable.media.local.post_detach.fresh.authority.consumption.receipt.fixture.schema.json",
        "removable.media.local.post_detach.successor.index.checkpoint.receipt.fixture.schema.json",
        "removable.media.local.post_detach.fresh.authority.receipt.fixture.schema.json",
        "removable.media.local.post_detach.reader.admission.receipt.fixture.schema.json",
        "removable.media.local.post_detach.successor.index.cutover.receipt.fixture.schema.json",
        "removable.media.local.post_detach.contract.fixture.schema.json",
        "removable.media.local.post_detach.reader.use.receipt.fixture.schema.json",
        "removable.media.local.post_detach.query.projection.fixture.schema.json",
        "removable.media.local.post_detach.export.bundle.fixture.schema.json",
        "removable.media.local.post_detach.revocation.tombstone.fixture.schema.json",
    )
    if rel.endswith(completed_fixture_splits):
        return "completed-production-fixture-split"
    return "open"


def priority_for(rel: str, count: int) -> str:
    if domain_for(rel) == "post-detach" and status_for(rel) == "open":
        return "p0"
    if count >= 100:
        return "p1"
    return "p2"


def action_for(rel: str) -> str:
    if status_for(rel) == "completed-production-fixture-split":
        return "Keep the exact fixture schema as history while using the paired generic runtime schema for new broker outputs."
    if status_for(rel) == "audited-runtime-policy-const-mesh":
        return "Keep this as a runtime policy schema: consts encode publish posture, while session identity, endpoint, authority, relay, and digest fields remain dynamic and are guarded by tools/check_net_publish_session_schema_classification.py."
    if domain_for(rel) == "post-detach":
        return "Split into a generic runtime schema, exact fixture schema, and semantic checker before adding new lifecycle joins."
    return "Assess whether this is a legacy exact fixture surface; if yes, split fixture literals from runtime contract fields."


def build_backlog() -> dict[str, Any]:
    audit = load_json(ROOT, AUDIT_EXAMPLE)
    audit_next = set(audit.get("refactor_policy", {}).get("next_schema_split_targets", []))
    items: list[dict[str, Any]] = []
    for path in sorted((ROOT / "spec").glob("*.schema.json")):
        rel = path.relative_to(ROOT).as_posix()
        count = const_count(path)
        if count <= CONST_HEAVY_THRESHOLD:
            continue
        item = {
            "schema": rel,
            "const_count": count,
            "priority": priority_for(rel, count),
            "status": status_for(rel),
            "domain": domain_for(rel),
            "recommended_action": action_for(rel),
            "audit_next_target": rel in audit_next,
        }
        items.append(item)

    items.sort(key=lambda x: (x["status"] != "open", x["priority"], -int(x["const_count"]), x["schema"]))
    open_count = sum(1 for item in items if item["status"] == "open")
    completed_count = sum(1 for item in items if item["status"] != "open")
    post_detach_count = sum(1 for item in items if item["domain"] == "post-detach")
    highest = max((int(item["const_count"]) for item in items), default=0)

    return {
        "kind": "cube.schema.refactor.backlog",
        "schema_version": "1.0",
        "backlog_id": f"cube-schema-refactor-backlog-{release_token(VERSION)}",
        "generated_for_version": VERSION,
        "source_audit_binding": {
            "audit_report_kind": "cube.schema.audit.report",
            "audit_report_schema": "spec/cube.schema.audit.report.schema.json",
            "audit_report_example": AUDIT_EXAMPLE,
            "audit_report_computed_digest": file_json_digest(ROOT, AUDIT_EXAMPLE),
            "const_heavy_threshold": CONST_HEAVY_THRESHOLD,
        },
        "selection_policy": {
            "selected_surface": "all-live-const-heavy-schemas",
            "priority_order": "post-detach-runtime-lane-before-other-legacy-fixture-heavy-schemas",
            "fixture_split_pattern": "generic-runtime-schema-plus-exact-fixture-schema-plus-semantic-checker",
            "non_blocking_legacy_history": True,
        },
        "counts": {
            "items_total": len(items),
            "open_items": open_count,
            "completed_items": completed_count,
            "post_detach_items": post_detach_count,
            "highest_const_count": highest,
            "audit_next_targets_count": len(audit_next),
        },
        "items": items,
        "invariants": {
            "every_const_heavy_schema_has_backlog_item": True,
            "audit_next_targets_are_p0_or_completed": True,
            "completed_items_have_allowed_disposition": True,
            "open_items_have_action": True,
        },
        "refactor_policy": {
            "next_cut_recommendation": "With post-detach p0 splits closed and net.publish.session audited as runtime policy, reduce the next p2 const-heavy surface only when it is on the critical implementation path.",
            "do_not_rewrite_historical_examples_without_fixture_schema": True,
            "checker_refactor_direction": "move-const-heavy-post-detach-schemas-through-generic-plus-fixture-split",
        },
    }


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("backlog version mismatch")
    if obj.get("source_audit_binding", {}).get("audit_report_computed_digest") != file_json_digest(ROOT, AUDIT_EXAMPLE):
        errors.append("audit report digest binding is stale")
    if obj.get("source_audit_binding", {}).get("const_heavy_threshold") != CONST_HEAVY_THRESHOLD:
        errors.append("const-heavy threshold drifted")

    live_const_heavy = {
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "spec").glob("*.schema.json"))
        if const_count(path) > CONST_HEAVY_THRESHOLD
    }
    item_by_schema = {item.get("schema"): item for item in obj.get("items", [])}
    if set(item_by_schema) != live_const_heavy:
        errors.append("backlog items must exactly cover live const-heavy schemas")

    audit = load_json(ROOT, AUDIT_EXAMPLE)
    audit_next = set(audit.get("refactor_policy", {}).get("next_schema_split_targets", []))
    missing_audit_next = sorted(audit_next - set(item_by_schema))
    if missing_audit_next:
        errors.append(f"audit next targets missing from backlog: {missing_audit_next}")

    for schema, item in item_by_schema.items():
        path = ROOT / schema if isinstance(schema, str) else None
        if not path or not path.exists():
            errors.append(f"unknown backlog schema path: {schema}")
            continue
        observed_count = const_count(path)
        if item.get("const_count") != observed_count:
            errors.append(f"{schema}: const_count {item.get('const_count')} != live {observed_count}")
        if item.get("domain") != domain_for(schema):
            errors.append(f"{schema}: domain drifted")
        if item.get("status") != status_for(schema):
            errors.append(f"{schema}: status drifted")
        if item.get("priority") != priority_for(schema, observed_count):
            errors.append(f"{schema}: priority drifted")
        if item.get("audit_next_target") != (schema in audit_next):
            errors.append(f"{schema}: audit_next_target drifted")
        if schema in audit_next and item.get("priority") != "p0" and item.get("status") == "open":
            errors.append(f"{schema}: audit next target must be p0 unless completed")
        if item.get("status") == "completed-production-fixture-split" and not schema.endswith(".fixture.schema.json"):
            errors.append(f"{schema}: completed split item must be an exact fixture schema")
        if item.get("status") == "audited-runtime-policy-const-mesh":
            if schema != "spec/net.publish.session.schema.json":
                errors.append(f"{schema}: only net.publish.session may use audited-runtime-policy-const-mesh today")
            if not (ROOT / "tools" / "check_net_publish_session_schema_classification.py").exists():
                errors.append("audited net.publish.session status requires check_net_publish_session_schema_classification.py")
        if item.get("status") == "open" and len(str(item.get("recommended_action", ""))) < 12:
            errors.append(f"{schema}: open item needs a concrete action")

    counts = obj.get("counts", {})
    expected_counts = build_backlog()["counts"]
    if counts != expected_counts:
        errors.append(f"counts drifted: {counts} != {expected_counts}")
    for key, value in obj.get("invariants", {}).items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


def require_docs() -> None:
    require_text_token_map(ROOT, REQUIRED_DOC_TOKENS, "backlog")
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8", errors="replace")
    if "check_cube_schema_refactor_backlog.py" not in hygiene:
        fail("tools/hygiene.py missing cube schema refactor backlog checker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write the live schema refactor backlog")
    args = ap.parse_args()

    expected = build_backlog()
    if args.write:
        (ROOT / EXAMPLE).write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {EXAMPLE}")
        return 0

    observed = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, observed)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(observed)
    if sem:
        fail("semantic schema refactor backlog errors:\n- " + "\n- ".join(sem[:30]))
    require_generated_artifact_id_consistency(observed, {"backlog_id"})
    if observed != expected:
        print("schema refactor backlog is stale; regenerate with:", file=sys.stderr)
        print("  python3 tools/check_cube_schema_refactor_backlog.py --write", file=sys.stderr)
        raise SystemExit(1)
    require_docs()
    print("cube schema refactor backlog check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

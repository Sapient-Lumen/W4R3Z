#!/usr/bin/env python3
"""Replay r522 removable-media post-detach lifecycle scenarios.

r521 made the post-detach lane runtime-shaped.  r522 adds a small executable
scenario model so the cube checks end-to-end behavior instead of only validating
individual receipts.  The replay model is intentionally compact, but it catches
semantic regressions that JSON Schema cannot express: expired roots must deny,
missing expiry proof must fail closed, stale/rollback roots must not export,
degraded time must deny, fresh authority must recover only through a successor
root, and idempotent replays must not double-debit rate limits.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r522"
SCHEMA = "spec/removable.media.local.post_detach.scenario.replay.manifest.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-scenario-replay-manifest"

BINDING_PATHS = {
    "state_machine_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.state_machine.manifest.json",
    "enforcement_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json",
    "fresh_authority_recovery_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
    "backend_evidence_computed_digest": "spec/examples/removable.media.local.post_detach.backend.enforcement.evidence.json",
}

EXPECTED_SCENARIOS = {
    "expired-root-denied-with-enforcement-ledger",
    "missing-expiry-receipt-fails-closed",
    "rollback-or-stale-root-is-rejected",
    "degraded-time-proof-fails-closed",
    "fresh-authority-recovers-to-successor-root-only",
    "same-idempotency-key-replays-same-denial-without-double-debit",
}

EXPECTED_INVALIDS = [
    "degraded-time-success.json",
    "expired-root-observation-allowed.json",
    "idempotent-replay-double-debits.json",
    "missing-expiry-not-fail-closed.json",
    "model-binding-symbolic-not-computed.json",
    "recovery-resurrects-expired-root.json",
    "stale-root-export-allowed.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "scenario-replay", "tools/check_removable_media_local_post_detach_scenario_replay.py"],
    "README.md": [VERSION, "scenario-replay", "cube-schema-audit"],
    "docs/00-index.md": [VERSION, "docs/777-removable-media-local-fallback-post-detach-scenario-replay-and-cube-schema-audit.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_scenario_replay.py", "check_cube_schema_audit_report.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_scenario_replay.py", "check_cube_schema_audit_report.py"],
    "docs/110-juicy-os-lessons.md": ["r522 removable-media post-detach scenario replay", "cube-schema-audit"],
    "docs/777-removable-media-local-fallback-post-detach-scenario-replay-and-cube-schema-audit.md": [
        "removable.media.local.post_detach.scenario.replay.manifest",
        "cube.schema.audit.report",
        "tools/cube_digest_lib.py",
    ],
    "docs/current/removable-media-post-detach-scenario-replay.md": [
        "expired-root-denied-with-enforcement-ledger",
        "same-idempotency-key-replays-same-denial-without-double-debit",
    ],
    "docs/current/cube-schema-audit.md": ["fixture-literal", "runtime-contract", "cube.schema.audit.report"],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require_valid() -> dict[str, Any]:
    obj = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, obj)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    return obj


def deny_outcome_ok(outcome: dict[str, Any]) -> bool:
    return (
        outcome["allow_new_observation"] is False
        and outcome["allow_export"] is False
        and outcome["allow_rehydration"] is False
        and outcome["expired_root_observation_allowed"] is False
    )


def scenario_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if obj.get("generated_for_version") != VERSION:
        errors.append("scenario replay manifest version mismatch")
    lane = obj.get("lane", {})
    if lane.get("family") != "removable-media-local-fallback" or lane.get("phase") != "post-detach":
        errors.append("lane must remain removable-media-local-fallback/post-detach")

    bindings = obj.get("model_bindings", {})
    for key, rel in BINDING_PATHS.items():
        expected = file_json_digest(ROOT, rel)
        if bindings.get(key) != expected:
            errors.append(f"model binding {key} {bindings.get(key)!r} != computed digest {expected}")
    if bindings.get("canonical_digest_rule") != "json-sort-keys-compact-utf8-sha256":
        errors.append("canonical digest rule mismatch")

    scenarios = obj.get("scenarios", [])
    ids = {s.get("scenario_id") for s in scenarios}
    if ids != EXPECTED_SCENARIOS:
        errors.append(f"scenario ids mismatch: {sorted(ids)} != {sorted(EXPECTED_SCENARIOS)}")
    if len(ids) != len(scenarios):
        errors.append("scenario ids must be unique")

    by_id = {s.get("scenario_id"): s for s in scenarios}

    def out(sid: str) -> dict[str, Any]:
        return by_id[sid]["expected_outcome"]

    # Negative paths: nothing may observe/export/rehydrate an expired, missing-proof,
    # stale, rollback, or degraded-time root.
    for sid in [
        "expired-root-denied-with-enforcement-ledger",
        "missing-expiry-receipt-fails-closed",
        "rollback-or-stale-root-is-rejected",
        "degraded-time-proof-fails-closed",
        "same-idempotency-key-replays-same-denial-without-double-debit",
    ]:
        if sid not in by_id:
            continue
        if not deny_outcome_ok(out(sid)):
            errors.append(f"{sid}: denial/fail-closed outcome allowed observation/export/rehydration")
        if by_id[sid]["support_visibility"] != "support-safe-digest-only":
            errors.append(f"{sid}: support visibility must stay digest-only")

    # Specific failure classes.
    missing = out("missing-expiry-receipt-fails-closed") if "missing-expiry-receipt-fails-closed" in by_id else {}
    if missing and (missing["terminal_state"] != "fail-closed-typed-denial" or missing["denial_reason_code"] != "missing-expiry-receipt"):
        errors.append("missing-expiry scenario must fail closed with missing-expiry-receipt denial")

    stale = out("rollback-or-stale-root-is-rejected") if "rollback-or-stale-root-is-rejected" in by_id else {}
    if stale and stale["denial_reason_code"] not in {"stale-root", "rollback-root", "forked-root"}:
        errors.append("rollback/stale scenario must carry a stale/rollback/forked denial reason")

    degraded = out("degraded-time-proof-fails-closed") if "degraded-time-proof-fails-closed" in by_id else {}
    if degraded and (degraded["terminal_state"] != "fail-closed-typed-denial" or degraded["denial_reason_code"] != "degraded-clock"):
        errors.append("degraded-time scenario must fail closed with degraded-clock denial")

    recovery = out("fresh-authority-recovers-to-successor-root-only") if "fresh-authority-recovers-to-successor-root-only" in by_id else {}
    if recovery:
        if recovery["terminal_state"] != "successor-root-admitted":
            errors.append("fresh-authority recovery must end in successor-root-admitted")
        if recovery["successor_root_only"] is not True:
            errors.append("fresh-authority recovery must be successor-root-only")
        if recovery["expired_root_observation_allowed"] is not False:
            errors.append("fresh-authority recovery must not resurrect the expired root")
        if recovery["fresh_authority_required"] is not False or recovery["denial_reason_code"] != "none-successor-authority":
            errors.append("fresh-authority recovery should clear the denial reason after successor admission")

    replay = out("same-idempotency-key-replays-same-denial-without-double-debit") if "same-idempotency-key-replays-same-denial-without-double-debit" in by_id else {}
    if replay:
        if replay["terminal_state"] != "idempotent-denial-replayed":
            errors.append("idempotent replay must replay the denial outcome")
        if replay["rate_limit_debited"] is not False or replay["double_debit_prevented"] is not True:
            errors.append("idempotent replay must not double-debit rate limits")

    # Receipt typing: every scenario must name at least one concrete dotted kind.
    for s in scenarios:
        kinds = s.get("required_receipt_kinds", [])
        if not kinds or any("." not in k for k in kinds):
            errors.append(f"{s.get('scenario_id')}: required receipts must be dotted kind names")

    inv = obj.get("invariants", {})
    for key in [
        "expired_root_never_observed_after_expiry",
        "missing_expiry_receipt_fails_closed",
        "rollback_fork_or_stale_root_rejected",
        "degraded_time_fails_closed",
        "fresh_authority_recovery_is_successor_only",
        "idempotent_replay_does_not_double_debit",
        "scenario_receipts_are_typed",
        "model_bindings_are_computed",
    ]:
        if inv.get(key) is not True:
            errors.append(f"invariant {key} must be true")

    return errors


def require_invalids_fail() -> None:
    root = ROOT / INVALID_DIR
    names = sorted(p.name for p in root.glob("*.json"))
    if names != EXPECTED_INVALIDS:
        fail(f"invalid fixture set mismatch: {names} != {EXPECTED_INVALIDS}")
    for path in sorted(root.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        schema_errs = validation_errors(SCHEMA, obj)
        semantic_errs: list[str] = []
        if not schema_errs:
            semantic_errs = scenario_errors(obj)
        if not schema_errs and not semantic_errs:
            fail(f"invalid fixture unexpectedly passed schema+semantic checks: {path.relative_to(ROOT)}")


def require_text_tokens() -> None:
    for rel, tokens in REQUIRED_DOC_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required doc/surface: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing required r522 token {token!r}")


def require_hygiene_wiring() -> None:
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8")
    for checker in [
        "check_removable_media_local_post_detach_scenario_replay.py",
        "check_cube_schema_audit_report.py",
    ]:
        if checker not in hygiene:
            fail(f"tools/hygiene.py missing {checker}")


def main() -> int:
    obj = require_valid()
    errs = scenario_errors(obj)
    if errs:
        fail("scenario replay semantic check failed: " + "; ".join(errs))
    require_invalids_fail()
    require_hygiene_wiring()
    require_text_tokens()
    print("removable-media post-detach scenario replay check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

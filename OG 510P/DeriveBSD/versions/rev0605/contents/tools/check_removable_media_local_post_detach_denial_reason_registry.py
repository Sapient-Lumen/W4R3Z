#!/usr/bin/env python3
"""Validate r524 post-detach denial reason precedence registry.

r523 made post-detach replay reviewable as ordered transition witnesses.  r524
adds the missing decision-selection layer: denial reason codes and precedence are
now a typed registry instead of being scattered across the old tombstone denial,
r521 enforcement ledger, r522 scenario replay, and r523 witness transcript.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r524"
SCHEMA = "spec/removable.media.local.post_detach.denial.reason.registry.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.denial.reason.registry.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-denial-reason-registry"

SOURCE_BINDINGS = {
    "state_machine_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.state_machine.manifest.json",
    "scenario_replay_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json",
    "transition_witness_capsule_computed_digest": "spec/examples/removable.media.local.post_detach.transition.witness.capsule.json",
    "enforcement_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json",
    "fresh_authority_recovery_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.json",
    "legacy_denial_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.receipt.json",
}

EXPECTED_INVALIDS = [
    "duplicate-rank.json",
    "missing-expired-ledger-code.json",
    "raw-support-code-allows-raw.json",
    "scenario-code-drift.json",
    "stale-source-binding.json",
    "subordinate-preempts-primary.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "denial.reason.registry", "check_removable_media_local_post_detach_denial_reason_registry.py"],
    "README.md": [VERSION, "denial-reason-registry", "schema-refactor-backlog"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-denial-reason-registry.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_denial_reason_registry.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_denial_reason_registry.py"],
    "docs/110-juicy-os-lessons.md": ["r524 removable-media post-detach denial reason registry"],
    "docs/779-removable-media-local-fallback-post-detach-denial-reason-registry-and-schema-refactor-backlog.md": [
        "removable.media.local.post_detach.denial.reason.registry",
        "cube.schema.refactor.backlog",
        "denial-reason-registry-positive-and-negative-fixture-guarded",
    ],
    "docs/current/removable-media-post-detach-denial-reason-registry.md": [
        "expired-ledger-root-fresh-authority-required",
        "lower-rank-wins",
        "support-safe-digest-only",
    ],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def build_registry() -> dict[str, Any]:
    scenario = load_json(ROOT, "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json")
    witness = load_json(ROOT, "spec/examples/removable.media.local.post_detach.transition.witness.capsule.json")
    trace_by_scenario = {trace["scenario_id"]: trace for trace in witness["traces"]}

    reason_rows = [
        {
            "reason_code": "raw-support-visibility",
            "rank": 5,
            "reason_class": "sanitization-failure",
            "terminal_states": ["fail-closed-typed-denial"],
            "fresh_authority_required": True,
            "deny_actions": ["observe", "export", "rehydrate", "raw-support"],
            "rate_limit_action": "debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "Any raw support/debug visibility wins before ordinary denial projection is released.",
        },
        {
            "reason_code": "tombstone-visible",
            "rank": 10,
            "reason_class": "primary-denial",
            "terminal_states": ["denied-stale-authority"],
            "fresh_authority_required": True,
            "deny_actions": ["query", "export", "rehydrate"],
            "rate_limit_action": "debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "The original r510 tombstone denial remains the legacy stale-authority cause.",
        },
        {
            "reason_code": "expired-ledger-root-fresh-authority-required",
            "rank": 20,
            "reason_class": "primary-denial",
            "terminal_states": ["expired-root-denied", "idempotent-denial-replayed"],
            "fresh_authority_required": True,
            "deny_actions": ["observe", "export", "rehydrate"],
            "rate_limit_action": "debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": ["missing-fresh-authority", "stale-root"],
            "summary": "An expired compacted reader-use ledger root requires fresh authority and cannot be observed directly.",
        },
        {
            "reason_code": "stale-root",
            "rank": 30,
            "reason_class": "primary-denial",
            "terminal_states": ["fail-closed-stale-root-denial", "fail-closed-typed-denial"],
            "fresh_authority_required": True,
            "deny_actions": ["observe", "export", "rehydrate"],
            "rate_limit_action": "debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "A rollback, fork, or stale attempted root is denied before any expired-root recovery succeeds.",
        },
        {
            "reason_code": "missing-expiry-receipt",
            "rank": 40,
            "reason_class": "primary-denial",
            "terminal_states": ["fail-closed-missing-expiry-denial", "fail-closed-typed-denial"],
            "fresh_authority_required": True,
            "deny_actions": ["observe", "export", "rehydrate"],
            "rate_limit_action": "debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "A missing expiry receipt fails closed instead of guessing that the old root is live.",
        },
        {
            "reason_code": "degraded-clock",
            "rank": 50,
            "reason_class": "primary-denial",
            "terminal_states": ["fail-closed-degraded-time-denial", "fail-closed-typed-denial"],
            "fresh_authority_required": True,
            "deny_actions": ["observe", "export", "rehydrate"],
            "rate_limit_action": "debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "A degraded, unavailable, or skewed time proof fails closed with a typed denial.",
        },
        {
            "reason_code": "missing-fresh-authority",
            "rank": 70,
            "reason_class": "subordinate-denial",
            "terminal_states": ["expired-root-denied", "fail-closed-typed-denial"],
            "fresh_authority_required": True,
            "deny_actions": ["observe", "export", "rehydrate"],
            "rate_limit_action": "not-applicable",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "Fresh authority absence is recorded under the primary expiry or tombstone cause.",
        },
        {
            "reason_code": "rate-limit-replayed-no-new-debit",
            "rank": 80,
            "reason_class": "idempotent-replay",
            "terminal_states": ["idempotent-denial-replayed"],
            "fresh_authority_required": True,
            "deny_actions": ["observe", "export", "rehydrate"],
            "rate_limit_action": "replayed-no-new-debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "The same idempotency key replays the prior expiry denial without a second rate-limit debit.",
        },
        {
            "reason_code": "none-successor-authority",
            "rank": 900,
            "reason_class": "successor-success",
            "terminal_states": ["successor-root-admitted"],
            "fresh_authority_required": False,
            "deny_actions": [],
            "rate_limit_action": "no-debit",
            "support_visibility": "support-safe-digest-only",
            "subordinate_reason_codes": [],
            "summary": "Fresh authority was consumed and a successor root, not the expired root, was admitted.",
        },
    ]

    # Scenario bindings are generated from r522/r523 so the registry cannot drift
    # from the replay and witness surfaces.
    scenario_bindings = []
    for s in scenario["scenarios"]:
        expected = s["expected_outcome"]
        trace = trace_by_scenario[s["scenario_id"]]
        reason_code = expected["denial_reason_code"]
        rank = next(row["rank"] for row in reason_rows if row["reason_code"] == reason_code)
        if s["scenario_id"] == "same-idempotency-key-replays-same-denial-without-double-debit":
            # The primary denial cause is unchanged, but the rate-limit action is
            # replay-specific and must be visible in the binding.
            rate_limit_action = "replayed-no-new-debit"
        elif expected["rate_limit_debited"]:
            rate_limit_action = "debit"
        else:
            rate_limit_action = "no-debit"
        scenario_bindings.append({
            "scenario_id": s["scenario_id"],
            "terminal_state": expected["terminal_state"],
            "primary_reason_code": reason_code,
            "expected_rank": rank,
            "fresh_authority_required": expected["fresh_authority_required"],
            "allow_observe": expected["allow_new_observation"],
            "allow_export": expected["allow_export"],
            "allow_rehydrate": expected["allow_rehydration"],
            "rate_limit_action": rate_limit_action,
            "witness_trace_id": trace["trace_id"],
        })

    return {
        "kind": "removable.media.local.post_detach.denial.reason.registry",
        "schema_version": "1.0",
        "registry_id": "rm-postdetach-denial-reason-registry-20260530-r524",
        "generated_for_version": VERSION,
        "lane": {
            "family": "removable-media-local-fallback",
            "phase": "post-detach",
            "identity_policy": "family-normalized-phase-by-kind",
        },
        "source_bindings": {
            "canonical_digest_rule": "json-sort-keys-compact-utf8-sha256",
            **{key: file_json_digest(ROOT, rel) for key, rel in SOURCE_BINDINGS.items()},
        },
        "precedence_policy": {
            "rank_order": "lower-rank-wins",
            "primary_reason_must_be_registry_member": True,
            "subordinate_reasons_must_not_preempt_primary": True,
            "successor_recovery_is_not_a_denial": True,
            "support_projection_after_denial_is_digest_only": True,
        },
        "reason_precedence": reason_rows,
        "scenario_bindings": scenario_bindings,
        "invariants": {
            "ranks_are_unique": True,
            "scenario_reason_codes_are_registry_members": True,
            "enforcement_denial_code_is_registry_member": True,
            "fresh_recovery_prior_denial_code_is_registry_member": True,
            "support_visibility_is_digest_only": True,
            "successor_authority_does_not_resurrect_expired_root": True,
        },
        "negative_fixture_policy": "known-bad-post-detach-denial-reason-registry-shapes-must-fail-validation",
    }


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("registry version mismatch")
    lane = obj.get("lane", {})
    if lane.get("family") != "removable-media-local-fallback" or lane.get("phase") != "post-detach":
        errors.append("lane must remain removable-media-local-fallback/post-detach")

    bindings = obj.get("source_bindings", {})
    if bindings.get("canonical_digest_rule") != "json-sort-keys-compact-utf8-sha256":
        errors.append("canonical digest rule mismatch")
    for key, rel in SOURCE_BINDINGS.items():
        expected = file_json_digest(ROOT, rel)
        if bindings.get(key) != expected:
            errors.append(f"source binding {key} {bindings.get(key)!r} != computed digest {expected}")

    reasons = obj.get("reason_precedence", [])
    code_to_reason = {row.get("reason_code"): row for row in reasons}
    if len(code_to_reason) != len(reasons):
        errors.append("reason codes must be unique")
    ranks = [row.get("rank") for row in reasons]
    if len(set(ranks)) != len(ranks):
        errors.append("reason ranks must be unique")
    if ranks != sorted(ranks):
        errors.append("reason_precedence must be sorted by ascending rank")
    for row in reasons:
        if row.get("support_visibility") != "support-safe-digest-only":
            errors.append(f"{row.get('reason_code')}: support visibility must remain digest-only")
        if row.get("reason_class") == "subordinate-denial":
            # Subordinate reasons may be listed, but they must not outrank the
            # primary expiry reason that names them.
            if row.get("rank", 1000) < code_to_reason.get("expired-ledger-root-fresh-authority-required", {}).get("rank", -1):
                errors.append(f"{row.get('reason_code')}: subordinate reason outranks primary expiry reason")
        for sub in row.get("subordinate_reason_codes", []):
            if sub not in code_to_reason:
                errors.append(f"{row.get('reason_code')}: unknown subordinate reason {sub}")
            elif code_to_reason[sub].get("rank", -1) <= row.get("rank", 1000):
                errors.append(f"{row.get('reason_code')}: subordinate reason {sub} must not preempt primary rank")

    scenario = load_json(ROOT, "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json")
    witness = load_json(ROOT, "spec/examples/removable.media.local.post_detach.transition.witness.capsule.json")
    trace_by_scenario = {trace["scenario_id"]: trace for trace in witness["traces"]}
    binding_by_scenario = {b.get("scenario_id"): b for b in obj.get("scenario_bindings", [])}
    if set(binding_by_scenario) != {s["scenario_id"] for s in scenario["scenarios"]}:
        errors.append("scenario bindings must exactly cover scenario replay manifest")
    for s in scenario["scenarios"]:
        sid = s["scenario_id"]
        expected = s["expected_outcome"]
        b = binding_by_scenario.get(sid)
        if not b:
            continue
        code = expected["denial_reason_code"]
        if b.get("primary_reason_code") != code:
            errors.append(f"{sid}: primary reason code drifted from scenario replay")
        if code not in code_to_reason:
            errors.append(f"{sid}: scenario reason code {code} is not in registry")
            continue
        if b.get("expected_rank") != code_to_reason[code].get("rank"):
            errors.append(f"{sid}: expected rank does not match registry")
        if b.get("terminal_state") != expected.get("terminal_state"):
            errors.append(f"{sid}: terminal state drifted from scenario replay")
        if b.get("fresh_authority_required") != expected.get("fresh_authority_required"):
            errors.append(f"{sid}: fresh_authority_required drifted from scenario replay")
        if b.get("allow_observe") != expected.get("allow_new_observation"):
            errors.append(f"{sid}: observe permission drifted from scenario replay")
        if b.get("allow_export") != expected.get("allow_export"):
            errors.append(f"{sid}: export permission drifted from scenario replay")
        if b.get("allow_rehydrate") != expected.get("allow_rehydration"):
            errors.append(f"{sid}: rehydrate permission drifted from scenario replay")
        trace = trace_by_scenario.get(sid)
        if trace and b.get("witness_trace_id") != trace.get("trace_id"):
            errors.append(f"{sid}: witness trace id drifted")
        if trace and trace.get("support_visibility") != "support-safe-digest-only":
            errors.append(f"{sid}: witness support visibility is not digest-only")
        if code_to_reason[code].get("reason_class") == "successor-success":
            if expected.get("expired_root_observation_allowed") is not False or expected.get("successor_root_only") is not True:
                errors.append(f"{sid}: successor success must stay successor-root-only")
        elif expected.get("allow_new_observation") or expected.get("allow_export") or expected.get("allow_rehydration"):
            errors.append(f"{sid}: denial reason cannot allow observe/export/rehydrate")

    enforcement = load_json(ROOT, "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json")
    denial_binding = enforcement.get("denial_binding", {})
    code = denial_binding.get("denial_reason_code")
    if code not in code_to_reason:
        errors.append("enforcement ledger denial reason is not in registry")
    for sub in denial_binding.get("subordinate_reason_codes", []):
        if sub not in code_to_reason:
            errors.append(f"enforcement ledger subordinate reason {sub} is not in registry")
    if code in code_to_reason and denial_binding.get("denial_precedence_rank") != code_to_reason[code].get("rank"):
        errors.append("enforcement ledger denial_precedence_rank drifted from registry")

    recovery = load_json(ROOT, "spec/examples/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.json")
    recovery_code = recovery.get("prior_denial_binding", {}).get("denial_reason_code")
    if recovery_code not in code_to_reason:
        errors.append("fresh-authority recovery prior denial reason is not in registry")
    if recovery.get("successor_binding", {}).get("expired_root_resurrected") is not False:
        errors.append("fresh-authority recovery must not resurrect expired root")

    invariants = obj.get("invariants", {})
    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


def invalid_objects(obj: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}

    dup = copy.deepcopy(obj)
    dup["reason_precedence"][1]["rank"] = dup["reason_precedence"][2]["rank"]
    out["duplicate-rank.json"] = dup

    missing = copy.deepcopy(obj)
    missing["reason_precedence"] = [r for r in missing["reason_precedence"] if r["reason_code"] != "expired-ledger-root-fresh-authority-required"]
    out["missing-expired-ledger-code.json"] = missing

    raw = copy.deepcopy(obj)
    raw["reason_precedence"][0]["support_visibility"] = "raw-support-visible"
    out["raw-support-code-allows-raw.json"] = raw

    drift = copy.deepcopy(obj)
    drift["scenario_bindings"][0]["primary_reason_code"] = "stale-root"
    out["scenario-code-drift.json"] = drift

    stale = copy.deepcopy(obj)
    stale["source_bindings"]["transition_witness_capsule_computed_digest"] = "sha256:" + "00" * 32
    out["stale-source-binding.json"] = stale

    sub = copy.deepcopy(obj)
    for row in sub["reason_precedence"]:
        if row["reason_code"] == "missing-fresh-authority":
            row["rank"] = 1
    sub["reason_precedence"].sort(key=lambda r: r["rank"])
    out["subordinate-preempts-primary.json"] = sub

    return out


def require_docs() -> None:
    for rel, tokens in REQUIRED_DOC_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required doc surface: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing required token {token!r}")
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8", errors="replace")
    if "check_removable_media_local_post_detach_denial_reason_registry.py" not in hygiene:
        fail("tools/hygiene.py missing denial reason registry checker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write positive and invalid fixtures")
    args = ap.parse_args()

    expected = build_registry()
    if args.write:
        (ROOT / EXAMPLE).write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        invalid_dir = ROOT / INVALID_DIR
        invalid_dir.mkdir(parents=True, exist_ok=True)
        for name, data in invalid_objects(expected).items():
            (invalid_dir / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {EXAMPLE} and {len(EXPECTED_INVALIDS)} invalid fixtures")
        return 0

    observed = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, observed)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(observed)
    if sem:
        fail("semantic denial reason registry errors:\n- " + "\n- ".join(sem[:30]))
    if observed != expected:
        print("denial reason registry is stale; regenerate with:", file=sys.stderr)
        print("  python3 tools/check_removable_media_local_post_detach_denial_reason_registry.py --write", file=sys.stderr)
        raise SystemExit(1)

    invalid_dir = ROOT / INVALID_DIR
    found = sorted(p.name for p in invalid_dir.glob("*.json"))
    if found != EXPECTED_INVALIDS:
        fail(f"invalid fixture set mismatch: {found} != {EXPECTED_INVALIDS}")
    for path in sorted(invalid_dir.glob("*.json")):
        bad = load_json(ROOT, f"{INVALID_DIR}/{path.name}")
        schema_errs = validation_errors(SCHEMA, bad)
        semantic_errs = semantic_errors(bad) if not schema_errs else []
        if not schema_errs and not semantic_errs:
            fail(f"invalid fixture unexpectedly passed: {path.name}")

    require_docs()
    print("removable-media post-detach denial reason registry check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate r526 post-detach rate-limit debit ledger receipts.

r525 proved that an expired-root denial selection chooses a rate-limit action.
r526 gives that action its own ledger receipt: the debit subject, policy, window,
CAS roots, idempotency key, replay/no-double-debit behavior, and support-safe
retry projection are checked as a typed artifact instead of remaining only as a
loose digest embedded in the enforcement ledger.
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
VERSION = "2026-05-30r526"
SCHEMA = "spec/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-rate-limit-debit-ledger-receipt"

SOURCE_BINDINGS = {
    "enforcement_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json",
    "denial_selection_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json",
    "denial_reason_registry_computed_digest": "spec/examples/removable.media.local.post_detach.denial.reason.registry.json",
    "scenario_replay_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json",
    "transition_witness_capsule_computed_digest": "spec/examples/removable.media.local.post_detach.transition.witness.capsule.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
}

EXPECTED_INVALIDS = [
    "cas-expected-mismatch.json",
    "double-debit-on-idempotent-replay.json",
    "ledger-root-not-advanced.json",
    "missing-debit.json",
    "policy-digest-drift.json",
    "stale-denial-selection-binding.json",
    "support-budget-visible.json",
    "unbounded-retry-window.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "rate_limit.debit.ledger.receipt", "check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py"],
    "README.md": [VERSION, "rate-limit-debit-ledger", "reader-use-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-rate-limit-debit-ledger.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r526 removable-media post-detach rate-limit debit ledger"],
    "docs/781-removable-media-local-fallback-post-detach-rate-limit-debit-ledger-and-reader-use-schema-split.md": [
        "removable.media.local.post_detach.rate_limit.debit.ledger.receipt",
        "post-detach-rate-limit-debit-ledger-positive-and-negative-fixture-guarded",
        "post-detach-reader-use-generic-runtime-schema-plus-exact-fixture-split",
    ],
    "docs/current/removable-media-post-detach-rate-limit-debit-ledger.md": [
        "idempotent replay",
        "double debit",
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


def scenario_by_id(scenario_id: str) -> dict[str, Any]:
    manifest = load_json(ROOT, "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json")
    for row in manifest["scenarios"]:
        if row["scenario_id"] == scenario_id:
            return row
    raise AssertionError(f"missing scenario {scenario_id}")


def build_receipt() -> dict[str, Any]:
    enforcement = load_json(ROOT, "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json")
    selection = load_json(ROOT, "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json")
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")
    rate = enforcement["rate_limit_binding"]
    first_scenario = scenario_by_id("expired-root-denied-with-enforcement-ledger")
    replay_scenario = scenario_by_id("same-idempotency-key-replays-same-denial-without-double-debit")

    return {
        "kind": "removable.media.local.post_detach.rate_limit.debit.ledger.receipt",
        "schema_version": "1.0",
        "debit_receipt_id": "rm-postdetach-rate-limit-debit-20260530-r526",
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
        "debit_subject": {
            "rate_limit_subject_digest": rate["rate_limit_subject_digest"],
            "attempted_action": selection["attempted_action"],
            "selected_reason_code": selection["selected_reason"]["reason_code"],
            "selected_reason_rank": selection["selected_reason"]["rank"],
            "denial_selection_receipt_id": selection["selection_receipt_id"],
            "selected_rate_limit_action": selection["selected_reason"]["rate_limit_action"],
            "denial_selection_debit_receipt_digest": selection["rate_limit_binding"]["debit_receipt_digest"],
        },
        "ledger_cas": {
            "prior_root_digest": rate["rate_limit_ledger_prior_root_digest"],
            "expected_root_digest": rate["rate_limit_ledger_prior_root_digest"],
            "new_root_digest": rate["rate_limit_ledger_new_root_digest"],
            "ledger_anchor_digest": "sha256:7a1af10d67a7ee7a1b820c319781e344fbd6fb41c318f2dd89ce43b267733dc4",
            "debit_sequence": 50,
            "broker_epoch_id": enforcement["enforcement_root_cas"]["broker_epoch_id"],
            "compare_and_swap_result": "committed",
            "replay_outcome": "first-debit",
            "rollback_accepted": False,
            "forked_root_accepted": False,
            "stale_root_accepted": False,
        },
        "debit_accounting": {
            "rate_limit_policy_digest": rate["rate_limit_policy_digest"],
            "rate_limit_window_id": rate["rate_limit_window_id"],
            "debit_amount": rate["debit_amount"],
            "debit_units": "post-expiry-denial-attempt",
            "remaining_budget_class": rate["remaining_budget_class"],
            "idempotency_key_digest": rate["idempotency_key_digest"],
            "debit_before_support_projection": True,
            "double_debit_allowed": False,
            "idempotent_replay_debit_amount": 0,
            "idempotent_replay_returns_same_denial": True,
            "rate_limit_not_debited_policy": "fail-closed-with-typed-denial",
        },
        "scenario_binding": {
            "first_attempt_scenario_id": first_scenario["scenario_id"],
            "first_attempt_terminal_state": first_scenario["expected_outcome"]["terminal_state"],
            "first_attempt_rate_limit_debited": first_scenario["expected_outcome"]["rate_limit_debited"],
            "replay_scenario_id": replay_scenario["scenario_id"],
            "replay_terminal_state": replay_scenario["expected_outcome"]["terminal_state"],
            "replay_rate_limit_debited": replay_scenario["expected_outcome"]["rate_limit_debited"],
            "replay_double_debit_prevented": replay_scenario["expected_outcome"]["double_debit_prevented"],
        },
        "retry_guidance": {
            "retry_after_not_before": rate["retry_after_not_before"],
            "retry_window_policy": "bounded-redacted-retry-window",
            "unbounded_retry_window": False,
            "fresh_authority_required": True,
            "fresh_authority_instruction_visible": support["retry_guidance"]["fresh_authority_instruction_visible"],
        },
        "support_projection": {
            "visibility": support["visibility"],
            "visible_reason_code": support["reason_code"],
            "budget_counts_visible": False,
            "ledger_roots_visible": False,
            "raw_subject_visible": False,
            "raw_idempotency_key_visible": False,
        },
        "joins": {
            "enforcement_symbolic_debit_receipt_digest": rate["rate_limit_debit_receipt_digest"],
            "selection_symbolic_debit_receipt_digest": selection["rate_limit_binding"]["debit_receipt_digest"],
            "enforcement_and_selection_symbolic_digest_match": True,
            "rate_limit_policy_matches_enforcement": True,
            "idempotency_key_matches_enforcement": True,
            "ledger_roots_match_enforcement": True,
        },
        "invariants": {
            "first_attempt_debits_once": True,
            "idempotent_replay_debits_zero": True,
            "ledger_root_advances_once": True,
            "cas_expected_equals_prior": True,
            "support_projection_is_digest_only": True,
            "retry_window_is_bounded": True,
        },
        "negative_fixture_policy": "known-bad-post-detach-rate-limit-debit-ledger-shapes-must-fail-validation",
    }


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("rate-limit debit receipt version mismatch")
    lane = obj.get("lane", {})
    if lane.get("family") != "removable-media-local-fallback" or lane.get("phase") != "post-detach":
        errors.append("lane must remain removable-media-local-fallback/post-detach")

    bindings = obj.get("source_bindings", {})
    if bindings.get("canonical_digest_rule") != "json-sort-keys-compact-utf8-sha256":
        errors.append("canonical digest rule mismatch")
    for key, rel in SOURCE_BINDINGS.items():
        if bindings.get(key) != file_json_digest(ROOT, rel):
            errors.append(f"source binding {key} is stale")

    enforcement = load_json(ROOT, "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json")
    selection = load_json(ROOT, "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json")
    rate = enforcement["rate_limit_binding"]
    subject = obj.get("debit_subject", {})
    acct = obj.get("debit_accounting", {})
    cas = obj.get("ledger_cas", {})
    joins = obj.get("joins", {})

    if subject.get("rate_limit_subject_digest") != rate["rate_limit_subject_digest"]:
        errors.append("rate-limit subject digest drifted from enforcement ledger")
    if subject.get("selected_reason_code") != selection["selected_reason"]["reason_code"]:
        errors.append("selected reason drifted from denial selection")
    if subject.get("selected_rate_limit_action") != "debit":
        errors.append("selected rate-limit action must be debit for the first expired-root denial")
    if subject.get("denial_selection_debit_receipt_digest") != rate["rate_limit_debit_receipt_digest"]:
        errors.append("selection and enforcement debit receipt digests must match")

    if acct.get("rate_limit_policy_digest") != rate["rate_limit_policy_digest"]:
        errors.append("rate-limit policy digest drifted from enforcement ledger")
    if acct.get("rate_limit_window_id") != rate["rate_limit_window_id"]:
        errors.append("rate-limit window id drifted from enforcement ledger")
    if acct.get("debit_amount") != 1:
        errors.append("first expired-root denial must debit exactly one unit")
    if acct.get("idempotency_key_digest") != rate["idempotency_key_digest"]:
        errors.append("idempotency key digest drifted from enforcement ledger")
    if acct.get("double_debit_allowed") is not False:
        errors.append("double debit must remain forbidden")
    if acct.get("idempotent_replay_debit_amount") != 0:
        errors.append("idempotent replay must not debit again")
    if acct.get("idempotent_replay_returns_same_denial") is not True:
        errors.append("idempotent replay must return the same denial")

    if cas.get("expected_root_digest") != cas.get("prior_root_digest"):
        errors.append("rate-limit CAS expected root must equal prior root")
    if cas.get("new_root_digest") == cas.get("prior_root_digest"):
        errors.append("rate-limit ledger root must advance")
    for key in ["rollback_accepted", "forked_root_accepted", "stale_root_accepted"]:
        if cas.get(key) is not False:
            errors.append(f"{key} must remain false")
    if cas.get("prior_root_digest") != rate["rate_limit_ledger_prior_root_digest"] or cas.get("new_root_digest") != rate["rate_limit_ledger_new_root_digest"]:
        errors.append("rate-limit ledger roots drifted from enforcement ledger")

    first = scenario_by_id("expired-root-denied-with-enforcement-ledger")["expected_outcome"]
    replay = scenario_by_id("same-idempotency-key-replays-same-denial-without-double-debit")["expected_outcome"]
    scen = obj.get("scenario_binding", {})
    if scen.get("first_attempt_rate_limit_debited") != first["rate_limit_debited"] or first["rate_limit_debited"] is not True:
        errors.append("first-attempt scenario must debit")
    if scen.get("replay_rate_limit_debited") != replay["rate_limit_debited"] or replay["rate_limit_debited"] is not False:
        errors.append("replay scenario must not debit")
    if scen.get("replay_double_debit_prevented") != replay["double_debit_prevented"] or replay["double_debit_prevented"] is not True:
        errors.append("replay scenario must prevent double debit")

    retry = obj.get("retry_guidance", {})
    if retry.get("retry_window_policy") != "bounded-redacted-retry-window" or retry.get("unbounded_retry_window") is not False:
        errors.append("retry guidance must stay bounded and redacted")
    if retry.get("fresh_authority_required") is not True:
        errors.append("fresh authority must be required after expired-root denial")

    support = obj.get("support_projection", {})
    if support.get("visibility") != "support-safe-digest-only":
        errors.append("support projection must be digest-only")
    for key in ["budget_counts_visible", "ledger_roots_visible", "raw_subject_visible", "raw_idempotency_key_visible"]:
        if support.get(key) is not False:
            errors.append(f"support projection leaks {key}")

    if joins.get("enforcement_symbolic_debit_receipt_digest") != joins.get("selection_symbolic_debit_receipt_digest"):
        errors.append("symbolic debit receipt digests must match")
    for key in [
        "enforcement_and_selection_symbolic_digest_match",
        "rate_limit_policy_matches_enforcement",
        "idempotency_key_matches_enforcement",
        "ledger_roots_match_enforcement",
    ]:
        if joins.get(key) is not True:
            errors.append(f"join proof {key} must be true")
    for key, value in obj.get("invariants", {}).items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


def invalid_objects(obj: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}

    cas = copy.deepcopy(obj)
    cas["ledger_cas"]["expected_root_digest"] = "sha256:" + "00" * 32
    out["cas-expected-mismatch.json"] = cas

    replay = copy.deepcopy(obj)
    replay["debit_accounting"]["idempotent_replay_debit_amount"] = 1
    replay["debit_accounting"]["double_debit_allowed"] = True
    replay["invariants"]["idempotent_replay_debits_zero"] = False
    out["double-debit-on-idempotent-replay.json"] = replay

    root = copy.deepcopy(obj)
    root["ledger_cas"]["new_root_digest"] = root["ledger_cas"]["prior_root_digest"]
    out["ledger-root-not-advanced.json"] = root

    missing = copy.deepcopy(obj)
    missing["debit_accounting"]["debit_amount"] = 0
    out["missing-debit.json"] = missing

    policy = copy.deepcopy(obj)
    policy["debit_accounting"]["rate_limit_policy_digest"] = "sha256:" + "11" * 32
    out["policy-digest-drift.json"] = policy

    stale = copy.deepcopy(obj)
    stale["source_bindings"]["denial_selection_receipt_computed_digest"] = "sha256:" + "22" * 32
    out["stale-denial-selection-binding.json"] = stale

    support = copy.deepcopy(obj)
    support["support_projection"]["budget_counts_visible"] = True
    out["support-budget-visible.json"] = support

    retry = copy.deepcopy(obj)
    retry["retry_guidance"]["unbounded_retry_window"] = True
    retry["retry_guidance"]["retry_window_policy"] = "unbounded-retry-window"
    out["unbounded-retry-window.json"] = retry

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
    if "check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py" not in hygiene:
        fail("tools/hygiene.py missing rate-limit debit ledger checker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write positive and invalid fixtures")
    args = ap.parse_args()

    expected = build_receipt()
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
        fail("semantic rate-limit debit ledger errors:\n- " + "\n- ".join(sem[:40]))
    if observed != expected:
        print("rate-limit debit ledger receipt is stale; regenerate with:", file=sys.stderr)
        print("  python3 tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py --write", file=sys.stderr)
        raise SystemExit(1)

    invalid_dir = ROOT / INVALID_DIR
    observed_invalids = sorted(p.name for p in invalid_dir.glob("*.json"))
    if observed_invalids != EXPECTED_INVALIDS:
        fail(f"invalid fixture set mismatch: {observed_invalids} != {EXPECTED_INVALIDS}")
    for path in sorted(invalid_dir.glob("*.json")):
        obj = load_json(ROOT, path.relative_to(ROOT).as_posix())
        schema_errs = validation_errors(SCHEMA, obj)
        sem_errs = semantic_errors(obj) if not schema_errs else []
        if not schema_errs and not sem_errs:
            fail(f"invalid fixture unexpectedly passes schema+semantic validation: {path.relative_to(ROOT)}")

    require_docs()
    print("removable-media post-detach rate-limit debit ledger receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

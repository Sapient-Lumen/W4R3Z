#!/usr/bin/env python3
"""Validate r525 post-detach denial selection receipts.

r524 gave the post-detach lane a ranked denial reason registry.  r525 proves an
individual broker attempt used that registry correctly: observed predicates are
turned into candidate reasons, the lowest active non-subordinate rank is selected,
support/debug projection remains digest-only, and rate-limit behavior matches the
selected denial path.
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
VERSION = "2026-05-30r525"
SCHEMA = "spec/removable.media.local.post_detach.denial.selection.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-denial-selection-receipt"

SOURCE_BINDINGS = {
    "denial_reason_registry_computed_digest": "spec/examples/removable.media.local.post_detach.denial.reason.registry.json",
    "scenario_replay_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json",
    "transition_witness_capsule_computed_digest": "spec/examples/removable.media.local.post_detach.transition.witness.capsule.json",
    "enforcement_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
}

EXPECTED_INVALIDS = [
    "omitted-higher-precedence.json",
    "rate-limit-action-drift.json",
    "selected-subordinate-reason.json",
    "selected-unknown-reason.json",
    "stale-registry-binding.json",
    "support-raw-visibility.json",
    "witness-scenario-drift.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "denial.selection.receipt", "check_removable_media_local_post_detach_denial_selection_receipt.py"],
    "README.md": [VERSION, "denial-selection", "contract-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-denial-selection.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_denial_selection_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_denial_selection_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r525 removable-media post-detach denial selection"],
    "docs/780-removable-media-local-fallback-post-detach-denial-selection-and-contract-schema-split.md": [
        "removable.media.local.post_detach.denial.selection.receipt",
        "removable.media.local.post_detach.contract.fixture.schema.json",
        "denial-selection-receipt-positive-and-negative-fixture-guarded",
    ],
    "docs/current/removable-media-post-detach-denial-selection.md": [
        "lower-rank-wins",
        "expired-ledger-root-fresh-authority-required",
        "support-safe-digest-only",
    ],
}

ACTIVE_REASON_CODES = {
    "expired-ledger-root-fresh-authority-required",
    "stale-root",
    "missing-fresh-authority",
}
SCENARIO_ID = "expired-root-denied-with-enforcement-ledger"


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def registry_rows() -> dict[str, dict[str, Any]]:
    registry = load_json(ROOT, "spec/examples/removable.media.local.post_detach.denial.reason.registry.json")
    return {row["reason_code"]: row for row in registry["reason_precedence"]}


def scenario_binding() -> dict[str, Any]:
    registry = load_json(ROOT, "spec/examples/removable.media.local.post_detach.denial.reason.registry.json")
    for binding in registry["scenario_bindings"]:
        if binding["scenario_id"] == SCENARIO_ID:
            return binding
    raise AssertionError(f"missing scenario binding {SCENARIO_ID}")


def build_receipt() -> dict[str, Any]:
    rows = registry_rows()
    binding = scenario_binding()
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")
    enforcement = load_json(ROOT, "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json")

    candidate_order = [
        "raw-support-visibility",
        "tombstone-visible",
        "expired-ledger-root-fresh-authority-required",
        "stale-root",
        "missing-expiry-receipt",
        "degraded-clock",
        "missing-fresh-authority",
        "rate-limit-replayed-no-new-debit",
    ]
    predicates = []
    candidates = []
    for code in candidate_order:
        row = rows[code]
        active = code in ACTIVE_REASON_CODES
        pred = f"predicate-{code}"
        evidence_rel = "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json" if active else "spec/examples/removable.media.local.post_detach.denial.reason.registry.json"
        predicates.append({
            "predicate_code": pred,
            "active": active,
            "evidence_digest": file_json_digest(ROOT, evidence_rel),
            "maps_to_reason_code": code,
            "support_visibility": "support-safe-digest-only",
        })
        candidates.append({
            "reason_code": code,
            "rank": row["rank"],
            "reason_class": row["reason_class"],
            "active": active,
            "source_predicates": [pred],
        })

    selected = rows["expired-ledger-root-fresh-authority-required"]
    return {
        "kind": "removable.media.local.post_detach.denial.selection.receipt",
        "schema_version": "1.0",
        "selection_receipt_id": "rm-postdetach-denial-selection-20260530-r525",
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
        "attempted_action": "observe",
        "scenario_binding": {
            "scenario_id": binding["scenario_id"],
            "witness_trace_id": binding["witness_trace_id"],
            "terminal_state": binding["terminal_state"],
            "expected_reason_code": binding["primary_reason_code"],
            "expected_rank": binding["expected_rank"],
        },
        "observed_predicates": predicates,
        "candidate_reasons": candidates,
        "selected_reason": {
            "reason_code": selected["reason_code"],
            "rank": selected["rank"],
            "reason_class": selected["reason_class"],
            "selected_by": "lower-rank-wins",
            "subordinate_reason_codes": selected["subordinate_reason_codes"],
            "fresh_authority_required": selected["fresh_authority_required"],
            "allowed_actions": {
                "observe": binding["allow_observe"],
                "export": binding["allow_export"],
                "rehydrate": binding["allow_rehydrate"],
            },
            "support_visibility": selected["support_visibility"],
            "rate_limit_action": binding["rate_limit_action"],
        },
        "decision_proof": {
            "active_candidate_count": len(ACTIVE_REASON_CODES),
            "lower_rank_wins": True,
            "no_active_lower_rank_reason_omitted": True,
            "subordinate_reasons_do_not_preempt": True,
            "selected_reason_matches_registry": True,
            "scenario_binding_matches_witness": True,
            "support_projection_matches_selected_reason": True,
        },
        "rate_limit_binding": {
            "rate_limit_action": binding["rate_limit_action"],
            "debit_count": 1,
            "idempotency_key_digest": enforcement["rate_limit_binding"]["idempotency_key_digest"],
            "debit_receipt_digest": enforcement["rate_limit_binding"]["rate_limit_debit_receipt_digest"],
            "replayed_no_new_debit": False,
        },
        "support_projection": {
            "visibility": support["visibility"],
            "projection_digest": file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json"),
            "visible_reason_code": support["reason_code"],
            "raw_visibility_detected": False,
            "fresh_authority_instruction_visible": support["retry_guidance"]["fresh_authority_instruction_visible"],
        },
        "invariants": {
            "selected_reason_is_active_registry_member": True,
            "lowest_active_non_subordinate_rank_selected": True,
            "support_projection_is_digest_only": True,
            "scenario_and_witness_bindings_match": True,
            "rate_limit_action_matches_selected_reason": True,
        },
        "negative_fixture_policy": "known-bad-post-detach-denial-selection-shapes-must-fail-validation",
    }


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("selection receipt version mismatch")
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

    rows = registry_rows()
    scenario = scenario_binding()
    candidates = obj.get("candidate_reasons", [])
    cand_by_code = {c.get("reason_code"): c for c in candidates}
    if len(cand_by_code) != len(candidates):
        errors.append("candidate reason codes must be unique")
    predicates = obj.get("observed_predicates", [])
    pred_by_code = {p.get("predicate_code"): p for p in predicates}
    if len(pred_by_code) != len(predicates):
        errors.append("predicate codes must be unique")

    for pred in predicates:
        if pred.get("support_visibility") != "support-safe-digest-only":
            errors.append(f"{pred.get('predicate_code')}: predicate support visibility must be digest-only")
        if pred.get("maps_to_reason_code") not in rows:
            errors.append(f"{pred.get('predicate_code')}: maps to unknown reason {pred.get('maps_to_reason_code')}")

    active_candidates = []
    for c in candidates:
        code = c.get("reason_code")
        if code not in rows:
            errors.append(f"unknown candidate reason {code}")
            continue
        row = rows[code]
        if c.get("rank") != row.get("rank"):
            errors.append(f"{code}: candidate rank drifted from registry")
        if c.get("reason_class") != row.get("reason_class"):
            errors.append(f"{code}: candidate class drifted from registry")
        for pred_code in c.get("source_predicates", []):
            pred = pred_by_code.get(pred_code)
            if not pred:
                errors.append(f"{code}: unknown source predicate {pred_code}")
                continue
            if pred.get("maps_to_reason_code") != code:
                errors.append(f"{code}: source predicate {pred_code} maps to {pred.get('maps_to_reason_code')}")
        if c.get("active"):
            active_candidates.append(c)

    selected = obj.get("selected_reason", {})
    selected_code = selected.get("reason_code")
    if selected_code not in rows:
        errors.append("selected reason is not in registry")
    elif selected_code not in cand_by_code:
        errors.append("selected reason is not in candidate set")
    else:
        reg = rows[selected_code]
        cand = cand_by_code[selected_code]
        if cand.get("active") is not True:
            errors.append("selected reason must be active")
        if reg.get("reason_class") == "subordinate-denial" or selected.get("reason_class") == "subordinate-denial":
            errors.append("subordinate reason cannot be the selected primary reason")
        if selected.get("rank") != reg.get("rank"):
            errors.append("selected reason rank drifted from registry")
        if selected.get("reason_class") != reg.get("reason_class"):
            errors.append("selected reason class drifted from registry")
        if selected.get("subordinate_reason_codes") != reg.get("subordinate_reason_codes"):
            errors.append("selected subordinate reasons drifted from registry")
        if selected.get("fresh_authority_required") != reg.get("fresh_authority_required"):
            errors.append("selected fresh_authority_required drifted from registry")
        if selected.get("support_visibility") != "support-safe-digest-only":
            errors.append("selected support visibility must remain digest-only")

    eligible = [c for c in active_candidates if rows.get(c.get("reason_code"), {}).get("reason_class") != "subordinate-denial"]
    if not eligible:
        errors.append("at least one active non-subordinate candidate is required")
    elif selected_code in rows:
        lowest = min(eligible, key=lambda c: int(c.get("rank", 1000)))
        if selected_code != lowest.get("reason_code"):
            errors.append(f"selected reason {selected_code} does not match lowest active non-subordinate {lowest.get('reason_code')}")
        lower_active = [c.get("reason_code") for c in eligible if int(c.get("rank", 1000)) < int(selected.get("rank", 1000))]
        if lower_active:
            errors.append(f"active lower-rank candidates omitted/preempted: {lower_active}")

    sb = obj.get("scenario_binding", {})
    if sb.get("scenario_id") != scenario.get("scenario_id"):
        errors.append("scenario id drifted from registry binding")
    if sb.get("witness_trace_id") != scenario.get("witness_trace_id"):
        errors.append("witness trace id drifted from registry binding")
    if sb.get("terminal_state") != scenario.get("terminal_state"):
        errors.append("terminal state drifted from registry binding")
    if sb.get("expected_reason_code") != scenario.get("primary_reason_code"):
        errors.append("expected reason code drifted from registry binding")
    if sb.get("expected_rank") != scenario.get("expected_rank"):
        errors.append("expected rank drifted from registry binding")
    if selected_code and selected_code != sb.get("expected_reason_code"):
        errors.append("selected reason does not match scenario expected reason")

    allowed = selected.get("allowed_actions", {})
    if allowed.get("observe") != scenario.get("allow_observe") or allowed.get("export") != scenario.get("allow_export") or allowed.get("rehydrate") != scenario.get("allow_rehydrate"):
        errors.append("allowed actions drifted from scenario binding")

    rate = obj.get("rate_limit_binding", {})
    if rate.get("rate_limit_action") != selected.get("rate_limit_action"):
        errors.append("rate limit action does not match selected reason")
    if scenario.get("rate_limit_action") != selected.get("rate_limit_action"):
        errors.append("selected rate limit action drifted from scenario binding")
    expected_debit_count = 1 if scenario.get("rate_limit_action") == "debit" else 0
    if rate.get("debit_count") != expected_debit_count:
        errors.append("rate limit debit_count drifted from scenario binding")
    if rate.get("replayed_no_new_debit") is not False:
        errors.append("primary expired-root attempt is not an idempotent replay")

    support = obj.get("support_projection", {})
    if support.get("visibility") != "support-safe-digest-only":
        errors.append("support projection visibility must be digest-only")
    if support.get("raw_visibility_detected") is not False:
        errors.append("support raw visibility must be false")
    if support.get("visible_reason_code") != selected_code:
        errors.append("support visible reason code must match selected reason")
    if support.get("projection_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json"):
        errors.append("support projection digest binding is stale")

    decision = obj.get("decision_proof", {})
    if decision.get("active_candidate_count") != len(active_candidates):
        errors.append("active candidate count drifted")
    for key, value in decision.items():
        if key != "active_candidate_count" and value is not True:
            errors.append(f"decision proof {key} must be true")
    for key, value in obj.get("invariants", {}).items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


def invalid_objects(obj: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}

    stale = copy.deepcopy(obj)
    stale["source_bindings"]["denial_reason_registry_computed_digest"] = "sha256:" + "00" * 32
    out["stale-registry-binding.json"] = stale

    omitted = copy.deepcopy(obj)
    for c in omitted["candidate_reasons"]:
        if c["reason_code"] == "raw-support-visibility":
            c["active"] = True
    for p in omitted["observed_predicates"]:
        if p["maps_to_reason_code"] == "raw-support-visibility":
            p["active"] = True
    omitted["decision_proof"]["active_candidate_count"] += 1
    out["omitted-higher-precedence.json"] = omitted

    unknown = copy.deepcopy(obj)
    unknown["selected_reason"]["reason_code"] = "unknown-denial-reason"
    out["selected-unknown-reason.json"] = unknown

    subordinate = copy.deepcopy(obj)
    subordinate["selected_reason"]["reason_code"] = "missing-fresh-authority"
    subordinate["selected_reason"]["rank"] = registry_rows()["missing-fresh-authority"]["rank"]
    subordinate["selected_reason"]["reason_class"] = "subordinate-denial"
    subordinate["selected_reason"]["subordinate_reason_codes"] = []
    out["selected-subordinate-reason.json"] = subordinate

    raw = copy.deepcopy(obj)
    raw["support_projection"]["visibility"] = "raw-support-visible"
    out["support-raw-visibility.json"] = raw

    rate = copy.deepcopy(obj)
    rate["selected_reason"]["rate_limit_action"] = "no-debit"
    rate["rate_limit_binding"]["rate_limit_action"] = "no-debit"
    rate["rate_limit_binding"]["debit_count"] = 0
    out["rate-limit-action-drift.json"] = rate

    witness = copy.deepcopy(obj)
    witness["scenario_binding"]["witness_trace_id"] = "trace-r523-wrong"
    out["witness-scenario-drift.json"] = witness

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
    if "check_removable_media_local_post_detach_denial_selection_receipt.py" not in hygiene:
        fail("tools/hygiene.py missing denial selection receipt checker")


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
        fail("semantic denial selection receipt errors:\n- " + "\n- ".join(sem[:40]))
    if observed != expected:
        print("denial selection receipt is stale; regenerate with:", file=sys.stderr)
        print("  python3 tools/check_removable_media_local_post_detach_denial_selection_receipt.py --write", file=sys.stderr)
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
    print("removable-media post-detach denial selection receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate r523 post-detach transition witness capsules.

r522 replayed whole scenarios.  r523 adds a transition witness capsule so the
replay is reviewable as ordered steps: each scenario has a trace, each trace
names known state-machine states, terminal outcomes match the replay manifest,
outcome digests are computed, support visibility remains digest-only, and the
idempotent replay path cannot double-debit rate limits.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import canonical_digest, file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r523"
SCHEMA = "spec/removable.media.local.post_detach.transition.witness.capsule.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.transition.witness.capsule.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-transition-witness-capsule"

BINDING_PATHS = {
    "state_machine_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.state_machine.manifest.json",
    "scenario_replay_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json",
    "enforcement_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json",
    "fresh_authority_recovery_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
    "backend_evidence_computed_digest": "spec/examples/removable.media.local.post_detach.backend.enforcement.evidence.json",
}

EXPECTED_INVALIDS = [
    "idempotent-replay-double-debit.json",
    "nonmonotonic-step-order.json",
    "stale-model-binding.json",
    "successor-trace-resurrects-expired-root.json",
    "support-raw-visibility.json",
    "trace-omits-enforcement-ledger-step.json",
]

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "transition-witness-capsule", "check_removable_media_local_post_detach_transition_witness.py"],
    "README.md": [VERSION, "transition-witness-capsule", "hygiene-checkset"],
    "docs/00-index.md": [VERSION, "docs/778-removable-media-local-fallback-post-detach-transition-witness-and-hygiene-shards.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_transition_witness.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_transition_witness.py"],
    "docs/110-juicy-os-lessons.md": ["r523 removable-media post-detach transition witness"],
    "docs/778-removable-media-local-fallback-post-detach-transition-witness-and-hygiene-shards.md": [
        "removable.media.local.post_detach.transition.witness.capsule",
        "cube.hygiene.checkset.manifest",
        "tools/hygiene.py --profile release-critical",
    ],
    "docs/current/removable-media-post-detach-transition-witness.md": [
        "transition-witness-capsule",
        "idempotent-denial-replayed",
        "successor-root-admitted",
    ],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def outcome_digest(trace: dict[str, Any]) -> str:
    copy_trace = copy.deepcopy(trace)
    copy_trace.pop("outcome_digest", None)
    return canonical_digest(copy_trace)


def scenario_map() -> dict[str, dict[str, Any]]:
    replay = load_json(ROOT, "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json")
    return {s["scenario_id"]: s for s in replay["scenarios"]}


def known_states() -> set[str]:
    sm = load_json(ROOT, "spec/examples/removable.media.local.post_detach.state_machine.manifest.json")
    return {s["state_id"] for s in sm["states"]} | {
        "fail-closed-missing-expiry-denial",
        "fail-closed-stale-root-denial",
        "fail-closed-degraded-time-denial",
        "idempotent-denial-replay-cache",
    }


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("transition witness version mismatch")
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

    scenarios = scenario_map()
    states = known_states()
    traces = obj.get("traces", [])
    trace_ids = {t.get("scenario_id") for t in traces}
    if trace_ids != set(scenarios):
        errors.append(f"trace scenario ids mismatch: {sorted(trace_ids)} != {sorted(scenarios)}")
    if len(trace_ids) != len(traces):
        errors.append("trace scenario ids must be unique")

    for trace in traces:
        sid = trace.get("scenario_id")
        scenario = scenarios.get(sid)
        if not scenario:
            continue
        expected = scenario["expected_outcome"]
        if trace.get("terminal_state") != expected.get("terminal_state"):
            errors.append(f"{sid}: terminal_state does not match replay manifest")
        if trace.get("expected_replay_terminal_state") != expected.get("terminal_state"):
            errors.append(f"{sid}: expected_replay_terminal_state drifted from replay manifest")
        if trace.get("fresh_authority_required") != expected.get("fresh_authority_required"):
            errors.append(f"{sid}: fresh_authority_required does not match replay manifest")
        allowed = trace.get("allowed_actions", {})
        if allowed.get("observe") != expected.get("allow_new_observation"):
            errors.append(f"{sid}: observe action does not match replay manifest")
        if allowed.get("export") != expected.get("allow_export"):
            errors.append(f"{sid}: export action does not match replay manifest")
        if allowed.get("rehydrate") != expected.get("allow_rehydration"):
            errors.append(f"{sid}: rehydrate action does not match replay manifest")
        if trace.get("expired_root_observable") != expected.get("expired_root_observation_allowed"):
            errors.append(f"{sid}: expired_root_observable does not match replay manifest")
        if trace.get("successor_root_only") != expected.get("successor_root_only"):
            errors.append(f"{sid}: successor_root_only does not match replay manifest")
        if trace.get("double_debit_prevented") != expected.get("double_debit_prevented"):
            errors.append(f"{sid}: double_debit_prevented does not match replay manifest")

        if trace.get("support_visibility") != "support-safe-digest-only":
            errors.append(f"{sid}: support visibility must be digest-only")
        if trace.get("outcome_digest") != outcome_digest(trace):
            errors.append(f"{sid}: outcome digest is not computed from trace content")

        steps = trace.get("steps", [])
        indexes = [step.get("step_index") for step in steps]
        if indexes != list(range(1, len(steps) + 1)):
            errors.append(f"{sid}: step indexes must be monotonic and contiguous")
        for step in steps:
            if step.get("from_state") not in states:
                errors.append(f"{sid}: unknown from_state {step.get('from_state')!r}")
            if step.get("to_state") not in states:
                errors.append(f"{sid}: unknown to_state {step.get('to_state')!r}")
            kind = step.get("required_receipt_kind", "")
            if "." not in kind:
                errors.append(f"{sid}: required_receipt_kind must be a dotted kind")
            actions_after = step.get("allowed_actions_after_step", {})
            if trace.get("terminal_state") != "successor-root-admitted":
                if actions_after.get("observe") or actions_after.get("export") or actions_after.get("rehydrate"):
                    errors.append(f"{sid}: denial/fail-closed step allowed observe/export/rehydrate")

        if sid == "expired-root-denied-with-enforcement-ledger":
            if not any(step.get("event") == "commit-enforcement-ledger" for step in steps):
                errors.append("expired-root-denied trace must commit enforcement ledger")
        if sid == "fresh-authority-recovers-to-successor-root-only":
            if trace.get("expired_root_observable") is not False or trace.get("successor_root_only") is not True:
                errors.append("fresh-authority trace must stay successor-root-only and not resurrect expired root")
            if not any(step.get("event") == "admit-successor-reader" for step in steps):
                errors.append("fresh-authority trace must admit a successor reader")
        if sid == "same-idempotency-key-replays-same-denial-without-double-debit":
            if trace.get("rate_limit_debit_count") != 0 or trace.get("double_debit_prevented") is not True:
                errors.append("idempotent replay trace must not debit rate limits")
            if not any(step.get("rate_limit_action") == "replayed-no-new-debit" for step in steps):
                errors.append("idempotent replay trace must record replayed-no-new-debit")

    invariants = obj.get("invariants", {})
    for key, value in invariants.items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


def require_invalids_fail() -> None:
    root = ROOT / INVALID_DIR
    if not root.is_dir():
        fail(f"missing invalid fixture dir {INVALID_DIR}")
    observed = sorted(p.name for p in root.glob("*.json"))
    if observed != EXPECTED_INVALIDS:
        fail(f"invalid fixtures mismatch: {observed} != {EXPECTED_INVALIDS}")
    for name in EXPECTED_INVALIDS:
        rel = f"{INVALID_DIR}/{name}"
        obj = load_json(ROOT, rel)
        if not validation_errors(SCHEMA, obj) and not semantic_errors(obj):
            fail(f"invalid fixture unexpectedly passed schema+semantic checks: {rel}")


def require_docs() -> None:
    for rel, tokens in REQUIRED_DOC_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            fail(f"missing required doc surface: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                fail(f"{rel} missing required token {token!r}")
    hygiene = (ROOT / "tools" / "hygiene.py").read_text(encoding="utf-8")
    for token in ["check_removable_media_local_post_detach_transition_witness.py", "--profile", "release-critical"]:
        if token not in hygiene:
            fail(f"tools/hygiene.py missing {token!r}")


def main() -> int:
    obj = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, obj)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(obj)
    if sem:
        fail("; ".join(sem[:20]))
    require_invalids_fail()
    require_docs()
    print("removable-media post-detach transition witness check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

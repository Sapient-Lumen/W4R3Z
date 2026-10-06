#!/usr/bin/env python3
"""Validate r530 post-detach terminal closure capsules.

r529 made export-bundle deletion typed, but the lane still lacked one terminal
capsule that binds deletion, denial selection, support projection, transition
witness, and scenario replay into a single close-out assertion.  r530 adds that
capsule so managed post-detach authority is closed without overclaiming offline
erasure and without resurrecting expired roots or old handles.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r530"
SCHEMA = "spec/removable.media.local.post_detach.terminal.closure.capsule.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.terminal.closure.capsule.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-terminal-closure-capsule"

SOURCE_BINDINGS = {
    "export_bundle_deletion_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.export.bundle.deletion.receipt.json",
    "export_bundle_access_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.export.bundle.access.receipt.json",
    "revocation_tombstone_computed_digest": "spec/examples/removable.media.local.post_detach.revocation.tombstone.json",
    "denial_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.receipt.json",
    "denial_selection_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json",
    "denial_reason_registry_computed_digest": "spec/examples/removable.media.local.post_detach.denial.reason.registry.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
    "transition_witness_capsule_computed_digest": "spec/examples/removable.media.local.post_detach.transition.witness.capsule.json",
    "scenario_replay_manifest_computed_digest": "spec/examples/removable.media.local.post_detach.scenario.replay.manifest.json",
}

EXPECTED_INVALIDS = [
    "closure-ledger-not-advanced.json",
    "denial-selection-not-bound.json",
    "expired-root-resurrected.json",
    "managed-export-left-open.json",
    "missing-export-deletion-binding.json",
    "new-export-approval-not-required.json",
    "offline-erasure-overclaimed.json",
    "raw-support-visible.json",
    "stale-export-deletion-binding.json",
    "transition-witness-not-checked.json",
]

FORBIDDEN_TOKENS = ("/media/", "/Volumes/", "file://", "raw-path:", "johnny", "j30385433", "secret=", "secret.txt")

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "terminal.closure.capsule", "check_removable_media_local_post_detach_terminal_closure_capsule.py"],
    "README.md": [VERSION, "terminal-closure", "denial-receipt-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-terminal-closure.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_terminal_closure_capsule.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_terminal_closure_capsule.py"],
    "docs/110-juicy-os-lessons.md": ["r530 removable-media post-detach terminal closure"],
    "docs/785-removable-media-local-fallback-post-detach-terminal-closure-and-denial-receipt-schema-split.md": [
        "removable.media.local.post_detach.terminal.closure.capsule",
        "post-detach-terminal-closure-positive-and-negative-fixture-guarded",
        "post-detach-denial-receipt-generic-runtime-schema-plus-exact-fixture-split",
    ],
    "docs/current/removable-media-post-detach-terminal-closure.md": [
        "terminal closure",
        "future access is denied",
        "offline-copy erasure is not claimed",
        "denial receipt schema split",
    ],
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def validation_errors(schema_rel: str, obj: Any) -> list[str]:
    schema = load_json(ROOT, schema_rel)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("generated_for_version") != VERSION:
        errors.append("terminal closure version mismatch")
    lane = obj.get("lane", {})
    if lane.get("family") != "removable-media-local-fallback" or lane.get("phase") != "post-detach":
        errors.append("lane must remain removable-media-local-fallback/post-detach")

    bindings = obj.get("source_bindings", {})
    if bindings.get("canonical_digest_rule") != "json-sort-keys-compact-utf8-sha256":
        errors.append("canonical digest rule mismatch")
    for key, rel in SOURCE_BINDINGS.items():
        if bindings.get(key) != file_json_digest(ROOT, rel):
            errors.append(f"{key} does not match {rel}")

    deletion = load_json(ROOT, "spec/examples/removable.media.local.post_detach.export.bundle.deletion.receipt.json")
    selection = load_json(ROOT, "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json")
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")

    terminal = obj.get("terminal_inputs", {})
    deletion_digest = file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.export.bundle.deletion.receipt.json")
    selection_digest = file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json")
    support_digest = file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")
    if terminal.get("export_bundle_deletion_receipt_id") != deletion.get("deletion_receipt_id"):
        errors.append("export deletion receipt id binding is stale")
    if terminal.get("export_bundle_deletion_receipt_digest") != deletion_digest:
        errors.append("export deletion receipt digest binding is stale")
    if terminal.get("delete_sequence") != deletion.get("deletion_ledger", {}).get("delete_sequence"):
        errors.append("delete sequence must match r529 deletion ledger")
    if terminal.get("denial_selection_receipt_id") != selection.get("selection_receipt_id"):
        errors.append("denial selection receipt id binding is stale")
    if terminal.get("denial_selection_receipt_digest") != selection_digest:
        errors.append("denial selection receipt digest binding is stale")
    if terminal.get("selected_reason_code") != selection.get("selected_reason", {}).get("reason_code"):
        errors.append("selected reason must match the denial-selection receipt")
    if terminal.get("support_projection_digest") != support_digest:
        errors.append("support projection digest binding is stale")

    auth = obj.get("authority_posture", {})
    expected_auth = {
        "managed_export_future_access": "denied-after-terminal-closure",
        "query_projection_future_access": "denied-unless-new-authority",
        "rehydration_future_access": "denied-unless-new-authority",
        "reader_observation_future_access": "denied-unless-successor-authority",
        "fresh_authority_required_for_any_new_successor": True,
        "expired_root_future_observation_allowed": False,
        "old_handle_resurrection_allowed": False,
        "new_export_requires_new_approval": True,
    }
    for key, expected in expected_auth.items():
        if auth.get(key) != expected:
            errors.append(f"authority posture {key} must be {expected!r}")

    deletion_closure = obj.get("deletion_closure", {})
    for key in ["local_managed_copy_terminal", "controlled_remote_object_terminal_or_revoked", "live_locator_absent_or_terminal", "bounded_retention_proven"]:
        if deletion_closure.get(key) is not True:
            errors.append(f"deletion closure {key} must be true")
    if deletion_closure.get("offline_copy_claim") != "not-claimed-erased-only-future-authority-denied":
        errors.append("terminal closure must not claim unmanaged offline-copy erasure")
    if deletion_closure.get("raw_locator_visible") is not False:
        errors.append("terminal closure must not expose raw locators")

    denial = obj.get("denial_closure", {})
    for key in ["denial_reason_registry_checked", "denial_selection_receipt_checked", "selected_reason_is_registry_member", "subordinate_reasons_do_not_preempt"]:
        if denial.get(key) is not True:
            errors.append(f"denial closure {key} must be true")
    if denial.get("rate_limit_double_debit_on_replay") is not False:
        errors.append("idempotent replay must not double debit rate limits")
    if denial.get("support_visibility") != support.get("visibility"):
        errors.append("denial closure support visibility must match support projection")

    projection = obj.get("support_projection", {})
    if projection.get("visibility") != support.get("visibility"):
        errors.append("support visibility must match support projection")
    for field in [
        "raw_payload_visible",
        "raw_path_visible",
        "filename_visible",
        "device_identifier_visible",
        "host_identity_visible",
        "body_or_full_text_visible",
        "secret_material_visible",
    ]:
        if projection.get(field) is not False:
            errors.append(f"{field} must be false")
    text = json.dumps(obj, sort_keys=True)
    for token in FORBIDDEN_TOKENS:
        if token in text:
            errors.append(f"terminal closure leaks forbidden token {token!r}")

    ledger = obj.get("closure_ledger", {})
    if ledger.get("expected_root_digest") != ledger.get("prior_root_digest"):
        errors.append("closure ledger CAS expected root must equal prior root")
    if ledger.get("new_root_digest") == ledger.get("prior_root_digest"):
        errors.append("closure ledger root must advance")
    if ledger.get("compare_and_swap_result") != "committed":
        errors.append("closure ledger CAS must commit")
    if ledger.get("closure_sequence", 0) <= terminal.get("delete_sequence", 0):
        errors.append("closure sequence must follow export deletion sequence")
    if any(ledger.get(flag) is not False for flag in ["rollback_accepted", "forked_root_accepted", "stale_root_accepted"]):
        errors.append("rollback/fork/stale closure roots must not be accepted")

    for key, value in obj.get("joins", {}).items():
        if value is not True:
            errors.append(f"join {key} must be true")
    for key, value in obj.get("invariants", {}).items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    return errors


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
    if "check_removable_media_local_post_detach_terminal_closure_capsule.py" not in hygiene:
        fail("tools/hygiene.py missing terminal closure checker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="no-op compatibility; examples are maintained as release artifacts")
    args = ap.parse_args()
    if args.write:
        print("terminal closure example is maintained directly")
        return 0

    obj = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, obj)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(obj)
    if sem:
        fail("semantic terminal closure errors:\n- " + "\n- ".join(sem[:30]))

    invalid_root = ROOT / INVALID_DIR
    names = sorted(p.name for p in invalid_root.glob("*.json"))
    if names != EXPECTED_INVALIDS:
        fail(f"invalid fixture set mismatch: {names} != {EXPECTED_INVALIDS}")
    for path in sorted(invalid_root.glob("*.json")):
        bad = load_json(ROOT, f"{INVALID_DIR}/{path.name}")
        schema_errs = validation_errors(SCHEMA, bad)
        sem_errs = semantic_errors(bad) if not schema_errs else ["schema rejected"]
        if not schema_errs and not sem_errs:
            fail(f"invalid fixture unexpectedly passes schema+semantic validation: {path}")

    require_docs()
    print("removable-media post-detach terminal-closure capsule check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

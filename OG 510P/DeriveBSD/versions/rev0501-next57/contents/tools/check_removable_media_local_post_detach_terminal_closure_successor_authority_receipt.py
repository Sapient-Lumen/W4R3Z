#!/usr/bin/env python3
"""Validate r532 post-detach terminal-closure successor-authority receipts.

r531 denied old managed authority after terminal closure. r532 adds the safe
positive path: a successor authority may be issued only from fresh authority,
after the post-closure access denial is bound, rate-limited, and support-safe.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r532"
SCHEMA = "spec/removable.media.local.post_detach.terminal.closure.successor.authority.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.terminal.closure.successor.authority.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-terminal-closure-successor-authority-receipt"
KIND = "removable.media.local.post_detach.terminal.closure.successor.authority.receipt"
POSTURE = "post-detach-terminal-closure-successor-authority-positive-and-negative-fixture-guarded"
POLICY = "known-bad-post-detach-terminal-closure-successor-authority-shapes-must-fail-validation"

SOURCE_BINDINGS = {
    "terminal_closure_capsule_computed_digest": "spec/examples/removable.media.local.post_detach.terminal.closure.capsule.json",
    "terminal_closure_access_receipt_computed_digest": "spec/examples/removable.media.local_post_detach.terminal.closure.access.receipt.json".replace("local_post", "local.post"),
    "fresh_authority_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json",
    "denial_reason_registry_computed_digest": "spec/examples/removable.media.local.post_detach.denial.reason.registry.json",
    "denial_selection_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json",
    "rate_limit_debit_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
    "reader_admission_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.reader.admission.receipt.json",
}

EXPECTED_INVALIDS = [
    "expired-root-resurrected.json",
    "fresh-authority-stale-handle-reused.json",
    "missing-terminal-closure-access-binding.json",
    "old-authority-presented-as-new-authority.json",
    "old-export-approval-carried-forward.json",
    "rate-limit-not-proven-before-successor.json",
    "reader-admission-not-required.json",
    "stale-terminal-closure-access-binding.json",
    "successor-ledger-not-advanced.json",
    "support-raw-visible.json",
    "terminal-closure-reopened.json",
]

FORBIDDEN_TOKENS = ("/media/", "/Volumes/", "file://", "raw-path:", "johnny", "j30385433", "secret=", "secret.txt")

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, KIND, "check_removable_media_local_post_detach_terminal_closure_successor_authority_receipt.py"],
    "README.md": [VERSION, "terminal-closure-successor-authority", "reader-admission-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-terminal-closure-successor-authority.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_terminal_closure_successor_authority_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_terminal_closure_successor_authority_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r532 removable-media post-detach terminal-closure successor authority"],
    "docs/787-removable-media-local-fallback-post-detach-terminal-closure-successor-authority-and-reader-admission-schema-split.md": [
        KIND,
        POSTURE,
        "post-detach-reader-admission-generic-runtime-schema-plus-exact-fixture-split",
    ],
    "docs/current/removable-media-post-detach-terminal-closure-successor-authority.md": [
        "terminal-closure successor authority",
        "successor-authority-issued-from-new-authority-only",
        "old managed authority remains denied",
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
    if obj.get("kind") != KIND:
        errors.append("kind mismatch")
    if obj.get("generated_for_version") != VERSION:
        errors.append("successor authority version mismatch")
    if obj.get("negative_fixture_policy") != POLICY:
        errors.append("negative fixture policy mismatch")
    lane = obj.get("lane", {})
    if lane.get("family") != "removable-media-local-fallback" or lane.get("phase") != "post-detach":
        errors.append("lane must remain removable-media-local-fallback/post-detach")

    bindings = obj.get("source_bindings", {})
    if bindings.get("canonical_digest_rule") != "json-sort-keys-compact-utf8-sha256":
        errors.append("canonical digest rule mismatch")
    for key, rel in SOURCE_BINDINGS.items():
        expected = file_json_digest(ROOT, rel)
        if bindings.get(key) != expected:
            errors.append(f"{key} does not match computed digest for {rel}")

    closure = load_json(ROOT, "spec/examples/removable.media.local.post_detach.terminal.closure.capsule.json")
    closure_access = load_json(ROOT, "spec/examples/removable.media.local.post_detach.terminal.closure.access.receipt.json")
    fresh = load_json(ROOT, "spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json")
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")
    reader = load_json(ROOT, "spec/examples/removable.media.local.post_detach.reader.admission.receipt.json")

    cab = obj.get("closure_access_binding", {})
    if cab.get("terminal_closure_capsule_id") != closure.get("closure_capsule_id"):
        errors.append("terminal closure capsule id binding is stale")
    if cab.get("terminal_closure_capsule_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.terminal.closure.capsule.json"):
        errors.append("terminal closure capsule digest binding is stale")
    if cab.get("terminal_closure_access_receipt_id") != closure_access.get("access_receipt_id"):
        errors.append("terminal closure access receipt id binding is stale")
    if cab.get("terminal_closure_access_receipt_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.terminal.closure.access.receipt.json"):
        errors.append("terminal closure access receipt digest binding is stale")
    if cab.get("prior_access_outcome") != "deny-post-closure-old-authority":
        errors.append("successor authority must bind a prior old-authority denial")
    if cab.get("old_authority_denied_before_successor_issue") is not True:
        errors.append("old authority must be denied before successor issuance")
    if cab.get("rate_limit_debited_for_denied_attempt") is not True:
        errors.append("prior denial must prove rate-limit debit before successor issuance")

    req = obj.get("new_authority_request", {})
    if req.get("closure_state_seen") != "managed-authority-terminally-closed":
        errors.append("new authority request must see terminal closure state")
    for key in ["ambient_reauthentication_attempted", "old_handle_presented_as_authority", "raw_handle_values_included", "raw_locator_values_included"]:
        if req.get(key) is not False:
            errors.append(f"new authority request {key} must be false")

    fab = obj.get("fresh_authority_binding", {})
    if fab.get("fresh_authority_receipt_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.fresh.authority.receipt.json"):
        errors.append("fresh authority digest binding is stale")
    if fab.get("approval_receipt_digest") != fresh.get("actor_intent", {}).get("approval_receipt_digest"):
        errors.append("fresh authority approval digest binding is stale")
    if fab.get("policy_digest") != fresh.get("authority_decision", {}).get("policy_digest"):
        errors.append("fresh authority policy digest binding is stale")
    if fab.get("new_lease_digest") != fresh.get("successor_subjects", {}).get("new_lease_digest"):
        errors.append("fresh authority lease digest binding is stale")
    if fab.get("fresh_lease_required_after_terminal_closure") is not True:
        errors.append("fresh lease must be required after terminal closure")
    for key in ["stale_handle_reused", "tombstone_bypass", "old_handle_reused"]:
        if fab.get(key) is not False:
            errors.append(f"fresh authority binding {key} must be false")

    issuance = obj.get("successor_issuance", {})
    expected_issuance = {
        "outcome": "successor-authority-issued-from-new-authority-only",
        "old_handle_reused": False,
        "expired_root_resurrected": False,
        "terminal_closure_reopened": False,
        "successor_issued_from_old_authority": False,
        "new_export_approval_required": True,
        "reader_admission_required_before_reader_use": True,
        "reader_admission_receipt_schema": "spec/removable.media.local.post_detach.reader.admission.receipt.schema.json",
        "reader_admission_fixture_schema": "spec/removable.media.local.post_detach.reader.admission.receipt.fixture.schema.json",
    }
    for key, expected in expected_issuance.items():
        if issuance.get(key) != expected:
            errors.append(f"successor issuance {key} must be {expected!r}")
    if issuance.get("reader_admission_receipt_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.reader.admission.receipt.json"):
        errors.append("reader admission computed digest binding is stale")
    if issuance.get("reader_admission_legacy_digest") != reader.get("contract_binding", {}).get("reader_admission_digest"):
        errors.append("reader admission legacy digest binding is stale")

    ledger = obj.get("successor_ledger", {})
    if ledger.get("expected_root_digest") != ledger.get("prior_root_digest"):
        errors.append("successor ledger expected root must equal prior root")
    if ledger.get("new_root_digest") == ledger.get("prior_root_digest"):
        errors.append("successor ledger new root must advance")
    if ledger.get("compare_and_swap_result") != "committed":
        errors.append("successor ledger CAS must commit")
    for key in ["rollback_accepted", "forked_root_accepted", "stale_root_accepted"]:
        if ledger.get(key) is not False:
            errors.append(f"successor ledger {key} must be false")

    projection = obj.get("support_projection", {})
    if projection.get("visibility") != support.get("visibility"):
        errors.append("support visibility must match allowlisted support projection")
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
            errors.append(f"support projection {field} must be false")
    if projection.get("offline_erasure_claim") != "not-claimed-erased-only-future-authority-controlled":
        errors.append("offline erasure must not be overclaimed")

    for key, value in obj.get("invariants", {}).items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    text = json.dumps(obj, sort_keys=True)
    for token in FORBIDDEN_TOKENS:
        if token in text:
            errors.append(f"successor authority receipt leaks forbidden token {token!r}")
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
    if "check_removable_media_local_post_detach_terminal_closure_successor_authority_receipt.py" not in hygiene:
        fail("tools/hygiene.py missing terminal closure successor authority checker")


def main() -> int:
    example = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, example)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(example)
    if sem:
        fail("semantic terminal-closure successor authority errors:\n- " + "\n- ".join(sem[:30]))

    observed = {p.name for p in (ROOT / INVALID_DIR).glob("*.json")}
    missing = sorted(set(EXPECTED_INVALIDS) - observed)
    if missing:
        fail(f"missing invalid fixtures under {INVALID_DIR}: {missing}")
    for name in EXPECTED_INVALIDS:
        rel = f"{INVALID_DIR}/{name}"
        bad = load_json(ROOT, rel)
        if not validation_errors(SCHEMA, bad) and not semantic_errors(bad):
            fail(f"invalid fixture unexpectedly validates: {rel}")

    require_docs()
    print("removable-media post-detach terminal-closure successor authority receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

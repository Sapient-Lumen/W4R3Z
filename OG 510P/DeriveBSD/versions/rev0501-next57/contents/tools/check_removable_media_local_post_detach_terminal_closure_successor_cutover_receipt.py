#!/usr/bin/env python3
"""Validate r533 post-detach terminal-closure successor cutover receipts.

r532 issues successor authority after terminal closure. r533 prevents that
successor authority from becoming active until the old successor-index cutover,
checkpoint, and reader-admission fences are all observed by computed digest.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r533"
SCHEMA = "spec/removable.media.local.post_detach.terminal.closure.successor.cutover.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.terminal.closure.successor.cutover.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-terminal-closure-successor-cutover-receipt"
KIND = "removable.media.local.post_detach.terminal.closure.successor.cutover.receipt"
POSTURE = "post-detach-terminal-closure-successor-cutover-positive-and-negative-fixture-guarded"
POLICY = "known-bad-post-detach-terminal-closure-successor-cutover-shapes-must-fail-validation"
SPLIT_POSTURE = "post-detach-successor-index-cutover-generic-runtime-schema-plus-exact-fixture-split"

SOURCE_BINDINGS = {
    "terminal_closure_successor_authority_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.terminal.closure.successor.authority.receipt.json",
    "successor_index_cutover_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json",
    "successor_index_checkpoint_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.successor.index.checkpoint.receipt.json",
    "reader_admission_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.reader.admission.receipt.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
}

EXPECTED_INVALIDS = [
    "broker-use-before-checkpoint.json",
    "checkpoint-not-observed.json",
    "cutover-not-observed.json",
    "missing-successor-authority-binding.json",
    "non-advancing-cutover-ledger.json",
    "old-index-dual-live.json",
    "raw-support-visible.json",
    "reader-admission-not-bound.json",
    "stale-successor-authority-binding.json",
    "successor-broadened.json",
    "terminal-closure-reopened.json",
]

FORBIDDEN_TOKENS = ("/media/", "/Volumes/", "file://", "raw-path:", "johnny", "j30385433", "secret=", "secret.txt")

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, KIND, "check_removable_media_local_post_detach_terminal_closure_successor_cutover_receipt.py"],
    "README.md": [VERSION, "terminal-closure-successor-cutover", "successor-index-cutover-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-terminal-closure-successor-cutover.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_terminal_closure_successor_cutover_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_terminal_closure_successor_cutover_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r533 removable-media post-detach terminal-closure successor cutover"],
    "docs/788-removable-media-local-fallback-post-detach-terminal-closure-successor-cutover-and-successor-index-cutover-schema-split.md": [
        KIND,
        POSTURE,
        SPLIT_POSTURE,
    ],
    "docs/current/removable-media-post-detach-terminal-closure-successor-cutover.md": [
        "terminal-closure successor cutover",
        "successor-index cutover observed before activation",
        "checkpoint observed before broker use",
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
        errors.append("successor cutover version mismatch")
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

    successor = load_json(ROOT, "spec/examples/removable.media.local.post_detach.terminal.closure.successor.authority.receipt.json")
    cutover = load_json(ROOT, "spec/examples/removable.media.local.post_detach.successor.index.cutover.receipt.json")
    checkpoint = load_json(ROOT, "spec/examples/removable.media.local.post_detach.successor.index.checkpoint.receipt.json")
    reader = load_json(ROOT, "spec/examples/removable.media.local.post_detach.reader.admission.receipt.json")
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")

    sab = obj.get("successor_authority_binding", {})
    if sab.get("successor_authority_receipt_id") != successor.get("successor_authority_receipt_id"):
        errors.append("successor authority id binding is stale")
    if sab.get("successor_authority_receipt_digest") != file_json_digest(ROOT, SOURCE_BINDINGS["terminal_closure_successor_authority_receipt_computed_digest"]):
        errors.append("successor authority computed digest binding is stale")
    if sab.get("outcome") != "successor-authority-issued-from-new-authority-only":
        errors.append("successor authority outcome must be new-authority-only")
    if sab.get("old_authority_denied_before_successor_issue") is not True:
        errors.append("old authority must have been denied before successor issue")
    if sab.get("issued_from_new_authority_only") is not True:
        errors.append("successor must be issued from new authority only")
    if sab.get("terminal_closure_reopened") is not False:
        errors.append("terminal closure must not be reopened")

    cb = obj.get("cutover_binding", {})
    if cb.get("successor_index_cutover_receipt_digest") != file_json_digest(ROOT, SOURCE_BINDINGS["successor_index_cutover_receipt_computed_digest"]):
        errors.append("successor index cutover computed digest binding is stale")
    if cb.get("successor_index_cutover_receipt_schema") != "spec/removable.media.local.post_detach.successor.index.cutover.receipt.schema.json":
        errors.append("successor index cutover runtime schema binding mismatch")
    if cb.get("successor_index_cutover_fixture_schema") != "spec/removable.media.local.post_detach.successor.index.cutover.receipt.fixture.schema.json":
        errors.append("successor index cutover fixture schema binding mismatch")
    if cb.get("cutover_sequence") != cutover.get("evidence_state", {}).get("monotonic_sequence"):
        errors.append("cutover sequence does not match cutover receipt")
    if cb.get("cutover_outcome") != cutover.get("cutover_decision", {}).get("outcome"):
        errors.append("cutover outcome is stale")
    for key in ["old_handles_terminal", "cutover_observed_before_activation"]:
        if cb.get(key) is not True:
            errors.append(f"cutover binding {key} must be true")
    for key in ["old_handles_still_live", "dual_active_window_allowed", "successor_authority_broadened"]:
        if cb.get(key) is not False:
            errors.append(f"cutover binding {key} must be false")

    chk = obj.get("checkpoint_binding", {})
    if chk.get("successor_index_checkpoint_receipt_digest") != file_json_digest(ROOT, SOURCE_BINDINGS["successor_index_checkpoint_receipt_computed_digest"]):
        errors.append("successor index checkpoint computed digest binding is stale")
    checkpoint_sequence = checkpoint.get("checkpoint_state", {}).get("checkpoint_sequence")
    if chk.get("checkpoint_sequence") != checkpoint_sequence:
        errors.append("checkpoint sequence does not match checkpoint receipt")
    if chk.get("minimum_accepted_sequence") != checkpoint.get("reader_fence", {}).get("minimum_accepted_sequence"):
        errors.append("minimum accepted sequence does not match checkpoint reader fence")
    if isinstance(chk.get("checkpoint_sequence"), int) and isinstance(cb.get("cutover_sequence"), int) and chk["checkpoint_sequence"] < cb["cutover_sequence"]:
        errors.append("checkpoint sequence must be at or after cutover sequence")
    if chk.get("checkpoint_observed_before_broker_use") is not True:
        errors.append("checkpoint must be observed before broker use")
    for key in ["rollback_to_pre_cutover_root_allowed", "old_handle_root_restored", "dual_active_snapshot_accepted"]:
        if chk.get(key) is not False:
            errors.append(f"checkpoint binding {key} must be false")

    rab = obj.get("reader_admission_binding", {})
    if rab.get("reader_admission_receipt_digest") != file_json_digest(ROOT, SOURCE_BINDINGS["reader_admission_receipt_computed_digest"]):
        errors.append("reader admission computed digest binding is stale")
    if rab.get("reader_admission_fixture_schema") != "spec/removable.media.local.post_detach.reader.admission.receipt.fixture.schema.json":
        errors.append("reader admission fixture schema binding mismatch")
    if rab.get("admission_outcome") != reader.get("admission_decision", {}).get("outcome"):
        errors.append("reader admission outcome is stale")
    if rab.get("observed_checkpoint_sequence") != reader.get("admission_state", {}).get("observed_checkpoint_sequence"):
        errors.append("reader admission checkpoint sequence does not match reader admission receipt")
    if rab.get("observed_checkpoint_sequence") != chk.get("checkpoint_sequence"):
        errors.append("reader admission must observe the bound checkpoint sequence")
    if rab.get("admission_required_before_broker_use") is not True:
        errors.append("reader admission must be required before broker use")
    if rab.get("broker_use_before_admission") is not False:
        errors.append("broker use before admission must remain false")
    if rab.get("successor_digest_exact") is not True:
        errors.append("reader admission successor digest must be exact")

    ledger = obj.get("activation_ledger", {})
    if ledger.get("expected_root_digest") != ledger.get("prior_root_digest"):
        errors.append("activation ledger expected root must equal prior root")
    if ledger.get("new_root_digest") == ledger.get("prior_root_digest"):
        errors.append("activation ledger new root must advance")
    if ledger.get("compare_and_swap_result") != "committed":
        errors.append("activation ledger CAS must commit")
    for key in ["rollback_accepted", "forked_root_accepted", "stale_root_accepted"]:
        if ledger.get(key) is not False:
            errors.append(f"activation ledger {key} must be false")

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
            errors.append(f"successor cutover receipt leaks forbidden token {token!r}")
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
    if "check_removable_media_local_post_detach_terminal_closure_successor_cutover_receipt.py" not in hygiene:
        fail("tools/hygiene.py missing terminal closure successor cutover checker")


def main() -> int:
    example = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, example)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(example)
    if sem:
        fail("semantic terminal-closure successor cutover errors:\n- " + "\n- ".join(sem[:30]))

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
    print("removable-media post-detach terminal closure successor cutover receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

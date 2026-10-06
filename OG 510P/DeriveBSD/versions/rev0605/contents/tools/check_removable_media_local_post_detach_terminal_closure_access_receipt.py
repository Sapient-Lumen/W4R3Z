#!/usr/bin/env python3
"""Validate r531 post-detach terminal closure access receipts.

r530 stated that future access after terminal closure is denied unless new
authority is issued.  r531 makes that executable per attempt: old managed
query/export/rehydration/observation/support authority must pass through a typed
post-closure access gate receipt, advance an access ledger, debit rate limits
once, and keep support projection digest-only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from cube_digest_lib import file_json_digest, load_json

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-05-30r531"
SCHEMA = "spec/removable.media.local.post_detach.terminal.closure.access.receipt.schema.json"
EXAMPLE = "spec/examples/removable.media.local.post_detach.terminal.closure.access.receipt.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-terminal-closure-access-receipt"

SOURCE_BINDINGS = {
    "terminal_closure_capsule_computed_digest": "spec/examples/removable.media.local.post_detach.terminal.closure.capsule.json",
    "export_bundle_deletion_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.export.bundle.deletion.receipt.json",
    "denial_selection_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.denial.selection.receipt.json",
    "denial_reason_registry_computed_digest": "spec/examples/removable.media.local.post_detach.denial.reason.registry.json",
    "rate_limit_debit_ledger_receipt_computed_digest": "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json",
    "support_projection_computed_digest": "spec/examples/removable.media.local.post_detach.support.projection.json",
}

EXPECTED_INVALIDS = [
    "access-ledger-not-advanced.json",
    "export-without-new-approval.json",
    "missing-terminal-closure-binding.json",
    "observe-successor-issued-from-old-authority.json",
    "old-authority-accepted.json",
    "query-allowed-after-closure.json",
    "rate-limit-not-debited.json",
    "raw-support-visible.json",
    "rehydration-live-locator-allowed.json",
    "stale-terminal-closure-binding.json",
]

FORBIDDEN_TOKENS = ("/media/", "/Volumes/", "file://", "raw-path:", "johnny", "j30385433", "secret=", "secret.txt")

REQUIRED_DOC_TOKENS = {
    "CHANGELOG.md": [VERSION, "terminal.closure.access.receipt", "check_removable_media_local_post_detach_terminal_closure_access_receipt.py"],
    "README.md": [VERSION, "terminal-closure-access", "fresh-authority-schema-split"],
    "docs/00-index.md": [VERSION, "docs/current/removable-media-post-detach-terminal-closure-access.md"],
    "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_terminal_closure_access_receipt.py"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_terminal_closure_access_receipt.py"],
    "docs/110-juicy-os-lessons.md": ["r531 removable-media post-detach terminal-closure access gate"],
    "docs/786-removable-media-local-fallback-post-detach-terminal-closure-access-and-fresh-authority-schema-split.md": [
        "removable.media.local.post_detach.terminal.closure.access.receipt",
        "post-detach-terminal-closure-access-positive-and-negative-fixture-guarded",
        "post-detach-fresh-authority-generic-runtime-schema-plus-exact-fixture-split",
    ],
    "docs/current/removable-media-post-detach-terminal-closure-access.md": [
        "terminal-closure access gate",
        "old managed authority is denied",
        "terminal-closure-managed-authority-closed",
        "fresh-authority schema split",
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
        errors.append("terminal closure access version mismatch")
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
    support = load_json(ROOT, "spec/examples/removable.media.local.post_detach.support.projection.json")
    rate_limit = load_json(ROOT, "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json")

    attempt = obj.get("attempt", {})
    closure_digest = file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.terminal.closure.capsule.json")
    if attempt.get("terminal_closure_capsule_id") != closure.get("closure_capsule_id"):
        errors.append("attempt closure capsule id binding is stale")
    if attempt.get("terminal_closure_capsule_digest") != closure_digest:
        errors.append("attempt closure capsule digest binding is stale")
    for key in ["raw_handle_values_included", "raw_locator_values_included", "ambient_reauthentication_attempted"]:
        if attempt.get(key) is not False:
            errors.append(f"attempt {key} must be false")

    gate = obj.get("closure_gate", {})
    expected_gate = {
        "terminal_closure_checked": True,
        "terminal_closure_state": "managed-authority-terminally-closed",
        "gate_reason_code": "terminal-closure-managed-authority-closed",
        "gate_reason_source": "terminal-closure-capsule",
        "old_authority_accepted": False,
        "successor_issued_from_old_authority": False,
        "new_authority_required": True,
        "new_export_requires_new_approval": True,
        "access_outcome": "deny-post-closure-old-authority",
        "support_visibility": "support-safe-digest-only",
    }
    for key, expected in expected_gate.items():
        if gate.get(key) != expected:
            errors.append(f"closure gate {key} must be {expected!r}")

    matrix = obj.get("action_matrix", [])
    actions = [row.get("action") for row in matrix]
    required_actions = ["query", "export", "rehydrate", "observe", "managed-copy", "support-debug"]
    if sorted(actions) != sorted(required_actions):
        errors.append("action matrix must cover query/export/rehydrate/observe/managed-copy/support-debug exactly once")
    for row in matrix:
        action = row.get("action")
        if row.get("old_authority_allowed") is not False:
            errors.append(f"{action}: old authority must be denied after terminal closure")
        if row.get("new_authority_required") is not True:
            errors.append(f"{action}: new authority must be required")
        if row.get("live_locator_allowed") is not False:
            errors.append(f"{action}: live locator must not be allowed")
        if row.get("raw_support_allowed") is not False:
            errors.append(f"{action}: raw support must not be allowed")
        if row.get("support_visibility") != "support-safe-digest-only":
            errors.append(f"{action}: support visibility must be digest-only")
        if action in {"export", "managed-copy"} and row.get("approval_required") is not True:
            errors.append(f"{action}: new approval is required after terminal closure")

    rl = obj.get("rate_limit_binding", {})
    if rl.get("rate_limit_action") != "debit-post-closure-attempt":
        errors.append("post-closure access attempts must debit the rate-limit ledger")
    if rl.get("debit_count") != 1:
        errors.append("post-closure access attempt must debit exactly once")
    if rl.get("replayed_no_new_debit") is not False:
        errors.append("canonical first post-closure attempt must not be marked replayed")
    if rl.get("rate_limit_debit_receipt_digest") != file_json_digest(ROOT, "spec/examples/removable.media.local.post_detach.rate_limit.debit.ledger.receipt.json"):
        errors.append("rate-limit debit digest binding is stale")
    if rl.get("idempotency_key_digest") == rate_limit.get("idempotency", {}).get("idempotency_key_digest"):
        # It is acceptable to reuse a policy digest, but the post-closure access
        # gate needs its own attempt idempotency key so it cannot collide with the
        # earlier expiry denial debit.
        errors.append("post-closure access gate must use a distinct idempotency key from the r526 expiry debit")

    ledger = obj.get("access_ledger", {})
    if ledger.get("expected_root_digest") != ledger.get("prior_root_digest"):
        errors.append("access ledger CAS expected root must equal prior root")
    if ledger.get("new_root_digest") == ledger.get("prior_root_digest"):
        errors.append("access ledger new root must advance")
    if ledger.get("compare_and_swap_result") != "committed":
        errors.append("access ledger CAS must commit")
    for key in ["rollback_accepted", "forked_root_accepted", "stale_root_accepted"]:
        if ledger.get(key) is not False:
            errors.append(f"access ledger {key} must be false")

    projection = obj.get("support_projection", {})
    if projection.get("visibility") != support.get("visibility"):
        errors.append("support visibility must match the allowlisted support projection")
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

    for key, value in obj.get("invariants", {}).items():
        if value is not True:
            errors.append(f"invariant {key} must be true")
    text = json.dumps(obj, sort_keys=True)
    for token in FORBIDDEN_TOKENS:
        if token in text:
            errors.append(f"terminal closure access receipt leaks forbidden token {token!r}")
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
    if "check_removable_media_local_post_detach_terminal_closure_access_receipt.py" not in hygiene:
        fail("tools/hygiene.py missing terminal closure access receipt checker")


def main() -> int:
    example = load_json(ROOT, EXAMPLE)
    errs = validation_errors(SCHEMA, example)
    if errs:
        fail(f"{EXAMPLE} failed {SCHEMA}: {errs[:10]}")
    sem = semantic_errors(example)
    if sem:
        fail("semantic terminal closure access errors:\n- " + "\n- ".join(sem[:30]))

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
    print("removable-media post-detach terminal-closure access receipt check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

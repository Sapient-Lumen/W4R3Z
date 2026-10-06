#!/usr/bin/env python3
"""Guard r521 removable-media post-detach runtime state-machine hardening.

This check is deliberately semantic rather than only JSON-Schema based.  r521
adds a state-machine manifest, production/fixture split for r520 enforcement,
computed example digests, a post-expiry enforcement ledger, a fresh-authority
success path, an allowlisted support projection, and FreeBSD backend enforcement
evidence.  The checker verifies the joins that JSON Schema cannot express.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from cube_digest_lib import canonical_digest, file_json_digest as cube_file_json_digest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

VERSION = "2026-05-30r521"
LANE = "removable-media-local-fallback"
OLD_LANE_ALIAS = "removable-media-local-post-detach"

SCHEMAS = {
    "state": "spec/removable.media.local.post_detach.state_machine.manifest.schema.json",
    "ledger": "spec/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.schema.json",
    "recovery": "spec/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.schema.json",
    "support": "spec/removable.media.local.post_detach.support.projection.schema.json",
    "backend": "spec/removable.media.local.post_detach.backend.enforcement.evidence.schema.json",
    "r520_prod": "spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.schema.json",
    "r520_fixture": "spec/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.fixture.schema.json",
}
EXAMPLES = {
    "state": "spec/examples/removable.media.local.post_detach.state_machine.manifest.json",
    "ledger": "spec/examples/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.json",
    "recovery": "spec/examples/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.json",
    "support": "spec/examples/removable.media.local.post_detach.support.projection.json",
    "backend": "spec/examples/removable.media.local.post_detach.backend.enforcement.evidence.json",
    "r520": "spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.enforcement.receipt.json",
    "r519": "spec/examples/removable.media.local.post_detach.reader.use.ledger.retention.expiry.receipt.json",
}
INVALID_DIRS = {
    "state": "spec/examples/invalid/removable-media/post-detach-state-machine-manifest",
    "ledger": "spec/examples/invalid/removable-media/post-detach-expiry-enforcement-ledger-receipt",
    "recovery": "spec/examples/invalid/removable-media/post-detach-expiry-fresh-authority-recovery-receipt",
    "support": "spec/examples/invalid/removable-media/post-detach-support-projection",
    "backend": "spec/examples/invalid/removable-media/post-detach-backend-enforcement-evidence",
    "r520": "spec/examples/invalid/removable-media/post-detach-reader-use-ledger-retention-expiry-enforcement-receipt",
}
EXPECTED_INVALIDS = {
    "state": [
        "degraded-time-not-fail-closed.json",
        "fresh-authority-not-successor-only.json",
        "lane-alias-used-as-family.json",
        "missing-computed-digest-join.json",
        "support-projection-not-allowlisted.json",
    ],
    "ledger": [
        "cas-expected-mismatch.json",
        "degraded-clock-not-fail-closed.json",
        "missing-denial-reason.json",
        "rate-limit-not-debited.json",
        "raw-support-leak.json",
        "stale-root-accepted.json",
    ],
    "recovery": [
        "expired-root-admitted.json",
        "expired-root-resurrected.json",
        "fresh-authority-absent.json",
        "fresh-authority-reused.json",
        "scope-widened.json",
        "successor-root-equals-expired-root.json",
    ],
    "support": [
        "filename-in-digest-facts.json",
        "full-text-visible.json",
        "raw-locator-field.json",
        "raw-path-visible.json",
        "secret-material-visible.json",
    ],
    "backend": [
        "capsicum-missing.json",
        "devfs-node-visible.json",
        "fd-rights-broad.json",
        "raw-path-reopen-authority.json",
        "worker-not-reaped.json",
    ],
    "r520": [
        "allow-export-after-expiry.json",
        "allow-new-observation.json",
        "allow-rehydration-after-expiry.json",
        "body-text-indexed.json",
        "forked-enforcement-accepted.json",
        "fresh-authority-not-required.json",
        "full-text-indexed.json",
        "host-identity-present.json",
        "missing-expiry-receipt.json",
        "missing-rate-limit-debit.json",
        "non-monotonic-enforcement-sequence.json",
        "raw-handle-present.json",
        "raw-locator-present.json",
        "rollback-accepted.json",
        "secret-material-present.json",
        "silent-success-without-denial.json",
        "stale-root-accepted.json",
        "support-raw-payload-visible.json",
        "unbounded-retry-window.json",
        "untrusted-filename-present.json",
    ],
}
FORBIDDEN_TOKENS = ("/media/", "/Volumes/", "file://", "raw-path:", "johnny", "j30385433", "secret=", "secret.txt")


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def file_json_digest(rel: str) -> str:
    return cube_file_json_digest(ROOT, rel)


def validate(schema_rel: str, obj: Any) -> list[str]:
    validator = Draft202012Validator(load_json(schema_rel))
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require_valid(schema_rel: str, example_rel: str) -> Any:
    obj = load_json(example_rel)
    errs = validate(schema_rel, obj)
    if errs:
        fail(f"{example_rel} failed {schema_rel}: {errs[:8]}")
    return obj


def parse_z(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


def semantic_errors(kind: str, obj: Any) -> list[str]:
    errors: list[str] = []
    if kind == "state":
        if obj["generated_for_version"] != VERSION:
            errors.append("manifest version mismatch")
        if obj["lane"]["family"] != LANE:
            errors.append("lane family is not normalized to removable-media-local-fallback")
        joins = {j["example_path"]: j["computed_example_digest"] for j in obj["digest_joins"]["joins"]}
        required_paths = {s["example_path"] for s in obj["states"]}
        missing = sorted(required_paths - set(joins))
        if missing:
            errors.append(f"missing computed digest joins: {missing}")
        for path, digest in joins.items():
            p = ROOT / path
            if not p.exists():
                errors.append(f"digest join path missing: {path}")
            else:
                actual = file_json_digest(path)
                if actual != digest:
                    errors.append(f"computed digest mismatch for {path}: {digest} != {actual}")
        inv = obj["invariants"]
        for key in [
            "expired_root_never_observed_after_expiry",
            "fresh_authority_successor_only",
            "support_projection_allowlisted",
            "freebsd_backend_evidence_required",
            "computed_digest_joins_required",
            "degraded_time_fails_closed",
        ]:
            if inv.get(key) is not True:
                errors.append(f"manifest invariant {key} is not true")
    elif kind == "ledger":
        bind = obj["expired_root_binding"]
        cas = obj["enforcement_root_cas"]
        denial = obj["denial_binding"]
        rate = obj["rate_limit_binding"]
        time_proof = obj["time_proof"]
        if bind["attempted_root_digest"] != bind["expired_ledger_root_digest"]:
            errors.append("post-expiry attempt must bind the same expired root being denied")
        if bind["expiry_receipt_computed_example_digest"] != file_json_digest(EXAMPLES["r519"]):
            errors.append("r519 expiry computed digest join mismatch")
        if not (parse_z(bind["attempt_observed_at"]) >= parse_z(bind["expiry_observed_at"]) >= parse_z(bind["retention_expires_at"])):
            errors.append("time order attempt >= expiry >= retention end is false")
        if cas["expected_enforcement_root_digest"] != cas["prior_enforcement_root_digest"]:
            errors.append("CAS expected root must equal prior root")
        if cas["new_enforcement_root_digest"] == cas["prior_enforcement_root_digest"]:
            errors.append("CAS new root must differ from prior root")
        if cas["rollback_accepted"] or cas["forked_enforcement_accepted"] or cas["stale_root_accepted"]:
            errors.append("rollback/fork/stale root acceptance must remain false")
        if denial["denial_reason_code"] != "expired-ledger-root-fresh-authority-required":
            errors.append("wrong denial reason code")
        if denial["denial_subject_digest"] != bind["expired_ledger_root_digest"]:
            errors.append("denial subject must be the expired ledger root")
        if rate["debit_amount"] < 1:
            errors.append("rate limit debit must be at least 1")
        if rate["rate_limit_ledger_new_root_digest"] == rate["rate_limit_ledger_prior_root_digest"]:
            errors.append("rate-limit ledger root must advance")
        if time_proof["degraded_clock_policy"] != "fail-closed-with-typed-denial":
            errors.append("degraded clock must fail closed with typed denial")
    elif kind == "recovery":
        prior = obj["prior_denial_binding"]
        fresh = obj["fresh_authority_binding"]
        succ = obj["successor_binding"]
        admission = obj["post_recovery_admission"]
        if prior["expired_root_digest"] != succ["predecessor_expired_root_digest"]:
            errors.append("recovery predecessor must equal prior denied expired root")
        if fresh["fresh_authority_present"] is not True or fresh["consumed_once"] is not True:
            errors.append("fresh authority must be present and consumed once")
        if fresh["scope_not_widened"] is not True:
            errors.append("fresh authority scope must not widen")
        if succ["successor_root_digest"] == succ["predecessor_expired_root_digest"]:
            errors.append("successor root must differ from expired root")
        if succ["expired_root_resurrected"] is not False:
            errors.append("expired root must not be resurrected")
        if admission["root_allowed_for_observation"] != "successor-root-only" or admission["expired_root_observation_allowed"] is not False:
            errors.append("post-recovery admission must be successor-root-only")
    elif kind == "support":
        text = json.dumps(obj, sort_keys=True)
        for token in FORBIDDEN_TOKENS:
            if token in text:
                errors.append(f"support projection leaks forbidden token {token!r}")
        forbidden = obj["forbidden_surfaces"]
        for key, val in forbidden.items():
            if val is not False:
                errors.append(f"support forbidden surface {key} must be false")
        allowed_top = {"kind","schema_version","projection_id","lane","visibility","reason_code","state_label","digest_facts","retry_guidance","allowed_fields_only_ack","forbidden_surfaces"}
        extra = set(obj) - allowed_top
        if extra:
            errors.append(f"support projection has non-allowlisted top-level fields: {sorted(extra)}")
    elif kind == "backend":
        controls = obj["freebsd_controls"]
        teardown = obj["launch_teardown"]
        if controls["capsicum_capability_mode_entered"] is not True:
            errors.append("Capsicum capability mode must be entered")
        if controls["cap_rights_limited"] is not True:
            errors.append("retained fd rights must be limited")
        if controls["raw_path_reopen_authority"] is not False:
            errors.append("raw path reopen authority must be absent")
        if teardown["worker_process_reaped"] is not True:
            errors.append("worker must be reaped")
        if teardown["devfs_device_node_visible"] is not False:
            errors.append("devfs device node must not remain visible to worker")
        if teardown["raw_device_reopen_authority"] is not False:
            errors.append("raw device reopen authority must be absent")
    elif kind == "r520":
        bind = obj["expiry_binding"]
        attempt = obj["post_expiry_attempt"]
        decision = obj["enforcement_decision"]
        evidence = obj["evidence_after_enforcement"]
        if attempt["attempted_root_digest"] != bind["expired_ledger_root_digest"]:
            errors.append("r520 attempted root must equal expired root")
        if decision["fresh_authority_required"] is not True:
            errors.append("r520 must require fresh authority")
        if decision["allow_new_observation"] or decision["allow_export"] or decision["allow_rehydration"]:
            errors.append("r520 must deny new observation/export/rehydration")
        if decision["rate_limit_debited"] is not True:
            errors.append("r520 must debit rate limit")
        if decision["monotonic_enforcement_sequence"] < bind["expiry_sequence"] + 1:
            errors.append("r520 enforcement sequence must advance after expiry")
        if evidence["raw_payload_visible"] or evidence["secret_material_present"]:
            errors.append("r520 evidence must stay redacted")
    return errors


def require_invalids_fail(kind: str, schema_rel: str, dir_rel: str) -> None:
    root = ROOT / dir_rel
    names = sorted(p.name for p in root.glob("*.json"))
    expected = sorted(EXPECTED_INVALIDS[kind])
    if names != expected:
        fail(f"invalid fixture set mismatch for {kind}: {names} != {expected}")
    for path in sorted(root.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        schema_errs = validate(schema_rel, obj)
        semantic_errs: list[str] = []
        if not schema_errs:
            semantic_errs = semantic_errors(kind, obj)
        if not schema_errs and not semantic_errs:
            fail(f"invalid fixture unexpectedly passed schema+semantic checks: {path.relative_to(ROOT)}")


def require_no_old_lane_alias_in_spec() -> None:
    allowed = {
        "spec/removable.media.local.post_detach.state_machine.manifest.schema.json",
        "spec/examples/removable.media.local.post_detach.state_machine.manifest.json",
        "spec/examples/invalid/removable-media/post-detach-state-machine-manifest/lane-alias-used-as-family.json",
    }
    offenders: list[str] = []
    for path in list((ROOT / "spec").rglob("*.json")) + list((ROOT / "spec").rglob("*.schema.json")):
        rel = str(path.relative_to(ROOT))
        if rel in allowed or rel.startswith("spec/examples/invalid/removable-media/post-detach-state-machine-manifest/"):
            continue
        if OLD_LANE_ALIAS in path.read_text(encoding="utf-8", errors="replace"):
            offenders.append(rel)
    if offenders:
        fail("old post-detach lane alias remains outside the retired-alias manifest surface: " + ", ".join(offenders))


def require_r520_schema_split() -> None:
    prod = load_json(SCHEMAS["r520_prod"])
    fixture = load_json(SCHEMAS["r520_fixture"])
    prod_text = json.dumps(prod)
    if prod_text.count('"const"') > 70:
        fail("r520 production schema still looks fixture-literal; expected fewer exact consts after r521 split")
    dynamic = copy.deepcopy(load_json(EXAMPLES["r520"]))
    dynamic["enforcement_receipt_id"] = "rm-postdetach-reader-use-ledger-retention-expiry-enforcement-20260624-dynamic"
    dynamic["post_expiry_attempt"]["attempt_id"] = "rm-postdetach-post-expiry-attempt-20260624-dynamic"
    dynamic["enforcement_decision"]["decision_digest"] = "sha256:" + "ab" * 32
    dynamic["enforcement_decision"]["monotonic_enforcement_sequence"] = 50
    if validate(SCHEMAS["r520_prod"], dynamic):
        fail("r520 production schema should accept a valid dynamic receipt instance")
    if not validate(SCHEMAS["r520_fixture"], dynamic):
        fail("r520 exact fixture schema should reject a dynamic non-golden receipt")


def require_text_tokens() -> None:
    reqs = {
        "CHANGELOG.md": [VERSION, "ADR-0365", "tools/check_removable_media_local_post_detach_runtime_state_machine.py"],
        "README.md": [VERSION, "ADR-0365", "runtime-verifiable-post-detach-state-machine"],
        "docs/00-index.md": [VERSION, "docs/776-removable-media-local-fallback-post-detach-state-machine-and-post-expiry-ledgers-are-runtime-verifiable.md"],
        "docs/98-archive-hygiene.md": ["check_removable_media_local_post_detach_runtime_state_machine.py", "check_readme_latest_cut.py"],
        "docs/99-llm-runbook.md": ["check_removable_media_local_post_detach_runtime_state_machine.py", "runtime-verifiable-post-detach-state-machine"],
        "docs/110-juicy-os-lessons.md": ["r521 removable-media post-detach runtime state-machine", "runtime-verifiable-post-detach-state-machine"],
        "docs/776-removable-media-local-fallback-post-detach-state-machine-and-post-expiry-ledgers-are-runtime-verifiable.md": [
            "spec/removable.media.local.post_detach.state_machine.manifest.schema.json",
            "spec/removable.media.local.post_detach.expiry.enforcement.ledger.receipt.schema.json",
            "spec/removable.media.local.post_detach.expiry.fresh_authority.recovery.receipt.schema.json",
            "spec/removable.media.local.post_detach.support.projection.schema.json",
            "spec/removable.media.local.post_detach.backend.enforcement.evidence.schema.json",
        ],
    }
    for rel, toks in reqs.items():
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for tok in toks:
            if tok not in txt:
                fail(f"{rel} missing required r521 token {tok!r}")


def main() -> int:
    state = require_valid(SCHEMAS["state"], EXAMPLES["state"])
    ledger = require_valid(SCHEMAS["ledger"], EXAMPLES["ledger"])
    recovery = require_valid(SCHEMAS["recovery"], EXAMPLES["recovery"])
    support = require_valid(SCHEMAS["support"], EXAMPLES["support"])
    backend = require_valid(SCHEMAS["backend"], EXAMPLES["backend"])
    r520 = require_valid(SCHEMAS["r520_prod"], EXAMPLES["r520"])
    require_valid(SCHEMAS["r520_fixture"], EXAMPLES["r520"])

    for kind, obj in [("state", state), ("ledger", ledger), ("recovery", recovery), ("support", support), ("backend", backend), ("r520", r520)]:
        errs = semantic_errors(kind, obj)
        if errs:
            fail(f"semantic errors for {kind}: {errs}")

    for kind in ["state", "ledger", "recovery", "support", "backend", "r520"]:
        schema_key = "r520_prod" if kind == "r520" else kind
        require_invalids_fail(kind, SCHEMAS[schema_key], INVALID_DIRS[kind])

    # Cross-object non-circular joins.
    if recovery["prior_denial_binding"]["expired_root_digest"] != ledger["expired_root_binding"]["expired_ledger_root_digest"]:
        fail("fresh-authority recovery must refer to the exact expired root denied by the enforcement ledger")
    if support["digest_facts"]["expired_root_digest"] != ledger["expired_root_binding"]["expired_ledger_root_digest"]:
        fail("support projection must describe the same expired root denied by the enforcement ledger")
    if backend["enforcement_join"]["support_projection_digest"] != file_json_digest(EXAMPLES["support"]):
        fail("backend evidence must join to the computed support projection example digest")

    require_no_old_lane_alias_in_spec()
    require_r520_schema_split()
    require_text_tokens()

    print("removable-media post-detach runtime state-machine check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

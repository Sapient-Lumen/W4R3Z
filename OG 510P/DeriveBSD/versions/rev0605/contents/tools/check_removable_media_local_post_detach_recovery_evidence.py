#!/usr/bin/env python3
"""Guard removable-media post-detach recovery evidence.

The first host-local removable-media fallback must not treat cleanup, crash
recovery, worker reap, or output sealing as best-effort prose. Recovery
evidence is a typed artifact with positive and negative fixtures and canonical
stack wiring.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.post_detach.recovery.evidence.schema.json"
FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.recovery.evidence.fixture.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.recovery.evidence.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-recovery-evidence"
RECOVERY_POSTURE = "typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded"
RECOVERY_DIGEST = "sha256:5050505050505050505050505050505050505050505050505050505050505050"
RECOVERY_POLICY = "known-bad-recovery-evidence-shapes-must-fail-validation"
RECOVERY_KIND = "removable.media.local.post_detach.recovery.evidence"
LAUNCH_SCHEMA_REL = "spec/removable.media.local.post_detach.launch.evidence.schema.json"
CONTRACT_SCHEMA_REL = "spec/removable.media.local.post_detach.contract.schema.json"

REQUIRED_INVALID_FIXTURES = {
    "cleanup-not-observed.json",
    "persistent-scratch-replayable.json",
    "crash-scan-missing.json",
    "derivative-receipt-visible-before-recovery.json",
    "orphan-worker-survived.json",
    "output-slot-unsealed.json",
    "disk-backed-scratch-without-key-discard.json",
    "media-path-reopened.json",
}

JSON_REQUIREMENTS = {
    "spec/examples/removable.media.local.post_detach.launch.evidence.json": (
        (("recovery_evidence", "posture"), RECOVERY_POSTURE),
        (("recovery_evidence", "kind"), RECOVERY_KIND),
        (("recovery_evidence", "schema"), SCHEMA_REL),
        (("recovery_evidence", "digest"), RECOVERY_DIGEST),
        (("recovery_evidence", "negative_fixture_policy"), RECOVERY_POLICY),
        (("recovery_evidence", "crash_recovery_required"), True),
    ),
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "recovery_evidence_posture"), RECOVERY_POSTURE),
        (("backend_evidence", "recovery_evidence_kind"), RECOVERY_KIND),
        (("backend_evidence", "recovery_evidence_schema"), SCHEMA_REL),
        (("backend_evidence", "recovery_evidence_digest"), RECOVERY_DIGEST),
        (("backend_evidence", "recovery_evidence_negative_fixture_policy"), RECOVERY_POLICY),
        (("backend_evidence", "recovery_evidence_required"), True),
        (("failure_policy", "recovery_evidence_missing"), "withhold-derivative-receipt"),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_recovery_evidence_posture"), RECOVERY_POSTURE),
        (("execution", "post_detach_recovery_evidence_digest"), RECOVERY_DIGEST),
        (("execution", "post_detach_recovery_evidence_schema"), SCHEMA_REL),
        (("execution", "post_detach_recovery_evidence_negative_fixture_policy"), RECOVERY_POLICY),
        (("execution", "post_detach_recovery_evidence_required"), True),
        (("operations", 0, "params", "post_detach_recovery_evidence_posture"), RECOVERY_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_recovery_evidence_posture"), RECOVERY_POSTURE),
        (("execution", "post_detach_recovery_evidence_digest"), RECOVERY_DIGEST),
        (("execution", "post_detach_recovery_evidence_schema"), SCHEMA_REL),
        (("execution", "post_detach_recovery_evidence_negative_fixture_policy"), RECOVERY_POLICY),
        (("execution", "post_detach_recovery_evidence_required"), True),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("recovery_evidence_posture",), RECOVERY_POSTURE),
        (("recovery_evidence_digest",), RECOVERY_DIGEST),
        (("recovery_evidence_schema",), SCHEMA_REL),
        (("recovery_evidence_negative_fixture_policy",), RECOVERY_POLICY),
        (("recovery_evidence_required",), True),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_recovery_evidence_posture"), RECOVERY_POSTURE),
        (("constraints", "post_detach_recovery_evidence_digest"), RECOVERY_DIGEST),
        (("constraints", "post_detach_recovery_evidence_schema"), SCHEMA_REL),
        (("constraints", "post_detach_recovery_evidence_negative_fixture_policy"), RECOVERY_POLICY),
        (("constraints", "post_detach_recovery_evidence_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_recovery_evidence_posture"), RECOVERY_POSTURE),
        (("runtime", "mapping", "post_detach_recovery_evidence_digest"), RECOVERY_DIGEST),
        (("runtime", "mapping", "post_detach_recovery_evidence_schema"), SCHEMA_REL),
        (("runtime", "mapping", "post_detach_recovery_evidence_negative_fixture_policy"), RECOVERY_POLICY),
        (("runtime", "mapping", "post_detach_recovery_evidence_required"), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (
        "removable.media.local.post_detach.recovery.evidence",
        "crash_or_kill_semantics",
        "host_state_scan_performed",
        "persistent_replay_possible",
        "orphan_survived",
        "visible_before_recovery_validates",
        "media_path_reopen",
        "disk_backed_scratch_without_key_discard",
        "post-detach-recovery-evidence-generic-runtime-schema-plus-exact-fixture-split",
        "sha256Digest",
    ),
    FIXTURE_SCHEMA_REL: (
        "allOf",
        "const",
        RECOVERY_DIGEST,
        "historical literal regression surface",
    ),
    LAUNCH_SCHEMA_REL: (
        "recovery_evidence",
        "crash_recovery_required",
        RECOVERY_POSTURE,
    ),
    CONTRACT_SCHEMA_REL: (
        "recovery_evidence_posture",
        "recovery_evidence_digest",
        "crash_recovery_unvalidated",
    ),
    "spec/content.import.plan.schema.json": (
        "post_detach_recovery_evidence_posture",
        "post_detach_recovery_evidence_digest",
        "post_detach_recovery_evidence_schema",
        "post_detach_recovery_evidence_negative_fixture_policy",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_recovery_evidence_posture",
        "post_detach_recovery_evidence_digest",
        "post_detach_recovery_evidence_schema",
        "post_detach_recovery_evidence_negative_fixture_policy",
    ),
    "spec/preopen.map.schema.json": (
        "recovery_evidence_posture",
        "recovery_evidence_digest",
        "recovery_evidence_schema",
        "recovery_evidence_negative_fixture_policy",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/761-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md": (
        RECOVERY_POSTURE,
        RECOVERY_DIGEST,
        RECOVERY_POLICY,
        SCHEMA_REL,
        FIXTURE_SCHEMA_REL,
        EXAMPLE_REL,
        INVALID_DIR,
        "withheld-until-recovery-evidence-validates",
        "Disk-backed scratch without key discard is not ordinary-lane-admitted",
    ),
    "adrs/ADR-0350-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md": (
        RECOVERY_POSTURE,
        RECOVERY_DIGEST,
        RECOVERY_POLICY,
        SCHEMA_REL,
        FIXTURE_SCHEMA_REL,
        INVALID_DIR,
    ),
    "docs/760-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md": (
        RECOVERY_POSTURE,
        RECOVERY_DIGEST,
        SCHEMA_REL,
    ),
    "docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md": (
        RECOVERY_POSTURE,
        RECOVERY_DIGEST,
        SCHEMA_REL,
    ),
    "docs/98-archive-hygiene.md": (
        "check_removable_media_local_post_detach_recovery_evidence.py",
        RECOVERY_POSTURE,
    ),
    "docs/99-llm-runbook.md": (
        "check_removable_media_local_post_detach_recovery_evidence.py",
        RECOVERY_POSTURE,
    ),
    "docs/110-juicy-os-lessons.md": (
        "docs/761-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md",
        RECOVERY_POLICY,
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (
        RECOVERY_POSTURE,
        RECOVERY_DIGEST,
    ),
    "docs/266-open-questions-and-risk-register.md": (
        RECOVERY_POSTURE,
        RECOVERY_POLICY,
    ),
    "README.md": (
        "ADR-0350",
        RECOVERY_POSTURE,
    ),
    "docs/00-index.md": (
        "ADR-0350",
        "docs/761-removable-media-local-fallback-post-detach-recovery-evidence-is-typed-and-negative-tested.md",
        RECOVERY_POSTURE,
    ),
    "CHANGELOG.md": (
        "2026-05-21r506",
        "check_removable_media_local_post_detach_recovery_evidence.py",
        RECOVERY_POSTURE,
    ),
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def nested_value(obj, path):
    cur = obj
    for part in path:
        cur = cur[part]
    return cur


def validation_errors(validator: Draft202012Validator, obj: object) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def main() -> None:
    schema = load_json(SCHEMA_REL)
    fixture_schema = load_json(FIXTURE_SCHEMA_REL)
    example = load_json(EXAMPLE_REL)
    validator = Draft202012Validator(schema)
    fixture_validator = Draft202012Validator(fixture_schema)

    errs = validation_errors(validator, example)
    if errs:
        fail(f"{EXAMPLE_REL} must validate against {SCHEMA_REL}: {errs[:10]}")
    fixture_errs = validation_errors(fixture_validator, example)
    if fixture_errs:
        fail(f"{EXAMPLE_REL} must validate against exact fixture schema {FIXTURE_SCHEMA_REL}: {fixture_errs[:10]}")

    if schema.get("additionalProperties") is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    schema_text = (ROOT / SCHEMA_REL).read_text(encoding="utf-8")
    if schema_text.count('"const"') > 50 or '"$defs"' not in schema_text:
        fail(f"{SCHEMA_REL} must stay generic runtime-shaped after the fixture split")

    invalid_dir = ROOT / INVALID_DIR
    observed = {p.name for p in invalid_dir.glob("*.json")}
    missing = sorted(REQUIRED_INVALID_FIXTURES - observed)
    if missing:
        fail(f"missing invalid fixtures under {INVALID_DIR}: {missing}")

    for name in sorted(REQUIRED_INVALID_FIXTURES):
        rel = f"{INVALID_DIR}/{name}"
        bad = load_json(rel)
        if not validation_errors(validator, bad):
            fail(f"invalid fixture unexpectedly validates runtime schema: {rel}")
        if not validation_errors(fixture_validator, bad):
            fail(f"invalid fixture unexpectedly validates exact fixture schema: {rel}")

    for rel, reqs in JSON_REQUIREMENTS.items():
        obj = load_json(rel)
        for path, expected in reqs:
            try:
                actual = nested_value(obj, path)
            except (KeyError, IndexError, TypeError) as exc:
                fail(f"{rel} missing {'.'.join(map(str, path))}: {exc}")
            if actual != expected:
                fail(f"{rel} {'.'.join(map(str, path))} = {actual!r}, expected {expected!r}")

    for rel, fields in SCHEMA_FIELDS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for field in fields:
            if f'"{field}"' not in text and field not in text:
                fail(f"{rel} missing schema field/token {field}")

    for rel, needles in TEXT_REQUIREMENTS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                fail(f"{rel} missing {needle!r}")

    print("removable-media post-detach recovery-evidence check passed")


if __name__ == "__main__":
    main()

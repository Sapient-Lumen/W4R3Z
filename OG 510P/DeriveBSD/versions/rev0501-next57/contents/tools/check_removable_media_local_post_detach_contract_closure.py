#!/usr/bin/env python3
"""Guard removable-media post-detach contract closure.

The first host-local removable-media fallback must not rely on posture strings
alone. The ordinary post-detach worker contract has to be schema-backed,
positive-fixture validated, negative-fixture rejected, and wired into the
canonical plan/receipt/preopen/attach/detach stack.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_REL = "spec/removable.media.local.post_detach.contract.schema.json"
FIXTURE_SCHEMA_REL = "spec/removable.media.local.post_detach.contract.fixture.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.contract.json"
INVALID_DIR = "spec/examples/invalid/removable-media/post-detach-contract"

CONTRACT_CLOSURE_POSTURE = "schema-backed-positive-and-negative-fixture-guarded"
CONTRACT_DIGEST = "sha256:4848484848484848484848484848484848484848484848484848484848484848"
BACKEND_EVIDENCE_POSTURE = "receipt-must-bind-freebsd-launch-evidence-to-contract"
NEGATIVE_FIXTURE_POLICY = "known-bad-authority-shapes-must-fail-validation"

REQUIRED_INVALID_FIXTURES = {
    "home-preopen-present.json",
    "reusable-scratch-present.json",
    "casper-network-service-present.json",
    "path-reopen-allowed.json",
    "scratch-cleanup-best-effort.json",
    "undeclared-output-surface-present.json",
}

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_contract_closure_posture"), CONTRACT_CLOSURE_POSTURE),
        (("execution", "post_detach_contract_digest"), CONTRACT_DIGEST),
        (("execution", "post_detach_backend_evidence_posture"), BACKEND_EVIDENCE_POSTURE),
        (("execution", "post_detach_negative_fixture_policy"), NEGATIVE_FIXTURE_POLICY),
        (("operations", 0, "params", "post_detach_contract_closure_posture"), CONTRACT_CLOSURE_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_contract_closure_posture"), CONTRACT_CLOSURE_POSTURE),
        (("execution", "post_detach_contract_digest"), CONTRACT_DIGEST),
        (("execution", "post_detach_backend_evidence_posture"), BACKEND_EVIDENCE_POSTURE),
        (("execution", "post_detach_negative_fixture_policy"), NEGATIVE_FIXTURE_POLICY),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("contract_closure_posture",), CONTRACT_CLOSURE_POSTURE),
        (("contract_digest",), CONTRACT_DIGEST),
        (("backend_evidence_posture",), BACKEND_EVIDENCE_POSTURE),
        (("negative_fixture_policy",), NEGATIVE_FIXTURE_POLICY),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_contract_closure_posture"), CONTRACT_CLOSURE_POSTURE),
        (("constraints", "post_detach_contract_digest"), CONTRACT_DIGEST),
        (("constraints", "post_detach_backend_evidence_posture"), BACKEND_EVIDENCE_POSTURE),
        (("constraints", "post_detach_negative_fixture_policy"), NEGATIVE_FIXTURE_POLICY),
        (("constraints", "post_detach_contract_closure_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_contract_closure_posture"), CONTRACT_CLOSURE_POSTURE),
        (("runtime", "mapping", "post_detach_contract_digest"), CONTRACT_DIGEST),
        (("runtime", "mapping", "post_detach_backend_evidence_posture"), BACKEND_EVIDENCE_POSTURE),
        (("runtime", "mapping", "post_detach_negative_fixture_policy"), NEGATIVE_FIXTURE_POLICY),
        (("runtime", "mapping", "post_detach_contract_closure_required"), True),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_contract_closure_posture",
        "post_detach_contract_digest",
        "post_detach_backend_evidence_posture",
        "post_detach_negative_fixture_policy",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_contract_closure_posture",
        "post_detach_contract_digest",
        "post_detach_backend_evidence_posture",
        "post_detach_negative_fixture_policy",
    ),
    "spec/preopen.map.schema.json": (
        "contract_closure_posture",
        "contract_digest",
        "backend_evidence_posture",
        "negative_fixture_policy",
    ),
    SCHEMA_REL: (
        "removable.media.local.post_detach.contract",
        "casper_services",
        "network_descriptors",
        "mount_flags_posture",
        "disk_backed_scratch_without_key_discard",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md": (
        CONTRACT_CLOSURE_POSTURE,
        BACKEND_EVIDENCE_POSTURE,
        NEGATIVE_FIXTURE_POLICY,
        SCHEMA_REL,
        EXAMPLE_REL,
        INVALID_DIR,
        "mount flags are defense-in-depth evidence",
        "memory-backed scratch or encrypted/key-discarded scratch",
    ),
    "adrs/ADR-0348-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md": (
        CONTRACT_CLOSURE_POSTURE,
        BACKEND_EVIDENCE_POSTURE,
        NEGATIVE_FIXTURE_POLICY,
        SCHEMA_REL,
        INVALID_DIR,
    ),
    "docs/758-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md": (
        CONTRACT_CLOSURE_POSTURE,
        BACKEND_EVIDENCE_POSTURE,
        NEGATIVE_FIXTURE_POLICY,
    ),
    "docs/98-archive-hygiene.md": (
        "check_removable_media_local_post_detach_contract_closure.py",
        CONTRACT_CLOSURE_POSTURE,
    ),
    "docs/99-llm-runbook.md": (
        "check_removable_media_local_post_detach_contract_closure.py",
        CONTRACT_CLOSURE_POSTURE,
    ),
    "docs/110-juicy-os-lessons.md": (
        "docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md",
        NEGATIVE_FIXTURE_POLICY,
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (
        CONTRACT_CLOSURE_POSTURE,
        BACKEND_EVIDENCE_POSTURE,
    ),
    "docs/278-device-grants-and-devfs-rulesets.md": (
        CONTRACT_CLOSURE_POSTURE,
        BACKEND_EVIDENCE_POSTURE,
    ),
    "docs/410-desktop-viability-checklist.md": (
        CONTRACT_CLOSURE_POSTURE,
        NEGATIVE_FIXTURE_POLICY,
    ),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (
        CONTRACT_CLOSURE_POSTURE,
        NEGATIVE_FIXTURE_POLICY,
    ),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (
        CONTRACT_CLOSURE_POSTURE,
        "defense-in-depth-not-primary-exec-boundary",
    ),
    "docs/266-open-questions-and-risk-register.md": (
        CONTRACT_CLOSURE_POSTURE,
        BACKEND_EVIDENCE_POSTURE,
        NEGATIVE_FIXTURE_POLICY,
    ),
    "README.md": (
        "ADR-0348",
        CONTRACT_CLOSURE_POSTURE,
        BACKEND_EVIDENCE_POSTURE,
    ),
    "docs/00-index.md": (
        "ADR-0348",
        "docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md",
        CONTRACT_CLOSURE_POSTURE,
    ),
    "CHANGELOG.md": (
        "2026-05-21r504",
        "check_removable_media_local_post_detach_contract_closure.py",
        CONTRACT_CLOSURE_POSTURE,
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
        fail(f"{EXAMPLE_REL} must validate against exact fixture {FIXTURE_SCHEMA_REL}: {fixture_errs[:10]}")

    invalid_dir = ROOT / INVALID_DIR
    observed = {p.name for p in invalid_dir.glob("*.json")}
    missing = sorted(REQUIRED_INVALID_FIXTURES - observed)
    if missing:
        fail(f"missing invalid fixtures under {INVALID_DIR}: {missing}")

    for name in sorted(REQUIRED_INVALID_FIXTURES):
        rel = f"{INVALID_DIR}/{name}"
        bad = load_json(rel)
        if not validation_errors(validator, bad):
            fail(f"invalid fixture unexpectedly validates: {rel}")

    if schema.get("additionalProperties") is not False:
        fail(f"{SCHEMA_REL} must be closed-world at the root")
    if "allOf" not in fixture_schema:
        fail(f"{FIXTURE_SCHEMA_REL} must preserve the exact historical contract schema under allOf")

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

    print("removable-media post-detach contract-closure check passed")


if __name__ == "__main__":
    main()

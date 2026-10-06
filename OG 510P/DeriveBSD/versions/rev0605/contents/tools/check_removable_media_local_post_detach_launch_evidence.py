#!/usr/bin/env python3
"""Guard removable-media post-detach FreeBSD launch evidence.

The r504 contract requires backend evidence. This r505 guardrail makes that
backend evidence a typed FreeBSD launch object with positive and negative
fixtures, then keeps the canonical plan/receipt/preopen/attach/detach stack
pointing at the evidence posture and digest.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_REL = 'spec/removable.media.local.post_detach.launch.evidence.schema.json'
FIXTURE_SCHEMA_REL = 'spec/removable.media.local.post_detach.launch.evidence.fixture.schema.json'
EXAMPLE_REL = 'spec/examples/removable.media.local.post_detach.launch.evidence.json'
INVALID_DIR = 'spec/examples/invalid/removable-media/post-detach-launch-evidence'
CONTRACT_SCHEMA_REL = "spec/removable.media.local.post_detach.contract.schema.json"
CONTRACT_EXAMPLE_REL = "spec/examples/removable.media.local.post_detach.contract.json"

LAUNCH_EVIDENCE_POSTURE = 'typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded'
LAUNCH_EVIDENCE_DIGEST = 'sha256:4949494949494949494949494949494949494949494949494949494949494949'
LAUNCH_EVIDENCE_POLICY = 'known-bad-freebsd-launch-evidence-shapes-must-fail-validation'
CONTRACT_DIGEST = 'sha256:4848484848484848484848484848484848484848484848484848484848484848'
BACKEND_EVIDENCE_POSTURE = 'receipt-must-bind-freebsd-launch-evidence-to-contract'

REQUIRED_INVALID_FIXTURES = {
    "capability-mode-not-observed.json",
    "unexpected-fd-present.json",
    "casper-service-present.json",
    "network-descriptor-present.json",
    "parent-env-inherited.json",
    "path-search-allowed.json",
    "persistent-scratch-visible.json",
    "output-rebind-possible.json",
}

JSON_REQUIREMENTS = {
    "spec/examples/removable.media.local.post_detach.contract.json": (
        (("backend_evidence", "launch_evidence_posture"), LAUNCH_EVIDENCE_POSTURE),
        (("backend_evidence", "launch_evidence_kind"), "removable.media.local.post_detach.launch.evidence"),
        (("backend_evidence", "launch_evidence_schema"), SCHEMA_REL),
        (("backend_evidence", "launch_evidence_digest"), LAUNCH_EVIDENCE_DIGEST),
        (("backend_evidence", "launch_evidence_negative_fixture_policy"), LAUNCH_EVIDENCE_POLICY),
    ),
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        (("execution", "post_detach_launch_evidence_posture"), LAUNCH_EVIDENCE_POSTURE),
        (("execution", "post_detach_launch_evidence_digest"), LAUNCH_EVIDENCE_DIGEST),
        (("execution", "post_detach_launch_evidence_schema"), SCHEMA_REL),
        (("execution", "post_detach_launch_evidence_negative_fixture_policy"), LAUNCH_EVIDENCE_POLICY),
        (("operations", 0, "params", "post_detach_launch_evidence_posture"), LAUNCH_EVIDENCE_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        (("execution", "post_detach_launch_evidence_posture"), LAUNCH_EVIDENCE_POSTURE),
        (("execution", "post_detach_launch_evidence_digest"), LAUNCH_EVIDENCE_DIGEST),
        (("execution", "post_detach_launch_evidence_schema"), SCHEMA_REL),
        (("execution", "post_detach_launch_evidence_negative_fixture_policy"), LAUNCH_EVIDENCE_POLICY),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        (("launch_evidence_posture",), LAUNCH_EVIDENCE_POSTURE),
        (("launch_evidence_digest",), LAUNCH_EVIDENCE_DIGEST),
        (("launch_evidence_schema",), SCHEMA_REL),
        (("launch_evidence_negative_fixture_policy",), LAUNCH_EVIDENCE_POLICY),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        (("constraints", "post_detach_launch_evidence_posture"), LAUNCH_EVIDENCE_POSTURE),
        (("constraints", "post_detach_launch_evidence_digest"), LAUNCH_EVIDENCE_DIGEST),
        (("constraints", "post_detach_launch_evidence_schema"), SCHEMA_REL),
        (("constraints", "post_detach_launch_evidence_negative_fixture_policy"), LAUNCH_EVIDENCE_POLICY),
        (("constraints", "post_detach_launch_evidence_required"), True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        (("runtime", "mapping", "post_detach_launch_evidence_posture"), LAUNCH_EVIDENCE_POSTURE),
        (("runtime", "mapping", "post_detach_launch_evidence_digest"), LAUNCH_EVIDENCE_DIGEST),
        (("runtime", "mapping", "post_detach_launch_evidence_schema"), SCHEMA_REL),
        (("runtime", "mapping", "post_detach_launch_evidence_negative_fixture_policy"), LAUNCH_EVIDENCE_POLICY),
        (("runtime", "mapping", "post_detach_launch_evidence_required"), True),
    ),
}

SCHEMA_FIELDS = {
    SCHEMA_REL: (
        "removable.media.local.post_detach.launch.evidence",
        "post-detach-launch-evidence-generic-runtime-schema-plus-exact-fixture-split",
        "sha256Digest",
        "freebsd-jail-capsicum",
        "capability_mode_entered",
        "unexpected_fds",
        "casper",
        "devfs",
        "pf",
        "path_search",
        "parent_env_inherited",
        "worker_visible_persistent_path",
        "rebind_possible",
    ),
    FIXTURE_SCHEMA_REL: (
        "allOf",
        "const",
        LAUNCH_EVIDENCE_DIGEST,
        "historical literal regression surface",
    ),
    CONTRACT_SCHEMA_REL: (
        "launch_evidence_posture",
        "launch_evidence_kind",
        "launch_evidence_schema",
        "launch_evidence_digest",
        "launch_evidence_negative_fixture_policy",
    ),
    "spec/content.import.plan.schema.json": (
        "post_detach_launch_evidence_posture",
        "post_detach_launch_evidence_digest",
        "post_detach_launch_evidence_schema",
        "post_detach_launch_evidence_negative_fixture_policy",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_launch_evidence_posture",
        "post_detach_launch_evidence_digest",
        "post_detach_launch_evidence_schema",
        "post_detach_launch_evidence_negative_fixture_policy",
    ),
    "spec/preopen.map.schema.json": (
        "launch_evidence_posture",
        "launch_evidence_digest",
        "launch_evidence_schema",
        "launch_evidence_negative_fixture_policy",
    ),
}

TEXT_REQUIREMENTS = {
    'docs/760-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md': (
        LAUNCH_EVIDENCE_POSTURE,
        LAUNCH_EVIDENCE_DIGEST,
        LAUNCH_EVIDENCE_POLICY,
        SCHEMA_REL,
        FIXTURE_SCHEMA_REL,
        EXAMPLE_REL,
        INVALID_DIR,
        "fd table after `closefrom`",
        "Casper absence",
        "withheld-until-launch-evidence-validates",
    ),
    'adrs/ADR-0349-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md': (
        LAUNCH_EVIDENCE_POSTURE,
        LAUNCH_EVIDENCE_DIGEST,
        LAUNCH_EVIDENCE_POLICY,
        SCHEMA_REL,
        FIXTURE_SCHEMA_REL,
        INVALID_DIR,
    ),
    "docs/759-removable-media-local-fallback-post-detach-contract-closure-is-schema-backed-and-negative-tested.md": (
        LAUNCH_EVIDENCE_POSTURE,
        SCHEMA_REL,
    ),
    "docs/98-archive-hygiene.md": (
        "check_removable_media_local_post_detach_launch_evidence.py",
        LAUNCH_EVIDENCE_POSTURE,
    ),
    "docs/99-llm-runbook.md": (
        "check_removable_media_local_post_detach_launch_evidence.py",
        LAUNCH_EVIDENCE_POSTURE,
    ),
    "docs/110-juicy-os-lessons.md": (
        'docs/760-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md',
        LAUNCH_EVIDENCE_POLICY,
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (
        LAUNCH_EVIDENCE_POSTURE,
        LAUNCH_EVIDENCE_DIGEST,
    ),
    "docs/278-device-grants-and-devfs-rulesets.md": (
        LAUNCH_EVIDENCE_POSTURE,
        "devfs",
    ),
    "docs/410-desktop-viability-checklist.md": (
        LAUNCH_EVIDENCE_POSTURE,
        "FreeBSD launch evidence",
    ),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (
        LAUNCH_EVIDENCE_POSTURE,
        LAUNCH_EVIDENCE_POLICY,
    ),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (
        LAUNCH_EVIDENCE_POSTURE,
        "fd table after `closefrom`",
    ),
    "docs/266-open-questions-and-risk-register.md": (
        LAUNCH_EVIDENCE_POSTURE,
        LAUNCH_EVIDENCE_POLICY,
    ),
    "README.md": (
        "ADR-0349",
        LAUNCH_EVIDENCE_POSTURE,
    ),
    "docs/00-index.md": (
        "ADR-0349",
        'docs/760-removable-media-local-fallback-post-detach-freebsd-launch-evidence-is-typed-and-negative-tested.md',
        LAUNCH_EVIDENCE_POSTURE,
    ),
    "CHANGELOG.md": (
        '2026-05-21r505',
        "check_removable_media_local_post_detach_launch_evidence.py",
        LAUNCH_EVIDENCE_POSTURE,
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

    if nested_value(example, ("contract_binding", "contract_digest")) != CONTRACT_DIGEST:
        fail(f"{EXAMPLE_REL} must bind the r504 contract digest {CONTRACT_DIGEST}")

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

    print("removable-media post-detach FreeBSD launch-evidence check passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Guard removable-media local fallback post-detach executable identity.

The first host-local removable-media fallback must not regress from a
launcher-pinned executable and receipt-visible wrapper identity to PATH/cwd/media
lookup or implicit helper/plugin discovery after the process launch context is
reviewed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXEC_POSTURE = 'launcher-resolved-executable-digest-no-path-search'
WRAPPER_POSTURE = 'receipt-records-executable-and-wrapper-digests'
HELPER_POSTURE = 'no-implicit-helper-or-plugin-discovery'
EXE_DIGEST = 'sha256:abababababababababababababababababababababababababababababababab'
WRAP_DIGEST = 'sha256:bcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbcbc'
EXE_LOCATOR = 'store:sha256:abababababababababababababababababababababababababababababababab/bin/sanitize-pdf'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        ("execution", "post_detach_executable_posture", EXEC_POSTURE),
        ("execution", "post_detach_executable_locator", EXE_LOCATOR),
        ("execution", "post_detach_executable_digest", EXE_DIGEST),
        ("execution", "post_detach_wrapper_contract_digest", WRAP_DIGEST),
        ("execution", "post_detach_helper_discovery_posture", HELPER_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        ("execution", "post_detach_executable_posture", EXEC_POSTURE),
        ("execution", "post_detach_executable_locator", EXE_LOCATOR),
        ("execution", "post_detach_executable_digest", EXE_DIGEST),
        ("execution", "post_detach_wrapper_contract_digest", WRAP_DIGEST),
        ("execution", "post_detach_helper_discovery_posture", HELPER_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        ("constraints", "post_detach_executable_posture", EXEC_POSTURE),
        ("constraints", "post_detach_executable_receipt_posture", WRAPPER_POSTURE),
        ("constraints", "post_detach_helper_discovery_posture", HELPER_POSTURE),
        ("constraints", "post_detach_executable_digest_required", True),
        ("constraints", "post_detach_wrapper_contract_digest_required", True),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        ("runtime", "mapping", "post_detach_executable_posture", EXEC_POSTURE),
        ("runtime", "mapping", "post_detach_executable_locator", EXE_LOCATOR),
        ("runtime", "mapping", "post_detach_executable_digest", EXE_DIGEST),
        ("runtime", "mapping", "post_detach_executable_receipt_posture", WRAPPER_POSTURE),
        ("runtime", "mapping", "post_detach_wrapper_contract_digest", WRAP_DIGEST),
        ("runtime", "mapping", "post_detach_helper_discovery_posture", HELPER_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        ("executable_posture", EXEC_POSTURE),
        ("executable_locator", EXE_LOCATOR),
        ("executable_digest", EXE_DIGEST),
        ("wrapper_contract_digest", WRAP_DIGEST),
        ("helper_discovery_posture", HELPER_POSTURE),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_executable_posture",
        "post_detach_executable_locator",
        "post_detach_executable_digest",
        "post_detach_wrapper_contract_digest",
        "post_detach_helper_discovery_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_executable_posture",
        "post_detach_executable_locator",
        "post_detach_executable_digest",
        "post_detach_wrapper_contract_digest",
        "post_detach_helper_discovery_posture",
    ),
    "spec/preopen.map.schema.json": (
        "executable_posture",
        "executable_locator",
        "executable_digest",
        "wrapper_contract_digest",
        "helper_discovery_posture",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/750-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md": (
        EXEC_POSTURE,
        WRAPPER_POSTURE,
        HELPER_POSTURE,
        "PATH", "cwd", "digest-pinned", "wrapper contract digest",
    ),
    "adrs/ADR-0339-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md": (
        EXEC_POSTURE,
        WRAPPER_POSTURE,
        HELPER_POSTURE,
        "launcher-resolved", "digest-pinned", "plugin discovery",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (EXEC_POSTURE, WRAPPER_POSTURE, HELPER_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (EXEC_POSTURE, WRAPPER_POSTURE, HELPER_POSTURE),
    "docs/410-desktop-viability-checklist.md": (EXEC_POSTURE, WRAPPER_POSTURE, HELPER_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (EXEC_POSTURE, WRAPPER_POSTURE, HELPER_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (EXEC_POSTURE, WRAPPER_POSTURE, HELPER_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (EXEC_POSTURE, WRAPPER_POSTURE, HELPER_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_executable_identity.py", EXEC_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_executable_identity.py", EXEC_POSTURE),
    "docs/110-juicy-os-lessons.md": (EXEC_POSTURE, WRAPPER_POSTURE, HELPER_POSTURE),
    "docs/00-index.md": ("ADR-0339", "docs/750-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md", EXEC_POSTURE),
    "README.md": ("ADR-0339", "executable identity", EXEC_POSTURE),
    "CHANGELOG.md": ("2026-05-18r495", "check_removable_media_local_executable_identity.py", EXEC_POSTURE),
}

FORBIDDEN_EXECUTABLE_FRAGMENTS = (
    "$PATH",
    "path-search-enabled",
    "cwd-relative executable",
    "/ingest",
    "invoice.pdf",
    "plugin-dir-from-env",
    "media-derived-executable",
)


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def nested_value(obj, path):
    cur = obj
    for part in path:
        cur = cur[part]
    return cur


def main() -> None:
    for rel, reqs in JSON_REQUIREMENTS.items():
        obj = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        for req in reqs:
            *path, expected = req
            try:
                actual = nested_value(obj, path)
            except KeyError as exc:
                fail(f"{rel} missing {'.'.join(path)}: {exc}")
            if actual != expected:
                fail(f"{rel} {'.'.join(path)} = {actual!r}, expected {expected!r}")

    preopen = json.loads((ROOT / "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json").read_text(encoding="utf-8"))
    argv = preopen.get("argv_template", [])
    if argv and (argv[0].startswith("/") or argv[0].startswith("./") or ".." in argv[0]):
        fail(f"preopen map argv_template[0] must stay a wrapper label, not an executable path lookup: {argv[0]!r}")
    executable_surface = json.dumps({
        "argv_template": preopen.get("argv_template", []),
        "executable_locator": preopen.get("executable_locator", ""),
        "executable_posture": preopen.get("executable_posture", ""),
        "helper_discovery_posture": preopen.get("helper_discovery_posture", ""),
    }, sort_keys=True)
    for frag in FORBIDDEN_EXECUTABLE_FRAGMENTS:
        if frag in executable_surface:
            fail(f"preopen map executable/helper surface contains forbidden lookup fragment {frag!r}")

    if not preopen.get("executable_digest", "").startswith("sha256:"):
        fail("preopen map executable_digest must be sha256-shaped")
    if not preopen.get("wrapper_contract_digest", "").startswith("sha256:"):
        fail("preopen map wrapper_contract_digest must be sha256-shaped")

    for rel, fields in SCHEMA_FIELDS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for field in fields:
            if f'"{field}"' not in text:
                fail(f"{rel} missing schema field {field}")

    for rel, needles in TEXT_REQUIREMENTS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                fail(f"{rel} missing {needle!r}")

    print("removable-media local-fallback executable identity check passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Guard removable-media local fallback reviewed process launch context.

The first host-local removable-media fallback must not regress from reviewed
process startup context to inherited parent environment, media-derived argv, or
inherited cwd authority after the descriptor set has already been closed-world.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_POSTURE = 'reviewed-minimal-env-no-inherited-parent-env'
ARGV_POSTURE = 'launcher-reviewed-argv-no-media-derived-args'
CWD_POSTURE = 'launcher-owned-empty-workdir-no-ingest-store-cwd'

JSON_REQUIREMENTS = {
    "spec/examples/content.import.plan.removable-media-local-ingest.json": (
        ("execution", "post_detach_environment_posture", ENV_POSTURE),
        ("execution", "post_detach_argv_posture", ARGV_POSTURE),
        ("execution", "post_detach_cwd_posture", CWD_POSTURE),
    ),
    "spec/examples/content.import.receipt.removable-media-local-ingest.json": (
        ("execution", "post_detach_environment_posture", ENV_POSTURE),
        ("execution", "post_detach_argv_posture", ARGV_POSTURE),
        ("execution", "post_detach_cwd_posture", CWD_POSTURE),
    ),
    "spec/examples/device.attach.grant.removable-media-local-ingest.json": (
        ("constraints", "post_detach_environment_posture", ENV_POSTURE),
        ("constraints", "post_detach_argv_posture", ARGV_POSTURE),
        ("constraints", "post_detach_cwd_posture", CWD_POSTURE),
    ),
    "spec/examples/device.detach.receipt.removable-media-local-ingest.json": (
        ("runtime", "mapping", "post_detach_environment_posture", ENV_POSTURE),
        ("runtime", "mapping", "post_detach_argv_posture", ARGV_POSTURE),
        ("runtime", "mapping", "post_detach_cwd_posture", CWD_POSTURE),
    ),
    "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json": (
        ("environment_posture", ENV_POSTURE),
        ("argv_posture", ARGV_POSTURE),
        ("cwd_posture", CWD_POSTURE),
        ("cwd", "/work"),
    ),
}

SCHEMA_FIELDS = {
    "spec/content.import.plan.schema.json": (
        "post_detach_environment_posture",
        "post_detach_argv_posture",
        "post_detach_cwd_posture",
    ),
    "spec/content.import.receipt.schema.json": (
        "post_detach_environment_posture",
        "post_detach_argv_posture",
        "post_detach_cwd_posture",
    ),
    "spec/preopen.map.schema.json": (
        "environment_posture",
        "environment_allowlist",
        "argv_posture",
        "argv_template",
        "cwd_posture",
        "cwd",
    ),
}

TEXT_REQUIREMENTS = {
    "docs/749-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md": (
        ENV_POSTURE,
        ARGV_POSTURE,
        CWD_POSTURE,
        "parent environment",
        "media-derived argv",
        "launcher-owned empty scratch",
    ),
    "adrs/ADR-0338-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md": (
        ENV_POSTURE,
        ARGV_POSTURE,
        CWD_POSTURE,
        "minimal, reviewed, and not inherited from the parent",
        "argument vector is launcher-reviewed and not media-derived",
        "current working directory is launcher-owned empty scratch",
    ),
    "docs/279-usb-quarantine-and-removable-media-workflow.md": (ENV_POSTURE, ARGV_POSTURE, CWD_POSTURE),
    "docs/278-device-grants-and-devfs-rulesets.md": (ENV_POSTURE, ARGV_POSTURE, CWD_POSTURE),
    "docs/410-desktop-viability-checklist.md": (ENV_POSTURE, ARGV_POSTURE, CWD_POSTURE),
    "docs/458-removable-media-and-usb-posture-by-profile.md": (ENV_POSTURE, ARGV_POSTURE, CWD_POSTURE),
    "docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md": (ENV_POSTURE, ARGV_POSTURE, CWD_POSTURE),
    "docs/266-open-questions-and-risk-register.md": (ENV_POSTURE, ARGV_POSTURE, CWD_POSTURE),
    "docs/98-archive-hygiene.md": ("check_removable_media_local_reviewed_process_launch.py", ENV_POSTURE),
    "docs/99-llm-runbook.md": ("check_removable_media_local_reviewed_process_launch.py", ENV_POSTURE),
    "docs/110-juicy-os-lessons.md": (ENV_POSTURE, ARGV_POSTURE, CWD_POSTURE),
    "docs/00-index.md": ("ADR-0338", "docs/749-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md", ENV_POSTURE),
    "README.md": ("ADR-0338", "reviewed process-launch context", ENV_POSTURE),
    "CHANGELOG.md": ("2026-05-18r494", "check_removable_media_local_reviewed_process_launch.py", ENV_POSTURE),
}


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def nested_value(obj, path):
    current = obj
    for part in path:
        current = current[part]
    return current


def main() -> None:
    for rel, reqs in JSON_REQUIREMENTS.items():
        obj = json.loads((ROOT / rel).read_text())
        for req in reqs:
            *path, expected = req
            try:
                actual = nested_value(obj, path)
            except KeyError as exc:
                fail(f"{rel} missing {'.'.join(path)}: {exc}")
            if actual != expected:
                fail(f"{rel} {'.'.join(path)} = {actual!r}, expected {expected!r}")

    preopen = json.loads((ROOT / "spec/examples/preopen.map.removable-media-local-ingest-post-detach.json").read_text())
    allowlist = preopen.get("environment_allowlist", [])
    for name in ("DERIVE_INPUT_FD", "DERIVE_OUTPUT_FD", "DERIVE_PREOPEN_MAP_DIGEST"):
        if name not in allowlist:
            fail(f"preopen map environment_allowlist missing {name}")
    argv = preopen.get("argv_template", [])
    forbidden_argv_fragments = ("/ingest", "invoice.pdf", "../", "${", "$", "--plugin-path")
    for frag in forbidden_argv_fragments:
        if any(frag in part for part in argv):
            fail(f"preopen map argv_template contains forbidden media/ambient fragment {frag!r}: {argv!r}")

    for rel, fields in SCHEMA_FIELDS.items():
        text = (ROOT / rel).read_text()
        for field in fields:
            if f'"{field}"' not in text:
                fail(f"{rel} missing schema field {field}")

    for rel, needles in TEXT_REQUIREMENTS.items():
        text = (ROOT / rel).read_text()
        for needle in needles:
            if needle not in text:
                fail(f"{rel} missing {needle!r}")

    print("removable-media local-fallback reviewed process-launch check passed")


if __name__ == "__main__":
    main()

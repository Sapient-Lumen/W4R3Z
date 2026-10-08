#!/usr/bin/env python3
"""Validate rev0849 queue decision authorization covers every public snapshot entry."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publish_queue_item as pqi  # noqa: E402

REQUIRED_SNIPPETS = [
    "snapshot must not digest public entry-point payloads that the queue decision",
    "snapshot_entry_paths",
    "unauthorized_entries",
    "published/PUBLIC_SURFACE.json snapshot contains entry paths not authorized by decision.public_paths",
]


def fail(message: str) -> None:
    print(f"publish-queue-item-authorized-snapshot-entries-rev0849: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


@contextlib.contextmanager
def with_root(root: Path):
    old_root = pqi.ROOT
    pqi.ROOT = root
    try:
        yield
    finally:
        pqi.ROOT = old_root


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_public_surface_fixture(root: Path, entry_paths: list[str]) -> dict:
    (root / "published").mkdir(parents=True, exist_ok=True)
    for rel in set(entry_paths):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# Fixture {rel}\n", encoding="utf-8")
    write_json(
        root / "published" / "PUBLIC_SURFACE.json",
        {
            "version": 1,
            "entry_points": [{"path": rel, "role": "fixture"} for rel in entry_paths],
            "canonical_context": {"fixture": True},
            "principles": ["fixture"],
        },
    )
    with with_root(root):
        _rel, data, _manifest_sha = pqi.build_public_surface_snapshot("EV-PUB-2026-06-13-fixture", "2026-06-13", "rev9999")
    return data


def expect_system_exit(fn, label: str, expected: str) -> None:
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            fn()
    except SystemExit as exc:
        if exc.code == 0:
            fail(f"{label} exited successfully instead of failing closed")
        if expected not in stderr.getvalue():
            fail(f"{label} failed without expected diagnostic {expected!r}: {stderr.getvalue()!r}")
        return
    fail(f"{label} did not fail closed")


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publish_queue_item.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_all_snapshot_entry_points_authorized_pass() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-pqi-authz-ok-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        data = build_public_surface_fixture(root, ["published/index.md", "published/reader_guide.md"])
        public_paths = pqi.validate_decision(
            {
                "decision_id": "EV-DECISION-good",
                "status": "publish",
                "public_paths": ["published/index.md", "published/reader_guide.md"],
            },
            "EV-DECISION-good",
        )
        pqi.validate_public_paths_against_snapshot(public_paths, data)


def assert_source_manifest_may_be_authorized_explicitly() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-pqi-source-manifest-ok-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        data = build_public_surface_fixture(root, ["published/index.md"])
        public_paths = pqi.validate_decision(
            {
                "decision_id": "EV-DECISION-good",
                "status": "publish",
                "public_paths": ["published/index.md", "published/PUBLIC_SURFACE.json"],
            },
            "EV-DECISION-good",
        )
        pqi.validate_public_paths_against_snapshot(public_paths, data)


def assert_unauthorized_snapshot_entry_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-pqi-authz-extra-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        data = build_public_surface_fixture(root, ["published/index.md", "published/unapproved.md"])
        public_paths = pqi.validate_decision(
            {"decision_id": "EV-DECISION-extra", "status": "publish", "public_paths": ["published/index.md"]},
            "EV-DECISION-extra",
        )
        expect_system_exit(
            lambda: pqi.validate_public_paths_against_snapshot(public_paths, data),
            "unauthorized public-surface entry",
            "not authorized by decision.public_paths",
        )


def assert_decision_absent_from_snapshot_still_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0849-pqi-authz-missing-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        data = build_public_surface_fixture(root, ["published/index.md"])
        public_paths = pqi.validate_decision(
            {"decision_id": "EV-DECISION-missing", "status": "publish", "public_paths": ["published/index.md", "published/not-in-snapshot.md"]},
            "EV-DECISION-missing",
        )
        expect_system_exit(
            lambda: pqi.validate_public_paths_against_snapshot(public_paths, data),
            "decision path absent from snapshot",
            "absent from published/PUBLIC_SURFACE.json snapshot",
        )


def main() -> int:
    assert_static_contract()
    assert_all_snapshot_entry_points_authorized_pass()
    assert_source_manifest_may_be_authorized_explicitly()
    assert_unauthorized_snapshot_entry_blocks()
    assert_decision_absent_from_snapshot_still_blocks()
    print("publish-queue-item-authorized-snapshot-entries-rev0849: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

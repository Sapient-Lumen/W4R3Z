#!/usr/bin/env python3
"""Validate rev0848 decision public_paths / PUBLIC_SURFACE consistency checks."""
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
    "def validate_public_paths_against_snapshot",
    "decision.public_paths must be a non-empty list for publication",
    "decision.public_paths absent from published/PUBLIC_SURFACE.json snapshot",
    "published/PUBLIC_SURFACE.json snapshot contains entry paths not authorized by decision.public_paths",
    "published/PUBLIC_SURFACE.json contains duplicate entry paths",
]


def fail(message: str) -> None:
    print(f"publish-queue-item-public-path-consistency-rev0848: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_public_surface_fixture(root: Path, entry_paths: list[str]) -> None:
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


@contextlib.contextmanager
def with_root(root: Path):
    old_root = pqi.ROOT
    pqi.ROOT = root
    try:
        yield
    finally:
        pqi.ROOT = old_root


def expect_system_exit(fn, label: str) -> None:
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            fn()
    except SystemExit as exc:
        if exc.code == 0:
            fail(f"{label} exited successfully instead of failing closed")
        return
    fail(f"{label} did not fail closed")


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publish_queue_item.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def snapshot_for(root: Path, entry_paths: list[str]) -> dict:
    build_public_surface_fixture(root, entry_paths)
    with with_root(root):
        _rel, data, _manifest_sha = pqi.build_public_surface_snapshot("EV-PUB-2026-06-13-fixture", "2026-06-13", "rev9999")
    return data


def assert_declared_entries_pass() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0848-pqi-public-path-ok-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        data = snapshot_for(root, ["published/index.md", "published/reader_guide.md"])
        public_paths = pqi.validate_decision(
            {"decision_id": "EV-DECISION-good", "status": "publish", "public_paths": ["published/index.md", "published/reader_guide.md"]},
            "EV-DECISION-good",
        )
        pqi.validate_public_paths_against_snapshot(public_paths, data)


def assert_absent_public_path_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0848-pqi-public-path-missing-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        data = snapshot_for(root, ["published/index.md"])
        public_paths = pqi.validate_decision(
            {"decision_id": "EV-DECISION-missing", "status": "publish", "public_paths": ["published/not-in-surface.md"]},
            "EV-DECISION-missing",
        )
        expect_system_exit(lambda: pqi.validate_public_paths_against_snapshot(public_paths, data), "decision public_paths absent from public surface")


def assert_empty_or_duplicate_public_paths_block() -> None:
    expect_system_exit(
        lambda: pqi.validate_decision({"decision_id": "EV-DECISION-empty", "status": "publish", "public_paths": []}, "EV-DECISION-empty"),
        "empty decision public_paths",
    )
    expect_system_exit(
        lambda: pqi.validate_decision(
            {"decision_id": "EV-DECISION-dupe", "status": "publish", "public_paths": ["published/index.md", "published/index.md"]},
            "EV-DECISION-dupe",
        ),
        "duplicate decision public_paths",
    )


def assert_duplicate_public_surface_entries_block() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0848-pqi-public-surface-dupe-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        data = snapshot_for(root, ["published/index.md", "published/index.md"])
        public_paths = pqi.validate_decision(
            {"decision_id": "EV-DECISION-good", "status": "publish", "public_paths": ["published/index.md"]},
            "EV-DECISION-good",
        )
        expect_system_exit(lambda: pqi.validate_public_paths_against_snapshot(public_paths, data), "duplicate public-surface entries")


def main() -> int:
    assert_static_contract()
    assert_declared_entries_pass()
    assert_absent_public_path_blocks()
    assert_empty_or_duplicate_public_paths_block()
    assert_duplicate_public_surface_entries_block()
    print("publish-queue-item-public-path-consistency-rev0848: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

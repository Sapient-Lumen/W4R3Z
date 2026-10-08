#!/usr/bin/env python3
"""Validate rev0846 symlink closure for publish_queue_item queue metadata reads."""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publish_queue_item as pqi  # noqa: E402

REQUIRED_SNIPPETS = [
    "def first_symlink_component",
    "def fail_on_symlink_path",
    "def iter_queue_state_json_files",
    "def iter_decision_json_files",
    "QUEUE_REL_ROOT = \"release_queue\"",
    "resolves through a symlink component",
]


def fail(message: str) -> None:
    print(f"publish-queue-item-metadata-symlink-rev0846: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@contextlib.contextmanager
def with_root(root: Path):
    old_root = pqi.ROOT
    pqi.ROOT = root
    try:
        yield
    finally:
        pqi.ROOT = old_root


def expect_system_exit(fn, label: str, expected_fragment: str = "symlink") -> None:
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            fn()
    except SystemExit as exc:
        if exc.code == 0:
            fail(f"{label} exited successfully instead of failing closed")
        if expected_fragment and expected_fragment not in stderr.getvalue() and expected_fragment not in str(exc):
            fail(f"{label} failed without expected diagnostic {expected_fragment!r}: {stderr.getvalue() or exc}")
        return
    fail(f"{label} did not fail closed")


def make_release_queue_root() -> tempfile.TemporaryDirectory[str]:
    tmp = tempfile.TemporaryDirectory(prefix="ev-rev0846-pqi-metadata-link-")
    root = Path(tmp.name) / "EvidenceVault-fixture"
    for dirname in pqi.QUEUE_MAP.values():
        (root / "release_queue" / dirname).mkdir(parents=True, exist_ok=True)
    (root / "release_queue" / "decisions").mkdir(parents=True, exist_ok=True)
    return tmp


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publish_queue_item.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_clean_queue_item_can_still_be_found_by_id() -> None:
    with make_release_queue_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-fixture"
        write_json(
            root / "release_queue" / "published_ready" / "clean.json",
            {"item_id": "EV-QUEUE-clean", "date": "2026-06-13", "decision_id": "EV-DEC-clean"},
        )
        with with_root(root):
            state, path = pqi.find_item("EV-QUEUE-clean")
        if state != "published_ready" or path.name != "clean.json":
            fail(f"clean queue lookup returned unexpected result: {(state, path)}")


def assert_symlinked_queue_state_file_is_rejected_without_reading_target() -> None:
    with make_release_queue_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-fixture"
        outside = Path(tmp_name) / "outside-queue-item.json"
        write_json(outside, {"item_id": "EV-QUEUE-linked", "date": "2026-06-13", "decision_id": "EV-DEC-linked"})
        os.symlink(outside, root / "release_queue" / "published_ready" / "linked.json")
        with with_root(root):
            expect_system_exit(lambda: pqi.find_item("EV-QUEUE-linked"), "symlinked queue item")


def assert_symlinked_queue_state_directory_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0846-pqi-state-dir-link-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        (root / "release_queue").mkdir(parents=True)
        outside = Path(tmp) / "outside-published-ready"
        outside.mkdir()
        os.symlink(outside, root / "release_queue" / "published_ready")
        with with_root(root):
            expect_system_exit(lambda: list(pqi.iter_queue_state_json_files("published_ready")), "symlinked queue state directory")


def assert_symlinked_decision_file_and_changelog_are_rejected() -> None:
    with make_release_queue_root() as tmp_name:
        root = Path(tmp_name) / "EvidenceVault-fixture"
        outside_decision = Path(tmp_name) / "outside-decision.json"
        write_json(outside_decision, {"decision_id": "EV-DEC-linked", "status": "publish", "public_paths": []})
        os.symlink(outside_decision, root / "release_queue" / "decisions" / "linked.json")
        outside_changelog = Path(tmp_name) / "outside-CHANGELOG.md"
        outside_changelog.write_text("## rev9999\n", encoding="utf-8")
        os.symlink(outside_changelog, root / "CHANGELOG.md")
        with with_root(root):
            expect_system_exit(lambda: list(pqi.iter_decision_json_files()), "symlinked decision file")
            expect_system_exit(lambda: pqi.latest_revision(), "symlinked changelog")


def main() -> int:
    assert_static_contract()
    assert_clean_queue_item_can_still_be_found_by_id()
    assert_symlinked_queue_state_file_is_rejected_without_reading_target()
    assert_symlinked_queue_state_directory_is_rejected()
    assert_symlinked_decision_file_and_changelog_are_rejected()
    print("publish-queue-item-metadata-symlink-rev0846: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

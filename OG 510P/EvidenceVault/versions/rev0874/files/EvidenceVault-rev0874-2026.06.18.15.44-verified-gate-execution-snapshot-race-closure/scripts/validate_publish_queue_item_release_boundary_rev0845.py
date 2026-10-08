#!/usr/bin/env python3
"""Validate rev0845 archive-boundary hardening in publish_queue_item.py."""
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
    "DATE_RE = re.compile",
    "def clean_relative_archive_path",
    "def archive_file_path",
    "decision_id mismatch",
    "public_surface.entry_points[{idx}].path",
    "resolves through a symlink",
]


def fail(message: str) -> None:
    print(f"publish-queue-item-release-boundary-rev0845: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_public_surface_fixture(root: Path, entry_path: str = "published/index.md") -> None:
    (root / "published").mkdir(parents=True, exist_ok=True)
    (root / "published" / "index.md").write_text("# Public index\n", encoding="utf-8")
    write_json(
        root / "published" / "PUBLIC_SURFACE.json",
        {
            "version": 1,
            "entry_points": [{"path": entry_path, "role": "index"}],
            "canonical_context": {"fixture": True},
            "principles": ["fixture"],
        },
    )


def with_root(root: Path):
    @contextlib.contextmanager
    def manager():
        old_root = pqi.ROOT
        pqi.ROOT = root
        try:
            yield
        finally:
            pqi.ROOT = old_root
    return manager()


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


def assert_clean_snapshot_still_builds() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0845-pqi-clean-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        build_public_surface_fixture(root)
        with with_root(root):
            rel, data, manifest_sha = pqi.build_public_surface_snapshot("EV-PUB-2026-06-13-clean", "2026-06-13", "rev9999")
        if rel != "published/releases/snapshots/EV-PUB-2026-06-13-clean.surface.json":
            fail(f"unexpected snapshot rel: {rel}")
        if data["entry_points"][0]["path"] != "published/index.md" or len(manifest_sha) != 64:
            fail(f"clean snapshot data malformed: {data}")


def assert_public_surface_traversal_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0845-pqi-traversal-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        (Path(tmp) / "outside.txt").write_text("outside\n", encoding="utf-8")
        build_public_surface_fixture(root, "../outside.txt")
        with with_root(root):
            expect_system_exit(lambda: pqi.build_public_surface_snapshot("EV-PUB-2026-06-13-bad", "2026-06-13", "rev9999"), "public-surface traversal")


def assert_public_surface_symlink_blocks() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0845-pqi-symlink-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        build_public_surface_fixture(root, "published/leak.md")
        outside = Path(tmp) / "outside.md"
        outside.write_text("outside secret\n", encoding="utf-8")
        os.symlink(outside, root / "published" / "leak.md")
        with with_root(root):
            expect_system_exit(lambda: pqi.build_public_surface_snapshot("EV-PUB-2026-06-13-bad", "2026-06-13", "rev9999"), "public-surface symlink")


def assert_queue_and_decision_metadata_boundaries() -> None:
    expect_system_exit(
        lambda: pqi.validate_queue_item({"item_id": "EV-QUEUE-safe", "date": "2026-06-13/../../evil", "decision_id": "EV-REL-safe"}),
        "queue date traversal",
    )
    expect_system_exit(
        lambda: pqi.validate_decision({"decision_id": "EV-REL-safe", "status": "publish", "public_paths": ["published/index.md", "../secret"]}, "EV-REL-safe"),
        "decision public_paths traversal",
    )
    expect_system_exit(
        lambda: pqi.validate_decision({"decision_id": "EV-REL-other", "status": "publish", "public_paths": []}, "EV-REL-safe"),
        "decision id mismatch",
    )


def main() -> int:
    assert_static_contract()
    assert_clean_snapshot_still_builds()
    assert_public_surface_traversal_blocks()
    assert_public_surface_symlink_blocks()
    assert_queue_and_decision_metadata_boundaries()
    print("publish-queue-item-release-boundary-rev0845: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

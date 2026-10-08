#!/usr/bin/env python3
"""Validate rev0844 no-clobber publication-output creation and rollback scope."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publish_queue_item as pqi  # noqa: E402

REQUIRED_SNIPPETS = [
    "def fsync_directory",
    "os.fchmod(f.fileno(), 0o644)",
    "overwrite: bool = True",
    "os.link(tmp_path, path)",
    "raise FileExistsError(f\"target already exists: {path}\")",
    "atomic_write_bytes(target, payload, overwrite=False)",
    "prepare_publication_output_path(path, 'atomic output')",
    "target = archive_file_path(rel, 'public_surface_snapshot', must_exist=False)",
    "created_outputs: list[Path] = []",
    "created_outputs.append(snapshot_path)",
    "created_outputs.append(record_json)",
    "created_outputs.append(record_md)",
    "atomic_write_text(record_json, json.dumps(record, indent=2) + '\\n', overwrite=False)",
    "atomic_write_text(record_md, rendered_markdown, overwrite=False)",
]


def fail(message: str) -> None:
    print(f"publish-queue-item-no-clobber-rev0844: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "publish_queue_item.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_no_tmp_or_bytecode(root: Path) -> None:
    offenders = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".tmp"}
    ]
    if offenders:
        fail("transient helper files remain: " + ", ".join(offenders[:10]))


def assert_atomic_helper_no_clobber() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0844-no-clobber-helper-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        root.mkdir()
        target = root / "published" / "releases" / "record.json"
        original_root = pqi.ROOT
        try:
            pqi.ROOT = root
            pqi.atomic_write_bytes(target, b"first\n", overwrite=False)
            if target.read_bytes() != b"first\n":
                fail("initial no-clobber write did not create expected payload")
            mode = stat.S_IMODE(target.stat().st_mode)
            if mode != 0o644:
                fail(f"atomic helper created unexpected file mode {oct(mode)} instead of 0o644")
            try:
                pqi.atomic_write_bytes(target, b"second\n", overwrite=False)
            except FileExistsError as exc:
                if "target already exists" not in str(exc):
                    fail(f"no-clobber collision raised unhelpful FileExistsError: {exc}")
            else:
                fail("no-clobber helper overwrote an existing publication output")
            if target.read_bytes() != b"first\n":
                fail("no-clobber collision changed existing target bytes")
            pqi.atomic_write_bytes(target, b"replacement\n", overwrite=True)
            if target.read_bytes() != b"replacement\n":
                fail("overwrite=True replacement path did not replace target bytes")
        finally:
            pqi.ROOT = original_root
        assert_no_tmp_or_bytecode(root)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_fixture(root: Path) -> None:
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## rev9999\n\nfixture\n", encoding="utf-8")
    (root / "published" / "index.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "published" / "index.md").write_text("# Public index\n", encoding="utf-8")
    write_json(
        root / "published" / "PUBLIC_SURFACE.json",
        {
            "version": 1,
            "entry_points": [{"path": "published/index.md", "role": "index"}],
            "canonical_context": {"fixture": True},
            "principles": ["fixture"],
        },
    )
    for dirname in ["candidates", "hold", "published_ready", "published", "decisions"]:
        (root / "release_queue" / dirname).mkdir(parents=True, exist_ok=True)
    write_json(
        root / "release_queue" / "published_ready" / "2026-06-13-race-probe.json",
        {
            "item_id": "EV-QUEUE-2026-06-13-race-probe",
            "date": "2026-06-13",
            "decision_id": "EV-REL-2026-06-13-race-probe",
            "summary": "No-clobber race probe.",
        },
    )
    write_json(
        root / "release_queue" / "decisions" / "2026-06-13-race-probe.json",
        {
            "decision_id": "EV-REL-2026-06-13-race-probe",
            "status": "publish",
            "public_paths": ["published/index.md", "published/PUBLIC_SURFACE.json"],
            "summary": "No-clobber race probe decision.",
        },
    )
    scripts = root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "transition_queue_item.py").write_text("#!/usr/bin/env python3\nprint('should not run during race probe')\n", encoding="utf-8")


def assert_race_owned_record_not_removed_by_rollback() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0844-no-clobber-race-") as tmp:
        fixture = Path(tmp) / "EvidenceVault-fixture"
        fixture.mkdir()
        build_fixture(fixture)
        snapshot = fixture / "published" / "releases" / "snapshots" / "EV-PUB-2026-06-13-race-probe.surface.json"
        record_json = fixture / "published" / "releases" / "2026-06-13-race-probe.json"
        record_md = fixture / "published" / "releases" / "2026-06-13-race-probe.md"

        original_root = pqi.ROOT
        original_rights = pqi.assert_publication_rights_ready
        original_writer = pqi.write_public_surface_snapshot
        original_argv = sys.argv[:]

        def bypass_rights(_root: Path, _context: str) -> None:
            return None

        def raced_snapshot_writer(rel: str, payload: bytes) -> None:
            original_writer(rel, payload)
            record_json.parent.mkdir(parents=True, exist_ok=True)
            record_json.write_text("race-owned record\n", encoding="utf-8")

        try:
            pqi.ROOT = fixture
            pqi.assert_publication_rights_ready = bypass_rights
            pqi.write_public_surface_snapshot = raced_snapshot_writer
            sys.argv = [
                "publish_queue_item.py",
                "--item",
                "EV-QUEUE-2026-06-13-race-probe",
                "--release-slug",
                "race-probe",
            ]
            try:
                pqi.main()
            except FileExistsError:
                pass
            except SystemExit as exc:
                fail(f"race probe exited through fail() instead of no-clobber collision: {exc}")
            else:
                fail("race probe unexpectedly succeeded despite a concurrent record path")
        finally:
            pqi.ROOT = original_root
            pqi.assert_publication_rights_ready = original_rights
            pqi.write_public_surface_snapshot = original_writer
            sys.argv = original_argv

        if snapshot.exists():
            fail("rollback did not remove the snapshot created by the failed publication attempt")
        if record_json.read_text(encoding="utf-8") != "race-owned record\n":
            fail("rollback removed or changed the race-owned release record")
        if record_md.exists():
            fail("record Markdown was created after a no-clobber JSON collision")
        transition_markers = list(fixture.rglob("should-not-exist"))
        if transition_markers:
            fail("transition unexpectedly ran after no-clobber collision")
        assert_no_tmp_or_bytecode(fixture)


def assert_rev0843_validator_still_passes() -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_publish_queue_item_atomic_outputs_rev0843.py")],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        fail(f"rev0843 atomic-output validator regressed: stdout={result.stdout!r} stderr={result.stderr!r}")


def main() -> int:
    assert_static_contract()
    assert_atomic_helper_no_clobber()
    assert_race_owned_record_not_removed_by_rollback()
    assert_rev0843_validator_still_passes()
    print("publish-queue-item-no-clobber-rev0844: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

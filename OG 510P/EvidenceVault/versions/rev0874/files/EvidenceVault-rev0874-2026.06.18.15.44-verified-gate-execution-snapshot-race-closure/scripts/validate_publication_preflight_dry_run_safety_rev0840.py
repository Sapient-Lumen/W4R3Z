#!/usr/bin/env python3
"""Validate rev0840 publication preflight and queue dry-run safety."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_publication_preflight_dry_run_safety_audit_rev0840 import JSON_OUT, MD_OUT, build, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"publication-preflight-dry-run-safety-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def file_snapshot(paths: list[Path]) -> dict[str, tuple[int, str] | None]:
    out: dict[str, tuple[int, str] | None] = {}
    for path in sorted(set(paths)):
        key = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        if not path.exists():
            out[key] = None
            continue
        if path.is_file():
            out[key] = (path.stat().st_size, str(path.stat().st_mtime_ns))
    return out


def tracked_publication_files() -> list[Path]:
    roots = [
        ROOT / "published" / "releases",
        ROOT / "published" / "releases" / "artifacts",
        ROOT / "published" / "releases" / "snapshots",
        ROOT / "release_queue",
    ]
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    manifest = ROOT / "RELEASE_MANIFEST.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            bundle = ROOT.parent / data.get("bundle", "")
            files.extend([bundle, bundle.with_name(bundle.name + ".sha256")])
        except Exception:
            pass
    return files


def assert_snapshot_unchanged(label: str, before: dict[str, tuple[int, str] | None], paths: list[Path]) -> None:
    after = file_snapshot(paths)
    if after != before:
        changed = [key for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]
        fail(f"{label} changed publication files during refusal probe: {changed[:10]}")


def run_rights_blocked_probe(label: str, command: list[str], forbidden_markers: list[str]) -> None:
    tracked = tracked_publication_files()
    before = file_snapshot(tracked)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0:
        fail(f"{label} succeeded even though rights readiness blocks publication")
    if "publication rights gate blocked" not in combined:
        fail(f"{label} did not fail with publication rights gate output; tail={combined[-500:]!r}")
    for marker in forbidden_markers:
        if marker in combined:
            fail(f"{label} reached forbidden marker {marker!r} despite rights blocker")
    assert_snapshot_unchanged(label, before, tracked)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def copy_script_tree(dst_root: Path) -> None:
    scripts = dst_root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    for name in ["publish_queue_item.py", "publication_rights_gate.py"]:
        shutil.copy2(ROOT / "scripts" / name, scripts / name)


def build_minimal_rights_ready_root(dst_root: Path) -> None:
    copy_script_tree(dst_root)
    (dst_root / "LICENSE").write_text("Temporary test-only license sentinel for dry-run validator.\n", encoding="utf-8")
    write_json(
        dst_root / "RIGHTS" / "component_license_ledger.json",
        {
            "status": "publication_ready_for_validator_probe",
            "decision_required_before_publication": False,
            "blocking_findings": [],
            "root_license_or_notice_file_present": True,
        },
    )
    (dst_root / "CHANGELOG.md").write_text("# Changelog\n\n## rev9999\n\nDry-run validator fixture.\n", encoding="utf-8")
    for rel in [
        "release_queue/candidates/README.md",
        "release_queue/hold/README.md",
        "release_queue/published/README.md",
        "release_queue/published_ready/README.md",
        "release_queue/decisions/README.md",
        "published/releases/README.md",
        "published/releases/snapshots/README.md",
    ]:
        path = dst_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    (dst_root / "published" / "index.md").parent.mkdir(parents=True, exist_ok=True)
    (dst_root / "published" / "index.md").write_text("# Fixture public index\n", encoding="utf-8")
    write_json(
        dst_root / "published" / "PUBLIC_SURFACE.json",
        {
            "version": 1,
            "entry_points": [{"path": "published/index.md", "role": "landing"}],
            "canonical_context": {"scope": "validator fixture"},
            "principles": ["dry-run must not mutate"],
        },
    )
    item = {
        "item_id": "EV-QUEUE-2026-06-10-dry-run-probe",
        "date": "2026-06-10",
        "state": "published_ready",
        "scope": "validator fixture",
        "owner": "rev0840 validator",
        "decision_id": "EV-REL-2026-06-10-dry-run-probe",
        "tracked_paths": ["published/index.md", "published/PUBLIC_SURFACE.json"],
        "summary": "Dry-run safety probe.",
    }
    write_json(dst_root / "release_queue" / "published_ready" / "2026-06-10-dry-run-probe.json", item)
    write_json(
        dst_root / "release_queue" / "decisions" / "2026-06-10-dry-run-probe.json",
        {
            "decision_id": "EV-REL-2026-06-10-dry-run-probe",
            "status": "publish",
            "public_paths": ["published/index.md", "published/PUBLIC_SURFACE.json"],
            "summary": "Dry-run safety probe decision.",
        },
    )


def temp_tree_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def assert_no_temp_bytecode(root: Path) -> None:
    offenders = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.name == "__pycache__" or path.suffix == ".pyc"]
    if offenders:
        fail("dry-run temp fixture emitted bytecode: " + ", ".join(offenders[:5]))


def probe_publish_queue_dry_run_no_write() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0840-dry-run-") as tmp:
        dst = Path(tmp) / "EvidenceVault-rev9999"
        dst.mkdir()
        build_minimal_rights_ready_root(dst)
        before = temp_tree_files(dst)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"
        result = subprocess.run(
            [
                sys.executable,
                str(dst / "scripts" / "publish_queue_item.py"),
                "--item",
                "EV-QUEUE-2026-06-10-dry-run-probe",
                "--release-slug",
                "dry-run-safety",
                "--dry-run",
            ],
            cwd=dst,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            fail(f"publish_queue_item.py --dry-run failed in rights-ready fixture: stdout={result.stdout!r} stderr={result.stderr!r}")
        try:
            record = json.loads(result.stdout)
        except Exception as exc:
            fail(f"dry-run did not emit JSON release preview: {exc}; stdout={result.stdout!r}")
        expected_snapshot = "published/releases/snapshots/EV-PUB-2026-06-10-dry-run-safety.surface.json"
        if record.get("public_surface_snapshot") != expected_snapshot:
            fail("dry-run preview has unexpected public_surface_snapshot")
        after = temp_tree_files(dst)
        if after != before:
            created = sorted(after - before)
            removed = sorted(before - after)
            fail(f"publish_queue_item.py --dry-run mutated fixture tree; created={created[:10]}, removed={removed[:10]}")
        assert_no_temp_bytecode(dst)


def assert_audit_fresh() -> None:
    expected = build(ROOT)
    if expected["status"] != "publication_preflight_and_dry_run_safety_hooks_present":
        fail(expected["status"])
    if not JSON_OUT.is_file() or not MD_OUT.is_file():
        fail("rev0840 audit files are missing")
    try:
        actual = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid {JSON_OUT.relative_to(ROOT).as_posix()}: {exc}")
    if actual != expected:
        fail(f"{JSON_OUT.relative_to(ROOT).as_posix()} is stale")
    if MD_OUT.read_text(encoding="utf-8") != render_markdown(expected):
        fail(f"{MD_OUT.relative_to(ROOT).as_posix()} is stale")


def main() -> int:
    assert_audit_fresh()
    run_rights_blocked_probe(
        "publish_preflight.sh",
        ["bash", str(ROOT / "scripts" / "publish_preflight.sh")],
        ["gate: OK", "runner: START", "preflight: OK"],
    )
    run_rights_blocked_probe(
        "make release-ledgers",
        ["make", "release-ledgers"],
        ["queue-index: OK", "release-ledger: OK", "materialize-public-release: OK"],
    )
    probe_publish_queue_dry_run_no_write()
    print("publication-preflight-dry-run-safety-validate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

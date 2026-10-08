#!/usr/bin/env python3
"""Validate rev0843 atomic/rollback behavior for publish_queue_item.py outputs."""
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
SCRIPT = ROOT / "scripts" / "publish_queue_item.py"

REQUIRED_SNIPPETS = [
    "def atomic_write_bytes",
    "tempfile.mkstemp",
    "os.fsync",
    "os.replace",
    "def fsync_directory",
    "overwrite: bool = True",
    "os.link(tmp_path, path)",
    "def remove_created_outputs",
    "created_outputs: list[Path] = []",
    "created_outputs.append(snapshot_path)",
    "created_outputs.append(record_json)",
    "created_outputs.append(record_md)",
    "remove_created_outputs(created_outputs)",
    "public release snapshot already exists",
]


def fail(msg: str) -> None:
    print(f"publish-queue-item-atomic-outputs-rev0843: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def assert_static_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_fixture(root: Path, transition_body: str) -> None:
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPT, root / "scripts" / "publish_queue_item.py")
    (root / "scripts" / "publication_rights_gate.py").write_text(
        "def assert_publication_rights_ready(root, context):\n    return None\n",
        encoding="utf-8",
    )
    (root / "scripts" / "transition_queue_item.py").write_text(transition_body, encoding="utf-8")
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## rev9999\n\nfixture\n", encoding="utf-8")
    (root / "published").mkdir(parents=True, exist_ok=True)
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
        root / "release_queue" / "published_ready" / "2026-06-12-atomic-probe.json",
        {
            "item_id": "EV-QUEUE-2026-06-12-atomic-probe",
            "date": "2026-06-12",
            "decision_id": "EV-REL-2026-06-12-atomic-probe",
            "summary": "Atomic output probe.",
        },
    )
    write_json(
        root / "release_queue" / "decisions" / "2026-06-12-atomic-probe.json",
        {
            "decision_id": "EV-REL-2026-06-12-atomic-probe",
            "status": "publish",
            "public_paths": ["published/index.md", "published/PUBLIC_SURFACE.json"],
            "summary": "Atomic output probe decision.",
        },
    )


def assert_no_bytecode(root: Path) -> None:
    offenders = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.name == "__pycache__" or path.suffix == ".pyc"]
    if offenders:
        fail("fixture emitted bytecode: " + ", ".join(offenders[:10]))


def release_outputs(root: Path) -> list[Path]:
    return [
        root / "published" / "releases" / "snapshots" / "EV-PUB-2026-06-12-atomic-output-probe.surface.json",
        root / "published" / "releases" / "2026-06-12-atomic-output-probe.json",
        root / "published" / "releases" / "2026-06-12-atomic-output-probe.md",
    ]


def run_publish(root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    return subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "publish_queue_item.py"),
            "--item",
            "EV-QUEUE-2026-06-12-atomic-probe",
            "--release-slug",
            "atomic-output-probe",
        ],
        cwd=root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )


def probe_transition_failure_rolls_back_outputs() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0843-publish-rollback-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        transition = "#!/usr/bin/env python3\nimport sys\nprint('transition fixture fails')\nsys.exit(7)\n"
        build_fixture(root, transition)
        result = run_publish(root)
        if result.returncode == 0:
            fail("publish_queue_item.py unexpectedly succeeded with failing transition fixture")
        if "rolled back created outputs" not in result.stderr or "returned non-zero exit status 7" not in result.stderr:
            fail(f"failing transition did not surface rollback/nonzero status; stderr={result.stderr!r}")
        leftover = [path.relative_to(root).as_posix() for path in release_outputs(root) if path.exists()]
        if leftover:
            fail("post-transition failure left publication outputs: " + ", ".join(leftover))
        temps = [path.relative_to(root).as_posix() for path in root.rglob("*.tmp")]
        if temps:
            fail("temporary atomic output files left behind: " + ", ".join(temps))
        assert_no_bytecode(root)


def probe_successful_transition_emits_all_outputs() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0843-publish-success-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        transition = "#!/usr/bin/env python3\nprint('transition fixture ok')\n"
        build_fixture(root, transition)
        result = run_publish(root)
        if result.returncode != 0:
            fail(f"publish_queue_item.py failed with successful transition fixture: stdout={result.stdout!r} stderr={result.stderr!r}")
        missing = [path.relative_to(root).as_posix() for path in release_outputs(root) if not path.is_file()]
        if missing:
            fail("successful transition did not emit outputs: " + ", ".join(missing))
        record = json.loads((root / "published" / "releases" / "2026-06-12-atomic-output-probe.json").read_text(encoding="utf-8"))
        if record.get("status") != "published":
            fail("record JSON did not declare published status")
        assert_no_bytecode(root)


def main() -> int:
    assert_static_contract()
    probe_transition_failure_rolls_back_outputs()
    probe_successful_transition_emits_all_outputs()
    print("publish-queue-item-atomic-outputs-rev0843: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

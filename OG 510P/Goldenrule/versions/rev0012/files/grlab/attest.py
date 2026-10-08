from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_hex(b: bytes) -> str:
    return sha256(b).hexdigest()


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class RunAttestation:
    schema_version: int
    created_at: str
    run_id: str | None
    definitions_hash: str | None
    git_head: str | None
    engine_bin: str | None
    engine_bin_sha256: str | None
    python_version: str
    manifest_sha256: str | None
    report_sha256: str | None
    queue_db_sha256: str | None
    artifacts_tree_sha256: str | None
    n_artifacts: int


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _engine_bin_path(repo_root: Path) -> Path:
    override = os.environ.get("GRLAB_ENGINE_BIN", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (repo_root / "target" / "debug" / "gr-engine").resolve()


def _try_git_head(repo_root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
            text=True,
        )
        head = proc.stdout.strip()
        return head if head else None
    except Exception:  # noqa: BLE001
        return None


def _artifacts_tree_sha256(run_dir: Path) -> str | None:
    artifacts_dir = (run_dir / "artifacts").resolve()
    if not artifacts_dir.exists() or not artifacts_dir.is_dir():
        return None

    entries: list[tuple[str, str]] = []
    for p in sorted(artifacts_dir.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(run_dir).as_posix()
        entries.append((rel, _sha256_hex(_read_bytes(p))))

    payload = json.dumps(entries, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_hex(payload)


def attest_run_dir(
    run_dir: Path, include_queue_db: bool = True, include_artifacts: bool = False
) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    manifest_path = run_dir / "manifest.json"
    report_path = run_dir / "report.json"
    queue_path = run_dir / "queue.sqlite3"

    manifest = _read_json(manifest_path) if manifest_path.exists() else {}
    run_id = manifest.get("run_id") if isinstance(manifest, dict) else None
    definitions_hash = manifest.get("definitions_hash") if isinstance(manifest, dict) else None
    if not isinstance(run_id, str):
        run_id = None
    if not isinstance(definitions_hash, str):
        definitions_hash = None

    manifest_sha256 = _sha256_hex(_read_bytes(manifest_path)) if manifest_path.exists() else None
    report_sha256 = _sha256_hex(_read_bytes(report_path)) if report_path.exists() else None
    queue_db_sha256 = None
    if include_queue_db and queue_path.exists():
        queue_db_sha256 = _sha256_hex(_read_bytes(queue_path))

    repo_root = _repo_root()
    git_head = _try_git_head(repo_root)
    engine_bin_path = _engine_bin_path(repo_root)
    engine_bin = str(engine_bin_path) if engine_bin_path.exists() else None
    engine_bin_sha256 = (
        _sha256_hex(_read_bytes(engine_bin_path)) if engine_bin_path.exists() else None
    )

    artifacts_tree_sha256 = _artifacts_tree_sha256(run_dir) if include_artifacts else None

    n_artifacts = 0
    if report_path.exists():
        report = _read_json(report_path)
        rows = report.get("rows") if isinstance(report, dict) else None
        if isinstance(rows, list):
            n_artifacts = len(rows)

    att = RunAttestation(
        schema_version=3,
        created_at=_utc_now(),
        run_id=run_id,
        definitions_hash=definitions_hash,
        git_head=git_head,
        engine_bin=engine_bin,
        engine_bin_sha256=engine_bin_sha256,
        python_version=sys.version.split()[0],
        manifest_sha256=manifest_sha256,
        report_sha256=report_sha256,
        queue_db_sha256=queue_db_sha256,
        artifacts_tree_sha256=artifacts_tree_sha256,
        n_artifacts=n_artifacts,
    )
    return {
        "schema_version": att.schema_version,
        "created_at": att.created_at,
        "run_id": att.run_id,
        "definitions_hash": att.definitions_hash,
        "git_head": att.git_head,
        "engine_bin": att.engine_bin,
        "engine_bin_sha256": att.engine_bin_sha256,
        "python_version": att.python_version,
        "manifest_sha256": att.manifest_sha256,
        "report_sha256": att.report_sha256,
        "queue_db_sha256": att.queue_db_sha256,
        "artifacts_tree_sha256": att.artifacts_tree_sha256,
        "n_artifacts": att.n_artifacts,
    }

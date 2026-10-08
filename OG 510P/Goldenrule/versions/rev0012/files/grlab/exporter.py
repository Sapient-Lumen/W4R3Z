from __future__ import annotations

import json
import re
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from grlab.attest import attest_run_dir


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


@dataclass(frozen=True)
class PublicExportResult:
    redacted_dir: Path | None
    bundle_path: Path | None


@dataclass(frozen=True)
class _CompiledRegex:
    pattern: str
    regex: re.Pattern[str]


@dataclass(frozen=True)
class PublicExportDenylist:
    deny_strategy_id: tuple[_CompiledRegex, ...]
    deny_task_id: tuple[_CompiledRegex, ...]
    deny_run_id: tuple[_CompiledRegex, ...]
    deny_world_id: tuple[_CompiledRegex, ...]


def _compile_regex_list(patterns: Any, label: str) -> tuple[_CompiledRegex, ...]:
    if patterns is None:
        return tuple()
    if not isinstance(patterns, list):
        raise ValueError(f"denylist.{label} must be a list of regex strings")
    out: list[_CompiledRegex] = []
    for p in patterns:
        if not isinstance(p, str) or not p:
            raise ValueError(f"denylist.{label} must contain only non-empty strings")
        try:
            out.append(_CompiledRegex(pattern=p, regex=re.compile(p)))
        except re.error as e:
            raise ValueError(f"invalid denylist regex in {label}: {p}: {e}") from e
    return tuple(out)


def _load_public_export_denylist(path: Path) -> PublicExportDenylist:
    obj = _read_json(path)
    if not isinstance(obj, dict):
        raise ValueError(f"denylist is not an object: {path}")
    if int(obj.get("schema_version", 0)) != 1:
        raise ValueError(f"unsupported denylist schema_version: {path}")
    deny = obj.get("deny", {})
    if deny is None:
        deny = {}
    if not isinstance(deny, dict):
        raise ValueError(f"denylist.deny is not an object: {path}")

    return PublicExportDenylist(
        deny_strategy_id=_compile_regex_list(deny.get("strategy_id_regex"), "strategy_id_regex"),
        deny_task_id=_compile_regex_list(deny.get("task_id_regex"), "task_id_regex"),
        deny_run_id=_compile_regex_list(deny.get("run_id_regex"), "run_id_regex"),
        deny_world_id=_compile_regex_list(deny.get("world_id_regex"), "world_id_regex"),
    )


def _denylist_matches_str(value: str, patterns: tuple[_CompiledRegex, ...]) -> list[str]:
    hits: list[str] = []
    for pr in patterns:
        if pr.regex.search(value):
            hits.append(pr.pattern)
    return hits


def _public_export_block_reasons(
    manifest: Any, denylist: PublicExportDenylist
) -> list[str]:
    if not isinstance(manifest, dict):
        return ["manifest.json is not an object (cannot apply denylist)"]

    reasons: list[str] = []

    run_id = manifest.get("run_id")
    if isinstance(run_id, str) and run_id:
        hits = _denylist_matches_str(run_id, denylist.deny_run_id)
        for pat in hits:
            reasons.append(f"run_id matched denylist regex: {pat}: {run_id}")

    world_id = manifest.get("world_id")
    if isinstance(world_id, str) and world_id:
        hits = _denylist_matches_str(world_id, denylist.deny_world_id)
        for pat in hits:
            reasons.append(f"world_id matched denylist regex: {pat}: {world_id}")

    defs = manifest.get("definitions", {})
    if defs is None:
        defs = {}
    if isinstance(defs, dict):
        strategies = defs.get("strategies", [])
        if isinstance(strategies, list):
            for s in strategies:
                if not isinstance(s, dict):
                    continue
                sid = s.get("id")
                if not isinstance(sid, str) or not sid:
                    continue
                hits = _denylist_matches_str(sid, denylist.deny_strategy_id)
                for pat in hits:
                    reasons.append(f"strategy_id matched denylist regex: {pat}: {sid}")

    tasks = manifest.get("tasks", [])
    if isinstance(tasks, list):
        for t in tasks:
            if not isinstance(t, dict):
                continue
            tid = t.get("task_id")
            if not isinstance(tid, str) or not tid:
                continue
            hits = _denylist_matches_str(tid, denylist.deny_task_id)
            for pat in hits:
                reasons.append(f"task_id matched denylist regex: {pat}: {tid}")

    reasons.sort()
    return reasons


def redact_run_public(
    run_dir: Path,
    out_dir: Path,
    report: dict[str, Any],
    denylist_path: Path | None = None,
    allow_sensitive: bool = False,
) -> PublicExportResult:
    run_dir = run_dir.resolve()
    out_dir = out_dir.resolve()
    if out_dir.exists():
        raise FileExistsError(f"out_dir already exists: {out_dir}")

    manifest = _read_json(run_dir / "manifest.json")
    if denylist_path is not None and denylist_path.exists() and not allow_sensitive:
        denylist = _load_public_export_denylist(denylist_path.resolve())
        reasons = _public_export_block_reasons(manifest, denylist)
        if reasons:
            msg = "public export blocked by denylist:\n" + "\n".join(f"- {r}" for r in reasons)
            raise PermissionError(msg)
    tasks = manifest.get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []

    out_dir.mkdir(parents=True, exist_ok=True)

    public_manifest: dict[str, Any] = {
        "schema_version": 1,
        "kind": "public_export_manifest",
        "run_id": manifest.get("run_id"),
        "schema_version_run": manifest.get("schema_version", 1),
        "experiment_hash": manifest.get("experiment_hash"),
        "definitions_hash": manifest.get("definitions_hash"),
        "world_id": manifest.get("world_id"),
        "replications": manifest.get("replications"),
        "trace_rounds": manifest.get("trace_rounds"),
        "tasks": [],
    }

    artifacts_dir = out_dir / "artifacts"
    for t in tasks:
        if not isinstance(t, dict):
            continue
        key = t.get("key")
        task_id = t.get("task_id")
        artifact_path = t.get("artifact_path")
        if not isinstance(artifact_path, str) or not artifact_path:
            continue
        src_art = (run_dir / artifact_path).resolve()
        if not src_art.exists():
            continue
        rel_art = Path(artifact_path)
        dst_art = (artifacts_dir / rel_art.name).resolve()
        dst_art.parent.mkdir(parents=True, exist_ok=True)

        obj = _read_json(src_art)
        if isinstance(obj, dict) and "trace" in obj:
            obj["trace"] = None
        _write_json(dst_art, obj)

        public_manifest["tasks"].append(
            {"key": key, "task_id": task_id, "artifact_path": str(Path("artifacts") / rel_art.name)}
        )

    public_report = dict(report)
    public_report["experiment"] = None
    _write_json(out_dir / "manifest.json", public_manifest)
    _write_json(out_dir / "report.json", public_report)
    _write_json(
        out_dir / "attestation.json",
        attest_run_dir(out_dir, include_queue_db=False, include_artifacts=True),
    )
    return PublicExportResult(redacted_dir=out_dir, bundle_path=None)


def export_run_public_tar(
    run_dir: Path,
    out_path: Path,
    report: dict[str, Any],
    denylist_path: Path | None = None,
    allow_sensitive: bool = False,
) -> PublicExportResult:
    run_dir = run_dir.resolve()
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td).resolve()
        redacted = tmp / "public"
        _ = redact_run_public(
            run_dir=run_dir,
            out_dir=redacted,
            report=report,
            denylist_path=denylist_path,
            allow_sensitive=allow_sensitive,
        )
        with tarfile.open(str(out_path), "w:gz") as tf:
            for p in sorted(redacted.rglob("*")):
                if p.is_dir():
                    continue
                tf.add(str(p), arcname=str(p.relative_to(redacted)))
    return PublicExportResult(redacted_dir=None, bundle_path=out_path)


def export_run_internal_tar(run_dir: Path, out_path: Path) -> Path:
    run_dir = run_dir.resolve()
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(str(out_path), "w:gz") as tf:
        for p in sorted(run_dir.rglob("*")):
            if p.is_dir():
                continue
            tf.add(str(p), arcname=str(p.relative_to(run_dir)))

        att = attest_run_dir(run_dir, include_queue_db=True)
        att_bytes = json.dumps(att, indent=2, sort_keys=True).encode("utf-8")
        ti = tarfile.TarInfo(name="attestation.json")
        ti.size = len(att_bytes)
        ti.mtime = 0
        import io

        tf.addfile(ti, io.BytesIO(att_bytes))

    return out_path

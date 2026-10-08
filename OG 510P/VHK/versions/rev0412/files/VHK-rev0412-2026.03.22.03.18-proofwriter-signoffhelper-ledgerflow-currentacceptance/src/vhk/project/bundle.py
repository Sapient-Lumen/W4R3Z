from __future__ import annotations

import hashlib
import json
import os
import stat
import time
import zipfile
from pathlib import Path
from typing import Any

import yaml

from vhk import __version__
from vhk.project.claim_pack import audit_target_claims, build_claim_plan

_ZIP_EPOCH_FLOOR = 315532800  # 1980-01-01T00:00:00Z


def _parse_source_date_epoch(value: str | None) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        epoch = int(text)
    except Exception as exc:
        raise ValueError(f"Invalid SOURCE_DATE_EPOCH: {value!r}") from exc
    if epoch < 0:
        raise ValueError(f"Invalid SOURCE_DATE_EPOCH: {value!r}")
    return epoch


def _zip_datetime_tuple(epoch: int) -> tuple[int, int, int, int, int, int]:
    clamped = max(int(epoch), _ZIP_EPOCH_FLOOR)
    t = time.gmtime(clamped)
    return (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


def _iso_utc(epoch: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(epoch)))


def _normalized_epoch(*, deterministic: bool, source_date_epoch: int | None, discovered: list[tuple[str, Path]]) -> int | None:
    env_epoch = _parse_source_date_epoch(os.environ.get("SOURCE_DATE_EPOCH"))
    epoch = source_date_epoch if source_date_epoch is not None else env_epoch
    if epoch is not None:
        return int(epoch)
    if not deterministic:
        return None
    latest = 0
    for _, abs_path in discovered:
        try:
            latest = max(latest, int(abs_path.stat().st_mtime))
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Bundle input disappeared: {abs_path}") from exc
    return latest


def _stable_zipinfo(path: str, epoch: int, *, mode: int = 0o644) -> zipfile.ZipInfo:
    zi = zipfile.ZipInfo(filename=path, date_time=_zip_datetime_tuple(epoch))
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.create_system = 3  # Unix
    zi.external_attr = (stat.S_IFREG | mode) << 16
    return zi


def _load_claim_rows(claims_file: Path) -> list[dict[str, Any]]:
    payload = yaml.safe_load(claims_file.read_text()) or {}
    if not isinstance(payload, dict):
        raise ValueError("Target claims file must be a mapping")
    rows = payload.get("target_claims") or []
    if not isinstance(rows, list):
        raise ValueError("Target claims file 'target_claims' must be a list")
    return [dict(item) for item in rows if isinstance(item, dict)]


def _build_bundle_support_metadata(project_dir: Path, *, discovered: list[tuple[str, Path]]) -> dict[str, Any] | None:
    manifest_path = project_dir / "project.yaml"
    if not manifest_path.exists():
        return None

    files_in_bundle = {rel for rel, _ in discovered}
    try:
        from vhk.project.support_posture import (
            load_or_build_release_deploy_plan,
            load_or_build_release_lane_plan,
            summarize_release_deploy_posture,
            summarize_release_lane_posture,
        )

        plan = build_claim_plan(project_dir)
        recommended = {
            str(item.get("target") or ""): dict(item)
            for item in list(plan.get("recommended_claims") or [])
            if isinstance(item, dict) and str(item.get("target") or "")
        }
        claims_file = project_dir / "docs" / "VHK_TARGET_CLAIMS.yaml"
        claim_source = "planner_recommendations"
        audit_summary: dict[str, Any] | None = None
        audit_by_target: dict[str, dict[str, Any]] = {}

        if claims_file.exists():
            claim_source = "claims_file"
            claim_rows = _load_claim_rows(claims_file)
            audit = audit_target_claims(project_dir, claims_file=claims_file)
            audit_summary = dict(audit.get("summary") or {})
            audit_by_target = {
                str(item.get("target") or ""): dict(item)
                for item in list(audit.get("results") or [])
                if isinstance(item, dict) and str(item.get("target") or "")
            }
        else:
            claim_rows = [dict(item) for item in recommended.values()]

        targets: list[dict[str, Any]] = []
        level_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}

        for row in claim_rows:
            target = str(row.get("target") or "").strip()
            if not target:
                continue
            rec = recommended.get(target, {})
            claim_level = str(row.get("claim_level") or row.get("recommended_level") or "unsupported").strip().lower()
            recommended_level = str(rec.get("recommended_level") or row.get("recommended_level") or "unsupported").strip().lower()
            required_artifacts = [str(x) for x in list(row.get("required_artifacts") or rec.get("required_artifacts") or []) if str(x)]
            artifacts_present = [path for path in required_artifacts if path in files_in_bundle]
            artifacts_missing = [path for path in required_artifacts if path not in files_in_bundle]
            audit_row = audit_by_target.get(target, {})
            status = str(audit_row.get("status") or ("recommended" if claim_source != "claims_file" else "unknown"))
            level_counts[claim_level] = level_counts.get(claim_level, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
            targets.append(
                {
                    "target": target,
                    "title": str(row.get("title") or rec.get("title") or target),
                    "score": int(rec.get("score") or row.get("score") or 0),
                    "fit": str(rec.get("fit") or row.get("fit") or "unknown"),
                    "claim_level": claim_level,
                    "recommended_level": recommended_level,
                    "status": status,
                    "evidence_status": str(row.get("evidence_status") or "").strip().lower() or None,
                    "required_artifact_count": len(required_artifacts),
                    "artifacts_present": artifacts_present,
                    "artifacts_missing": artifacts_missing,
                    "issues": [str(x) for x in list(audit_row.get("issues") or []) if str(x)],
                    "warnings": [str(x) for x in list(audit_row.get("warnings") or []) if str(x)],
                }
            )

        targets.sort(key=lambda item: (-(int(item.get("score") or 0)), str(item.get("title") or "")))
        publish_doc_paths = [
            "docs/VHK_PUBLIC_SUPPORT.md",
            "docs/VHK_INSTALL_QUICKSTART.md",
            "docs/VHK_PUBLISH_PLAN.json",
        ]
        publish_docs_present = [path for path in publish_doc_paths if path in files_in_bundle]
        publish_docs_missing = [path for path in publish_doc_paths if path not in files_in_bundle]
        release_lane_plan = load_or_build_release_lane_plan(project_dir, prefer_cached=True)
        release_lane_overview = summarize_release_lane_posture(release_lane_plan)
        release_doc_paths = [str(x) for x in list(release_lane_overview.get("docs") or []) if str(x)]
        release_docs_present = [path for path in release_doc_paths if path in files_in_bundle]
        release_docs_missing = [path for path in release_doc_paths if path not in files_in_bundle]
        release_deploy_plan = load_or_build_release_deploy_plan(project_dir, prefer_cached=True)
        release_deploy_overview = summarize_release_deploy_posture(release_deploy_plan)
        release_deploy_doc_paths = [str(x) for x in list(release_deploy_overview.get("docs") or []) if str(x)]
        release_deploy_docs_present = [path for path in release_deploy_doc_paths if path in files_in_bundle]
        release_deploy_docs_missing = [path for path in release_deploy_doc_paths if path not in files_in_bundle]
        return {
            "claim_source": claim_source,
            "claims_file_present": claims_file.exists(),
            "project_name": str((plan.get("project") or {}).get("name") or project_dir.name),
            "claim_summary": dict(plan.get("claim_summary") or {}),
            "audit_summary": audit_summary,
            "target_count": len(targets),
            "level_counts": level_counts,
            "status_counts": status_counts,
            "targets": targets,
            "publish_docs_present": publish_docs_present,
            "publish_docs_missing": publish_docs_missing,
            "publish_pack_present": len(publish_docs_present) == len(publish_doc_paths),
            "release_lane_overview": release_lane_overview,
            "release_docs_present": release_docs_present,
            "release_docs_missing": release_docs_missing,
            "release_lane_pack_present": bool(release_doc_paths) and len(release_docs_present) == len(release_doc_paths),
            "release_deploy_overview": release_deploy_overview,
            "release_deploy_docs_present": release_deploy_docs_present,
            "release_deploy_docs_missing": release_deploy_docs_missing,
            "release_deploy_pack_present": bool(release_deploy_doc_paths) and len(release_deploy_docs_present) == len(release_deploy_doc_paths),
            "review_commands": [str(x) for x in list(plan.get("claim_commands") or []) if str(x)][:8],
        }
    except Exception as exc:
        return {
            "claim_source": "unavailable",
            "error": str(exc),
            "project_name": project_dir.name,
        }


def _discover_bundle_inputs(project_dir: Path, *, exclude_prefixes: set[str] | None = None) -> list[tuple[str, Path]]:
    exclude_prefixes = set(exclude_prefixes or set())
    discovered: list[tuple[str, Path]] = []

    for root, dirs, fns in os.walk(project_dir):
        rel_root = Path(root).relative_to(project_dir).as_posix()
        if rel_root == ".":
            rel_root = ""
        if rel_root and not rel_root.endswith("/"):
            rel_root += "/"

        dirs[:] = sorted([d for d in dirs if f"{rel_root}{d}/" not in exclude_prefixes and not d.startswith(".")])
        for fn in sorted(fns):
            if fn.startswith("."):
                continue
            rel_path = f"{rel_root}{fn}" if rel_root else fn
            if any(rel_path.startswith(p) for p in exclude_prefixes):
                continue
            discovered.append((rel_path, Path(root) / fn))

    return discovered


def _write_bundle_from_discovered(
    out_zip: Path,
    *,
    project_dir_name: str,
    bundle_root_name: str,
    discovered: list[tuple[str, Path]],
    deterministic: bool = False,
    source_date_epoch: int | None = None,
    bundle_kind: str = "project",
    support_metadata: dict[str, Any] | None = None,
    release_stage_metadata: dict[str, Any] | None = None,
) -> None:
    files: list[dict[str, object]] = []

    normalized_epoch = _normalized_epoch(
        deterministic=deterministic,
        source_date_epoch=source_date_epoch,
        discovered=discovered,
    )
    deterministic_active = normalized_epoch is not None

    for rel_path, abs_path in discovered:
        try:
            data = abs_path.read_bytes()
            src_stat = abs_path.stat()
        except Exception as exc:
            raise FileNotFoundError(f"Bundle input disappeared: {abs_path}") from exc

        sha256 = hashlib.sha256(data).hexdigest()
        files.append(
            {
                "path": rel_path,
                "size": len(data),
                "sha256": sha256,
                "mtime": int(normalized_epoch if deterministic_active else src_stat.st_mtime),
            }
        )

    created_epoch = int(normalized_epoch if deterministic_active else time.time())
    manifest = {
        "schema": 1,
        "bundle_kind": bundle_kind,
        "vhk_version": __version__,
        "created_at": _iso_utc(created_epoch),
        "project_dir_name": project_dir_name,
        "bundle_root_name": bundle_root_name,
        "file_count": len(files),
        "total_bytes": int(sum(int(f["size"]) for f in files)),
        "files": files,
    }
    if deterministic_active:
        manifest["deterministic"] = True
        manifest["source_date_epoch"] = int(normalized_epoch)
    if support_metadata:
        manifest["bundle_support_metadata"] = support_metadata
    if release_stage_metadata:
        manifest["release_stage_metadata"] = release_stage_metadata

    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        if deterministic_active:
            z.writestr(_stable_zipinfo("vhk_bundle_manifest.json", int(normalized_epoch)), manifest_text.encode("utf-8"))
            for rel_path, abs_path in discovered:
                z.writestr(_stable_zipinfo(rel_path, int(normalized_epoch)), abs_path.read_bytes())
        else:
            z.writestr("vhk_bundle_manifest.json", manifest_text)
            for rel_path, abs_path in discovered:
                z.write(abs_path, arcname=rel_path)


def _load_release_stage_metadata(project_dir: Path, profile_id: str) -> tuple[Path, dict[str, Any]]:
    from vhk.project.release_stage_pack import write_release_stage_pack

    project_dir = project_dir.expanduser().resolve()
    stage_root = project_dir / "build" / "release-stage" / profile_id
    manifest_path = stage_root / "vhk_release_stage.json"
    if not manifest_path.exists():
        write_release_stage_pack(
            project_dir,
            guide_doc=False,
            matrix_doc=False,
            plan_json=False,
            refresh_script=False,
            materialize_stage_trees=True,
            target_profiles=[profile_id],
            force=False,
        )
    if not manifest_path.exists():
        raise ValueError(f"Release-stage lane not found: {profile_id}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid release-stage metadata for {profile_id}")
    return stage_root, payload


def _build_release_stage_metadata(lane: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile_id": str(lane.get("profile_id") or "target"),
        "title": str(lane.get("title") or lane.get("profile_id") or "target"),
        "release_level": str(lane.get("release_level") or "experimental"),
        "deploy_style": str(lane.get("deploy_style") or "launcher-fallback"),
        "delivery_headline": str(lane.get("delivery_headline") or ""),
        "overall_status": str(lane.get("overall_status") or "unknown"),
        "stage_root": str(lane.get("stage_root") or ""),
        "payload_root": str(lane.get("payload_root") or ""),
        "manifest_path": str(lane.get("manifest_path") or ""),
        "readme_path": str(lane.get("readme_path") or ""),
        "install_script_path": str(lane.get("install_script_path") or ""),
        "verify_script_path": str(lane.get("verify_script_path") or ""),
        "assemble_script_path": str(lane.get("assemble_script_path") or ""),
        "required_artifact_count": len([str(x) for x in list(lane.get("required_artifacts") or []) if str(x)]),
        "missing_artifact_count": len([str(x) for x in list(lane.get("missing_artifacts") or []) if str(x)]),
        "generator_command_count": int(lane.get("generator_command_count") or 0),
        "project_copy_source_count": int(lane.get("project_copy_source_count") or 0),
    }


def bundle_project(
    project_dir: Path,
    out_zip: Path,
    *,
    deterministic: bool = False,
    source_date_epoch: int | None = None,
) -> None:
    """Zip a project folder into a shareable bundle.

    Excludes runtime artifacts like logs/ by default.

    Parameters
    ----------
    deterministic:
        Normalize zip-entry timestamps and manifest timestamps for better
        reproducibility. If ``SOURCE_DATE_EPOCH`` is set in the environment, it
        is honored automatically.
    source_date_epoch:
        Explicit UTC epoch used for deterministic timestamps. Overrides the
        environment variable when provided.
    """

    project_dir = project_dir.resolve()
    out_zip = out_zip.resolve()
    exclude_prefixes = {"logs/", ".venv/", "__pycache__/"}
    discovered = _discover_bundle_inputs(project_dir, exclude_prefixes=exclude_prefixes)
    support_metadata = _build_bundle_support_metadata(project_dir, discovered=discovered)
    _write_bundle_from_discovered(
        out_zip,
        project_dir_name=project_dir.name,
        bundle_root_name=project_dir.name,
        discovered=discovered,
        deterministic=deterministic,
        source_date_epoch=source_date_epoch,
        bundle_kind="project",
        support_metadata=support_metadata,
    )


def bundle_release_stage(
    project_dir: Path,
    out_zip: Path,
    *,
    profile_id: str,
    deterministic: bool = False,
    source_date_epoch: int | None = None,
) -> None:
    """Zip one materialized release-stage lane into a shareable bundle.

    The bundle root is the lane's stage directory (for example
    ``build/release-stage/gnome-wayland``), so the payload, README, install,
    verify, and assemble scripts stay together.
    """

    project_dir = project_dir.expanduser().resolve()
    out_zip = out_zip.expanduser().resolve()
    stage_root, lane = _load_release_stage_metadata(project_dir, str(profile_id))
    discovered = _discover_bundle_inputs(stage_root)
    _write_bundle_from_discovered(
        out_zip,
        project_dir_name=project_dir.name,
        bundle_root_name=stage_root.name,
        discovered=discovered,
        deterministic=deterministic,
        source_date_epoch=source_date_epoch,
        bundle_kind="release-stage",
        release_stage_metadata=_build_release_stage_metadata(lane),
    )


def verify_bundle(bundle_zip: Path) -> tuple[bool, list[str]]:
    """Verify a VHK project bundle against its embedded manifest.

    Returns ``(ok, errors)``.

    Notes
    -----
    - This is not a security boundary.
    - It is meant to detect corrupt transfers and provide a future-friendly
      integrity primitive for tooling.
    """

    bundle_zip = bundle_zip.expanduser().resolve()
    errors: list[str] = []

    with zipfile.ZipFile(bundle_zip, "r") as z:
        try:
            manifest = json.loads(z.read("vhk_bundle_manifest.json").decode("utf-8"))
        except KeyError:
            return False, ["Missing vhk_bundle_manifest.json"]
        except Exception as e:
            return False, [f"Failed to parse manifest: {e}"]

        if not isinstance(manifest, dict):
            return False, ["Manifest must be a JSON object"]

        if manifest.get("schema") != 1:
            errors.append(f"Unsupported manifest schema: {manifest.get('schema')!r}")

        files = manifest.get("files")
        if not isinstance(files, list):
            errors.append("Manifest 'files' must be a list")
            return False, errors

        for entry in files:
            if not isinstance(entry, dict):
                errors.append("Manifest file entry must be an object")
                continue
            rel = entry.get("path")
            expected_sha = entry.get("sha256")
            expected_size = entry.get("size")
            if not isinstance(rel, str):
                errors.append("Manifest file entry missing string 'path'")
                continue
            if not isinstance(expected_sha, str) or len(expected_sha) != 64:
                errors.append(f"{rel}: invalid sha256 in manifest")
                continue
            try:
                expected_size_i = int(expected_size)  # type: ignore[arg-type]
            except Exception:
                errors.append(f"{rel}: invalid size in manifest")
                continue

            try:
                data = z.read(rel)
            except KeyError:
                errors.append(f"{rel}: missing from zip")
                continue

            got_sha = hashlib.sha256(data).hexdigest()
            if got_sha != expected_sha:
                errors.append(f"{rel}: sha256 mismatch")
            if len(data) != expected_size_i:
                errors.append(f"{rel}: size mismatch")

    return len(errors) == 0, errors


def inspect_bundle(bundle_zip: Path) -> dict[str, Any]:
    """Read a VHK bundle manifest and expose support metadata for review."""

    bundle_zip = bundle_zip.expanduser().resolve()
    with zipfile.ZipFile(bundle_zip, "r") as z:
        manifest = json.loads(z.read("vhk_bundle_manifest.json").decode("utf-8"))

    if not isinstance(manifest, dict):
        raise ValueError("Bundle manifest must be a JSON object")

    support = manifest.get("bundle_support_metadata")
    if support is not None and not isinstance(support, dict):
        raise ValueError("bundle_support_metadata must be a JSON object when present")

    return {
        "bundle": str(bundle_zip),
        "schema": manifest.get("schema"),
        "bundle_kind": manifest.get("bundle_kind") or "project",
        "vhk_version": manifest.get("vhk_version"),
        "created_at": manifest.get("created_at"),
        "project_dir_name": manifest.get("project_dir_name"),
        "bundle_root_name": manifest.get("bundle_root_name"),
        "file_count": manifest.get("file_count"),
        "total_bytes": manifest.get("total_bytes"),
        "deterministic": bool(manifest.get("deterministic") or False),
        "source_date_epoch": manifest.get("source_date_epoch"),
        "support": support,
        "release_stage": manifest.get("release_stage_metadata"),
    }

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from vhk.project.release_deploy_pack import build_release_deploy_plan
from vhk.project.support_posture import summarize_support_posture


_DOC_PATHS = [
    "docs/VHK_PUBLIC_SUPPORT.md",
    "docs/VHK_INSTALL_QUICKSTART.md",
    "docs/VHK_RELEASE_LANES.md",
    "docs/VHK_RELEASE_SNIPPETS.md",
    "docs/VHK_RELEASE_DEPLOYMENT.md",
    "docs/VHK_RELEASE_INSTALL_SNIPPETS.md",
]


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 10) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _stage_root(profile_id: str) -> str:
    return f"./build/release-stage/{profile_id}"


def _payload_root(profile_id: str) -> str:
    return f"{_stage_root(profile_id)}/payload"


def _rewrite_stage_path(path: str, *, profile_id: str) -> str:
    text = str(path or "")
    lane_prefix = f"./build/release-lanes/{profile_id}"
    if text.startswith(lane_prefix):
        return text.replace(lane_prefix, _payload_root(profile_id), 1)
    if text.startswith("docs/"):
        return f"{_payload_root(profile_id)}/{text}"
    if text.startswith("scripts/"):
        return f"{_payload_root(profile_id)}/{text}"
    return text


def _rewrite_stage_command(command: str, *, profile_id: str) -> str:
    text = str(command or "")
    lane_prefix = f"./build/release-lanes/{profile_id}"
    if lane_prefix in text:
        text = text.replace(lane_prefix, _payload_root(profile_id))
    return text


def _stage_docs_manifest(project_dir: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for rel_path in _DOC_PATHS:
        abs_path = project_dir / rel_path
        docs.append(
            {
                "source": rel_path,
                "stage_path": f"./payload/{rel_path}",
                "present": abs_path.exists(),
                "copy_command": f"test -f {rel_path} && install -D {rel_path} ./payload/{rel_path} || true",
            }
        )
    return docs


def _artifact_stage_rows(project_dir: Path, lane: Mapping[str, Any]) -> list[dict[str, Any]]:
    profile_id = str(lane.get("profile_id") or "target")
    rows: list[dict[str, Any]] = []
    for raw in list(lane.get("artifact_subset") or []):
        if not isinstance(raw, Mapping):
            continue
        source_path = str(raw.get("path") or "").strip()
        if not source_path:
            continue
        stage_path = _rewrite_stage_path(source_path, profile_id=profile_id)
        generator_command = str(raw.get("generator_command") or "").strip()
        if generator_command:
            generator_command = _rewrite_stage_command(generator_command, profile_id=profile_id)
        rows.append(
            {
                "source_path": source_path,
                "stage_path": stage_path,
                "kind": str(raw.get("kind") or "generated"),
                "reason": str(raw.get("reason") or ""),
                "generator_command": generator_command,
                "present_in_project": (project_dir / source_path).exists(),
            }
        )
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = str(row.get("stage_path") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _stage_install_commands(lane: Mapping[str, Any]) -> list[str]:
    commands = [str(cmd) for cmd in list(lane.get("install_commands") or []) if str(cmd)]
    return _dedupe_keep_order(commands)


def _stage_verify_commands(lane: Mapping[str, Any]) -> list[str]:
    commands = [str(cmd) for cmd in list(lane.get("verify_commands") or []) if str(cmd)]
    return _dedupe_keep_order(commands)


def _stage_assemble_commands(lane: Mapping[str, Any], *, project_dir: Path) -> list[str]:
    profile_id = str(lane.get("profile_id") or "target")
    commands = [f"mkdir -p {_payload_root(profile_id)}"]
    for item in _stage_docs_manifest(project_dir):
        commands.append(str(item.get("copy_command") or ""))
    for item in _artifact_stage_rows(project_dir, lane):
        command = str(item.get("generator_command") or "").strip()
        source_path = str(item.get("source_path") or "")
        stage_path = str(item.get("stage_path") or "")
        if command:
            commands.append(command)
        elif source_path and stage_path and (project_dir / source_path).is_file():
            commands.append(f"install -D {source_path} {stage_path}")
    return _dedupe_keep_order([cmd for cmd in commands if cmd])


def _release_stage_level_summary(rows: list[dict[str, Any]], *, level: str) -> list[str]:
    return [
        str(item.get("profile_id") or "")
        for item in rows
        if str(item.get("release_level") or "") == level and str(item.get("profile_id") or "")
    ]


def build_release_stage_plan(
    project_dir: Path,
    *,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    deploy_plan = build_release_deploy_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )
    support_posture = summarize_support_posture(
        project_dir,
        prefer_cached=False,
        capability_usage=capability_usage,
        include_release_lanes=False,
        include_release_deploy=False,
    )

    lanes: list[dict[str, Any]] = []
    for raw in list(deploy_plan.get("deploy_lanes") or []):
        if not isinstance(raw, Mapping):
            continue
        lane = dict(raw)
        profile_id = str(lane.get("profile_id") or "target")
        stage_root = _stage_root(profile_id)
        payload_root = _payload_root(profile_id)
        install_commands = _stage_install_commands(lane)
        verify_commands = _stage_verify_commands(lane)
        assemble_commands = _stage_assemble_commands(lane, project_dir=project_dir)
        docs_manifest = _stage_docs_manifest(project_dir)
        artifact_manifest = _artifact_stage_rows(project_dir, lane)
        lane_row = {
            "profile_id": profile_id,
            "title": str(lane.get("title") or profile_id or "target"),
            "release_level": str(lane.get("release_level") or "experimental"),
            "deploy_style": str(lane.get("deploy_style") or "launcher-fallback"),
            "delivery_headline": str(lane.get("delivery_headline") or ""),
            "overall_status": str(lane.get("overall_status") or "unknown"),
            "stage_root": stage_root,
            "payload_root": payload_root,
            "manifest_path": f"{stage_root}/vhk_release_stage.json",
            "readme_path": f"{stage_root}/README.md",
            "install_script_path": f"{stage_root}/install.sh",
            "verify_script_path": f"{stage_root}/verify.sh",
            "assemble_script_path": f"{stage_root}/assemble_payload.sh",
            "install_commands": install_commands,
            "verify_commands": verify_commands,
            "assemble_commands": assemble_commands,
            "docs_manifest": docs_manifest,
            "artifact_manifest": artifact_manifest,
            "required_artifacts": [str(x) for x in list(lane.get("required_artifacts") or []) if str(x)],
            "missing_artifacts": [str(x) for x in list(lane.get("missing_artifacts") or []) if str(x)],
            "operator_notes": [str(x) for x in list(lane.get("operator_notes") or []) if str(x)],
            "priority_package_group_ids": [str(x) for x in list(lane.get("priority_package_group_ids") or []) if str(x)],
            "generator_command_count": sum(1 for item in artifact_manifest if str(item.get("generator_command") or "").strip()),
            "project_copy_source_count": sum(1 for item in docs_manifest if bool(item.get("present")))
            + sum(1 for item in artifact_manifest if bool(item.get("present_in_project"))),
        }
        lanes.append(lane_row)

    lanes.sort(
        key=lambda item: (
            ["reference", "supported", "caveated", "experimental"].index(
                str(item.get("release_level") or "experimental")
            )
            if str(item.get("release_level") or "experimental") in ["reference", "supported", "caveated", "experimental"]
            else 99,
            str(item.get("title") or ""),
        )
    )

    if lanes:
        order = {"reference": 0, "supported": 1, "caveated": 2, "experimental": 3}
        lanes.sort(key=lambda item: (order.get(str(item.get("release_level") or "experimental"), 9), str(item.get("title") or "")))

    deploy_summary = dict(deploy_plan.get("deploy_summary") or {})
    flagship_lane_id = str(deploy_summary.get("flagship_lane_id") or (lanes[0].get("profile_id") if lanes else ""))
    summary = {
        "profile_count": len(lanes),
        "flagship_lane_id": flagship_lane_id,
        "reference_lane_ids": _release_stage_level_summary(lanes, level="reference"),
        "supported_lane_ids": _release_stage_level_summary(lanes, level="supported"),
        "caveated_lane_ids": _release_stage_level_summary(lanes, level="caveated"),
        "experimental_lane_ids": _release_stage_level_summary(lanes, level="experimental"),
        "materialized_stage_roots": [str(item.get("stage_root") or "") for item in lanes if str(item.get("stage_root") or "")],
    }

    return {
        "project": dict(deploy_plan.get("project") or {}),
        "source_contract": "release_stage_pack",
        "release_summary": dict(deploy_plan.get("release_summary") or {}),
        "deploy_summary": deploy_summary,
        "stage_summary": summary,
        "support_posture": {
            "headline": str(support_posture.get("headline") or "Support posture unavailable"),
            "docs": [str(x) for x in list(support_posture.get("docs") or []) if str(x)],
        },
        "stage_lanes": lanes,
        "review_commands": _dedupe_keep_order(
            [
                f"vhk gen-release-deploy-pack {project_dir.as_posix()} --force --quiet",
                f"vhk gen-release-stage-pack {project_dir.as_posix()} --force --quiet",
            ]
        ),
    }


def render_release_stage_guide(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    support_posture = dict(plan.get("support_posture") or {})
    lanes = _trim_items(plan.get("stage_lanes"), limit=8)

    lines: list[str] = []
    lines.append(f"# VHK release staging guide for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-release-stage-pack`. This pack materializes per-lane release-stage trees so a maintainer can ship a concrete payload root, not just a release/deploy narrative.")
    lines.append("")
    headline = str(support_posture.get("headline") or "").strip()
    if headline:
        lines.append(headline)
        lines.append("")
    lines.append("## Stage lanes")
    lines.append("")
    for lane in lanes:
        lines.append(f"### {lane.get('title') or lane.get('profile_id')}")
        lines.append("")
        lines.append(f"- Release level: `{lane.get('release_level') or 'experimental'}`")
        lines.append(f"- Deploy style: `{lane.get('deploy_style') or 'launcher-fallback'}`")
        lines.append(f"- Stage root: `{lane.get('stage_root') or ''}`")
        lines.append(f"- Payload root: `{lane.get('payload_root') or ''}`")
        delivery = str(lane.get("delivery_headline") or "").strip()
        if delivery:
            lines.append(f"- Delivery headline: {delivery}")
        lines.append(f"- Generator commands: `{lane.get('generator_command_count') or 0}`")
        lines.append(f"- Copyable project sources: `{lane.get('project_copy_source_count') or 0}`")
        notes = [str(x) for x in list(lane.get("operator_notes") or []) if str(x)]
        if notes:
            lines.append("- Notes:")
            for note in notes[:4]:
                lines.append(f"  - {note}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_release_stage_matrix(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    lanes = _trim_items(plan.get("stage_lanes"), limit=8)

    lines: list[str] = []
    lines.append(f"# VHK release stage matrix for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-release-stage-pack`. Use this to compare the materialized stage trees, payload roots, and script surfaces that each desktop lane would actually ship.")
    lines.append("")
    lines.append("## Lane matrix")
    lines.append("")
    for lane in lanes:
        lines.append(f"## {lane.get('title') or lane.get('profile_id')}")
        lines.append("")
        lines.append(f"- Stage root: `{lane.get('stage_root') or ''}`")
        lines.append(f"- Payload root: `{lane.get('payload_root') or ''}`")
        lines.append(f"- Install script: `{lane.get('install_script_path') or ''}`")
        lines.append(f"- Verify script: `{lane.get('verify_script_path') or ''}`")
        lines.append(f"- Assemble script: `{lane.get('assemble_script_path') or ''}`")
        docs_manifest = [dict(item) for item in list(lane.get("docs_manifest") or []) if isinstance(item, dict)]
        if docs_manifest:
            lines.append("- Stage docs:")
            for item in docs_manifest[:6]:
                lines.append(f"  - `{item.get('source') or ''}` → `{item.get('stage_path') or ''}`")
        artifact_manifest = [dict(item) for item in list(lane.get("artifact_manifest") or []) if isinstance(item, dict)]
        if artifact_manifest:
            lines.append("- Staged artifacts:")
            for item in artifact_manifest[:8]:
                note = f" — {item.get('reason') or ''}" if str(item.get("reason") or "") else ""
                lines.append(f"  - `{item.get('stage_path') or ''}`{note}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _script_header(path_from_stage_root_to_project: str) -> list[str]:
    return [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd)"',
        f'PROJECT_DIR="$(CDPATH= cd -- \"$SCRIPT_DIR/{path_from_stage_root_to_project}\" && pwd)"',
        'cd "$PROJECT_DIR"',
        "",
    ]


def render_lane_install_script(lane: Mapping[str, Any]) -> str:
    lines = _script_header("../../..")
    lines.append('printf "%s\\n" "Applying VHK lane install commands..."')
    for cmd in list(lane.get("install_commands") or []):
        text = str(cmd).strip()
        if text:
            lines.append(text)
    lines.append('printf "%s\\n" "Lane install commands complete."')
    lines.append("")
    return "\n".join(lines)


def render_lane_verify_script(lane: Mapping[str, Any]) -> str:
    lines = _script_header("../../..")
    lines.append('printf "%s\\n" "Running VHK lane verification commands..."')
    for cmd in list(lane.get("verify_commands") or []):
        text = str(cmd).strip()
        if text:
            lines.append(text)
    lines.append('printf "%s\\n" "Lane verification complete."')
    lines.append("")
    return "\n".join(lines)


def render_lane_assemble_script(lane: Mapping[str, Any]) -> str:
    lines = _script_header("../../..")
    lines.append('printf "%s\\n" "Materializing staged payload..."')
    for cmd in list(lane.get("assemble_commands") or []):
        text = str(cmd).strip()
        if text:
            lines.append(text)
    lines.append('printf "%s\\n" "Stage payload materialization complete."')
    lines.append("")
    return "\n".join(lines)


def render_lane_stage_readme(lane: Mapping[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# VHK staged lane: {lane.get('title') or lane.get('profile_id')}")
    lines.append("")
    lines.append(f"- Release level: `{lane.get('release_level') or 'experimental'}`")
    lines.append(f"- Deploy style: `{lane.get('deploy_style') or 'launcher-fallback'}`")
    lines.append(f"- Stage root: `{lane.get('stage_root') or ''}`")
    lines.append(f"- Payload root: `{lane.get('payload_root') or ''}`")
    lines.append("")
    lines.append("This directory is the project-local release-stage handoff for one target desktop lane.")
    lines.append("Run `assemble_payload.sh` to materialize export commands and copy any already-present docs into `payload/`. Use `install.sh` and `verify.sh` from the project checkout after reviewing the generated commands.")
    lines.append("")
    artifact_manifest = [dict(item) for item in list(lane.get("artifact_manifest") or []) if isinstance(item, dict)]
    if artifact_manifest:
        lines.append("## Staged artifacts")
        lines.append("")
        for item in artifact_manifest[:10]:
            reason = f" — {item.get('reason') or ''}" if str(item.get("reason") or "") else ""
            lines.append(f"- `{item.get('stage_path') or ''}`{reason}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_release_stage_refresh_script(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('printf "%s\\n" "Collecting VHK release-stage evidence..."')
    lines.append('printf "+ %s\\n" "vhk gen-release-deploy-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-release-deploy-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-release-stage-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-release-stage-pack . --force --quiet" || true')
    lines.append('printf "%s\\n" "Release-stage refresh complete."')
    lines.append("")
    return "\n".join(lines)


def _copy_stage_sources(project_dir: Path, lane: Mapping[str, Any]) -> None:
    stage_root = project_dir / str(lane.get("stage_root") or "")
    payload_root = project_dir / str(lane.get("payload_root") or "")
    stage_root.mkdir(parents=True, exist_ok=True)
    payload_root.mkdir(parents=True, exist_ok=True)
    for item in list(lane.get("docs_manifest") or []):
        if not isinstance(item, Mapping):
            continue
        source = str(item.get("source") or "")
        stage_path = str(item.get("stage_path") or "")
        if not source or not stage_path:
            continue
        source_abs = project_dir / source
        if not source_abs.is_file():
            continue
        target_abs = stage_root / stage_path.removeprefix("./")
        target_abs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_abs, target_abs)
    for item in list(lane.get("artifact_manifest") or []):
        if not isinstance(item, Mapping):
            continue
        source = str(item.get("source_path") or "")
        stage_path = str(item.get("stage_path") or "")
        if not source or not stage_path:
            continue
        source_abs = project_dir / source
        if not source_abs.is_file():
            continue
        target_abs = project_dir / stage_path.removeprefix("./")
        target_abs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_abs, target_abs)


def write_release_stage_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    build_dir: Path | None = None,
    force: bool = False,
    guide_doc: bool = True,
    matrix_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    materialize_stage_trees: bool = True,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()
    build_dir = (build_dir or (project_dir / "build" / "release-stage")).expanduser().resolve()

    plan = build_release_stage_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )

    written: dict[str, Path] = {}
    if guide_doc:
        path = out_dir / "VHK_RELEASE_STAGE.md"
        _write_if_allowed(path, render_release_stage_guide(plan), force=force)
        written["guide_doc"] = path
    if matrix_doc:
        path = out_dir / "VHK_RELEASE_STAGE_MATRIX.md"
        _write_if_allowed(path, render_release_stage_matrix(plan), force=force)
        written["matrix_doc"] = path
    if plan_json:
        path = out_dir / "VHK_RELEASE_STAGE_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_refresh_release_stage.sh"
        _write_if_allowed(path, render_release_stage_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path

    if materialize_stage_trees:
        build_dir.mkdir(parents=True, exist_ok=True)
        for lane in list(plan.get("stage_lanes") or []):
            if not isinstance(lane, Mapping):
                continue
            profile_id = str(lane.get("profile_id") or "target")
            stage_root = build_dir / profile_id
            payload_root = stage_root / "payload"
            stage_root.mkdir(parents=True, exist_ok=True)
            payload_root.mkdir(parents=True, exist_ok=True)
            _write_if_allowed(stage_root / "README.md", render_lane_stage_readme(lane), force=force)
            install_path = stage_root / "install.sh"
            verify_path = stage_root / "verify.sh"
            assemble_path = stage_root / "assemble_payload.sh"
            manifest_path = stage_root / "vhk_release_stage.json"
            _write_if_allowed(install_path, render_lane_install_script(lane), force=force)
            _write_if_allowed(verify_path, render_lane_verify_script(lane), force=force)
            _write_if_allowed(assemble_path, render_lane_assemble_script(lane), force=force)
            _write_if_allowed(manifest_path, json.dumps(dict(lane), indent=2, sort_keys=True) + "\n", force=force)
            install_path.chmod(0o755)
            verify_path.chmod(0o755)
            assemble_path.chmod(0o755)
            _copy_stage_sources(project_dir, lane)
        written["build_dir"] = build_dir
    return written

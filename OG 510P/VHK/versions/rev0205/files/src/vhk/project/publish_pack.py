from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from vhk.project.claim_pack import audit_target_claims, build_claim_plan


_CLAIM_LEVELS = ["unsupported", "experimental", "caveated", "supported", "reference"]
_CLAIM_STRENGTH = {name: idx for idx, name in enumerate(_CLAIM_LEVELS)}


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 5) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _first_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _render_artifact_summary(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        title = str(item.get("title") or item.get("id") or "artifact")
        path_hint = str(item.get("path_hint") or item.get("install_hint") or "").strip()
        if path_hint:
            return f"{title} (`{path_hint}`)"
        return title
    return str(item)


def _load_claim_rows(claims_file: Path) -> list[dict[str, Any]]:
    payload = yaml.safe_load(claims_file.read_text()) or {}
    if not isinstance(payload, dict):
        raise ValueError("Target claims file must be a mapping")
    rows = payload.get("target_claims") or []
    if not isinstance(rows, list):
        raise ValueError("Target claims file 'target_claims' must be a list")
    return [dict(item) for item in rows if isinstance(item, dict)]


def _dedupe_keep_order(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _rollout_from_environment_diffs(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in [dict(x) for x in list(plan.get("environment_diffs") or []) if isinstance(x, dict)]:
        preferred_surfaces = [
            {
                "id": str(surface.get("id") or ""),
                "title": str(surface.get("title") or surface.get("id") or "surface"),
                "category": str(surface.get("category") or ""),
                "fit": str(surface.get("fit") or ""),
            }
            for surface in list(item.get("preferred_surfaces") or [])[:4]
            if isinstance(surface, dict)
        ]
        rows.append(
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or item.get("id") or "environment"),
                "score": int(item.get("score") or 0),
                "fit": str(item.get("fit") or "unknown"),
                "summary": _first_text(item, "summary", "why", "description", "notes"),
                "blocking_capabilities": [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)],
                "diff_highlights": [str(x) for x in list(item.get("diff_highlights") or []) if str(x)],
                "preferred_surfaces": preferred_surfaces,
                "commands": [str(x) for x in list(item.get("commands") or []) if str(x)][:6],
            }
        )
    rows.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))
    return rows


def _language_guardrails(matrix: list[dict[str, Any]]) -> list[str]:
    refs = [str(item.get("title") or item.get("target") or "target") for item in matrix if item.get("claim_level") == "reference"]
    supported = [str(item.get("title") or item.get("target") or "target") for item in matrix if item.get("claim_level") == "supported"]
    caveated = [str(item.get("title") or item.get("target") or "target") for item in matrix if item.get("claim_level") == "caveated"]
    experimental = [str(item.get("title") or item.get("target") or "target") for item in matrix if item.get("claim_level") == "experimental"]
    guardrails: list[str] = []

    if refs:
        guardrails.append("Lead public docs with the reference lane(s): " + ", ".join(refs[:3]) + ".")
    elif supported:
        guardrails.append("Lead public docs with the supported lane(s): " + ", ".join(supported[:3]) + ", and avoid implying a stronger reference environment than the audit supports.")
    else:
        guardrails.append("Do not market this as blanket Linux support yet; name the tested desktop/session lanes explicitly.")

    if caveated:
        guardrails.append("Keep caveated lanes visibly caveated in README/release notes: " + ", ".join(caveated[:4]) + ".")
    if experimental:
        guardrails.append("List experimental lanes under a separate heading so trial support is not confused with shipping support: " + ", ".join(experimental[:4]) + ".")
    if not refs and not supported:
        guardrails.append("Require bundle recipients to read the install quickstart and claim guide before assuming their compositor/session will behave like the maintainer's reference setup.")
    guardrails.append("When a lane depends on remappers, portals, helper daemons, or service units, mention that deployment boundary in public docs instead of hiding it behind generic install wording.")
    return _dedupe_keep_order(guardrails)


def _resolve_bundle_release_story(
    project_dir: Path,
    *,
    project_name: str,
    bundle_target_profile: str | None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    if not bundle_target_profile:
        bundle_name = f"{project_name}.zip"
        return {
            "bundle_kind": "project",
            "headline": "Ship the whole project bundle when you want docs, macros, and generated artifacts to travel together.",
            "bundle_name_hint": bundle_name,
            "bundle_command": f"vhk bundle . ./dist/{bundle_name} --deterministic",
            "inspect_command": f"vhk inspect-bundle ./dist/{bundle_name}",
            "prebundle_commands": [],
        }

    from vhk.project.target_route_pack import build_target_route_plan

    target_plan = build_target_route_plan(
        project_dir,
        target_profiles=[bundle_target_profile],
        capability_usage=capability_usage,
    )
    target_profiles = [dict(item) for item in list(target_plan.get("target_profiles") or []) if isinstance(item, dict)]
    if not target_profiles:
        raise ValueError(f"No matching target profile selected for release-stage bundle: {bundle_target_profile}")

    profile = dict(target_profiles[0].get("profile") or {})
    profile_id = str(profile.get("id") or bundle_target_profile).strip() or bundle_target_profile
    profile_title = str(profile.get("title") or profile_id)
    bundle_name = f"{project_name}-{profile_id}.zip"
    return {
        "bundle_kind": "release-stage",
        "headline": f"Ship the reviewed `{profile_id}` release-stage lane when you want one desktop/session payload instead of the whole project tree.",
        "bundle_profile_id": profile_id,
        "bundle_profile_title": profile_title,
        "bundle_profile_summary": str(profile.get("summary") or "").strip() or None,
        "bundle_stage_root": f"build/release-stage/{profile_id}",
        "bundle_name_hint": bundle_name,
        "bundle_command": f"vhk bundle-stage . ./dist/{bundle_name} --target-profile {profile_id} --deterministic",
        "inspect_command": f"vhk inspect-bundle ./dist/{bundle_name}",
        "prebundle_commands": [
            f"vhk gen-release-stage-pack . --target-profile {profile_id} --force",
        ],
    }


def _build_publish_handoff_story(bundle_story: dict[str, Any]) -> dict[str, Any]:
    bundle_name = str(bundle_story.get("bundle_name_hint") or "project.zip").strip() or "project.zip"
    slug = Path(bundle_name).stem or "project"
    root = f"build/publish/{slug}"
    payload_root = f"{root}/payload"
    payload_docs = [
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
        "docs/VHK_PUBLISH_PLAN.json",
    ]
    payload_stage_refs: list[str] = []
    if str(bundle_story.get("bundle_kind") or "project") == "release-stage":
        profile_id = str(bundle_story.get("bundle_profile_id") or "target").strip() or "target"
        payload_stage_refs = [
            f"build/release-stage/{profile_id}/README.md",
            f"build/release-stage/{profile_id}/vhk_release_stage.json",
        ]
    return {
        "slug": slug,
        "root": root,
        "payload_root": payload_root,
        "manifest_path": f"{root}/vhk_publish_handoff.json",
        "readme_path": f"{root}/README.md",
        "bundle_script_path": f"{root}/bundle_release.sh",
        "refresh_script_path": f"{root}/refresh_publish_inputs.sh",
        "payload_docs": payload_docs,
        "payload_stage_refs": payload_stage_refs,
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
        "bundle_name_hint": bundle_name,
        "bundle_profile_id": str(bundle_story.get("bundle_profile_id") or "").strip() or None,
        "bundle_stage_root": str(bundle_story.get("bundle_stage_root") or "").strip() or None,
        "bundle_command": str(bundle_story.get("bundle_command") or ""),
        "inspect_command": str(bundle_story.get("inspect_command") or ""),
        "prebundle_commands": [str(x) for x in list(bundle_story.get("prebundle_commands") or []) if str(x)],
    }


def _project_relative(path: Path, start: Path) -> str:
    return start.relative_to(path.parent).as_posix()


def render_publish_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("bundle_release_story") or {})
    handoff = dict(plan.get("publish_handoff") or {})
    lines: list[str] = []
    lines.append(f"# VHK publish handoff for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-publish-pack`. This tree is the reviewable release handoff that keeps publish docs, bundle commands, and staged-lane references together.")
    lines.append("")
    lines.append(f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`")
    handoff = dict(plan.get("publish_handoff") or {})
    if handoff.get("root"):
        lines.append(f"- Publish handoff root: `{handoff.get('root')}`")
    lines.append(f"- Bundle name hint: `{handoff.get('bundle_name_hint') or story.get('bundle_name_hint') or 'project.zip'}`")
    if story.get("bundle_profile_id"):
        lines.append(f"- Target profile: `{story.get('bundle_profile_id')}` ({story.get('bundle_profile_title') or story.get('bundle_profile_id')})")
    if handoff.get("payload_root"):
        lines.append(f"- Payload root: `{handoff.get('payload_root')}`")
    lines.append("")
    lines.append("## Review flow")
    lines.append("")
    lines.append("1. Refresh the generated publish inputs and any staged release-lane inputs.")
    lines.append("2. Read the copied support/install docs under `payload/docs/`.")
    lines.append("3. Run `bundle_release.sh` from this directory when the handoff is ready to ship.")
    lines.append("")
    cmds = [str(x) for x in list(handoff.get("prebundle_commands") or []) if str(x)]
    if handoff.get("bundle_command"):
        cmds.append(str(handoff.get("bundle_command")))
    if handoff.get("inspect_command"):
        cmds.append(str(handoff.get("inspect_command")))
    if cmds:
        lines.append("## Commands")
        lines.append("")
        for cmd in cmds[:8]:
            lines.append(f"- `{cmd}`")
        lines.append("")
    stage_refs = [str(x) for x in list(handoff.get("payload_stage_refs") or []) if str(x)]
    if stage_refs:
        lines.append("## Embedded stage references")
        lines.append("")
        for ref in stage_refs:
            lines.append(f"- `{ref}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _publish_script_header(handoff_root: Path, project_dir: Path) -> list[str]:
    rel = _project_relative(project_dir, handoff_root)
    return [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"',
        f'PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/{rel}" && pwd)"',
        'cd "$PROJECT_DIR"',
        "",
    ]


def render_publish_handoff_refresh_script(plan: dict[str, Any], *, handoff_root: Path, project_dir: Path) -> str:
    lines = _publish_script_header(handoff_root, project_dir)
    story = dict(plan.get("bundle_release_story") or {})
    bundle_profile_id = str(story.get("bundle_profile_id") or "").strip()
    lines.append('printf "%s\n" "Refreshing VHK publish handoff inputs..."')
    cmd = 'vhk gen-publish-pack . --force --quiet'
    if bundle_profile_id:
        cmd += f' --bundle-target-profile {bundle_profile_id}'
    lines.append(f'printf "+ %s\n" {cmd!r}')
    lines.append(f'sh -lc {cmd!r} || true')
    lines.append('printf "%s\n" "Publish handoff refresh complete."')
    lines.append("")
    return "\n".join(lines)


def render_publish_handoff_bundle_script(plan: dict[str, Any], *, handoff_root: Path, project_dir: Path) -> str:
    lines = _publish_script_header(handoff_root, project_dir)
    handoff = dict(plan.get("publish_handoff") or {})
    story = dict(plan.get("bundle_release_story") or {})
    bundle_name = str(handoff.get("bundle_name_hint") or story.get("bundle_name_hint") or "project.zip").strip() or "project.zip"
    lines.extend([
        'DIST_DIR="${DIST_DIR:-./dist}"',
        f'BUNDLE_NAME="${{BUNDLE_NAME:-{bundle_name}}}"',
        'mkdir -p "$DIST_DIR"',
        'printf "%s\n" "Bundling VHK publish handoff..."',
    ])
    if str(story.get("bundle_kind") or "project") == "release-stage":
        profile_id = str(story.get("bundle_profile_id") or "target").strip() or "target"
        lines.append(f'VHK_STAGE_PROFILE="${{VHK_STAGE_PROFILE:-{profile_id}}}"')
    for cmd in [str(x) for x in list(handoff.get("prebundle_commands") or []) if str(x)]:
        runtime_cmd = cmd.replace(str(story.get("bundle_profile_id") or ""), '"$VHK_STAGE_PROFILE"') if 'VHK_STAGE_PROFILE' in "\n".join(lines) else cmd
        lines.append(f'printf "+ %s\n" {runtime_cmd!r}')
        lines.append(f'sh -lc {runtime_cmd!r}')
    bundle_cmd = str(handoff.get("bundle_command") or "")
    inspect_cmd = str(handoff.get("inspect_command") or "")
    if bundle_cmd:
        if 'VHK_STAGE_PROFILE' in "\n".join(lines):
            profile_id = str(story.get("bundle_profile_id") or "target").strip() or "target"
            bundle_cmd = bundle_cmd.replace(f'./dist/{bundle_name}', '"$DIST_DIR/$BUNDLE_NAME"').replace(profile_id, '"$VHK_STAGE_PROFILE"')
        else:
            bundle_cmd = bundle_cmd.replace(f'./dist/{bundle_name}', '"$DIST_DIR/$BUNDLE_NAME"')
        lines.append(f'printf "+ %s\n" {bundle_cmd!r}')
        lines.append(f'sh -lc {bundle_cmd!r}')
    if inspect_cmd:
        inspect_cmd = inspect_cmd.replace(f'./dist/{bundle_name}', '"$DIST_DIR/$BUNDLE_NAME"')
        lines.append(f'printf "+ %s\n" {inspect_cmd!r}')
        lines.append(f'sh -lc {inspect_cmd!r} > "$DIST_DIR/${{BUNDLE_NAME%.zip}}.inspect.txt" 2>&1 || true')
    lines.append('printf "%s\n" "Publish handoff bundle complete."')
    lines.append("")
    return "\n".join(lines)


def _copy_if_present(src: Path, dest: Path) -> bool:
    if not src.is_file():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def _materialize_publish_handoff(project_dir: Path, plan: dict[str, Any], *, build_dir: Path, force: bool) -> dict[str, Path]:
    handoff = dict(plan.get("publish_handoff") or {})
    if not handoff:
        return {}
    root = build_dir / str(handoff.get("slug") or "project")
    payload_root = root / "payload"
    docs_payload_root = payload_root / "docs"
    root.mkdir(parents=True, exist_ok=True)
    docs_payload_root.mkdir(parents=True, exist_ok=True)

    story = dict(plan.get("bundle_release_story") or {})
    profile_id = str(story.get("bundle_profile_id") or "").strip()
    if str(story.get("bundle_kind") or "project") == "release-stage" and profile_id:
        from vhk.project.release_stage_pack import write_release_stage_pack
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

    copied_docs: list[str] = []
    for rel in [str(x) for x in list(handoff.get("payload_docs") or []) if str(x)]:
        if _copy_if_present(project_dir / rel, docs_payload_root / Path(rel).name):
            copied_docs.append(rel)
    copied_stage_refs: list[str] = []
    stage_payload_root = payload_root / "release-stage"
    for rel in [str(x) for x in list(handoff.get("payload_stage_refs") or []) if str(x)]:
        if _copy_if_present(project_dir / rel, stage_payload_root / Path(rel).name):
            copied_stage_refs.append(rel)

    manifest_payload = dict(handoff)
    manifest_payload["copied_docs"] = copied_docs
    manifest_payload["copied_stage_refs"] = copied_stage_refs
    manifest_payload["project_root"] = str(project_dir)
    manifest_payload["root"] = root.relative_to(project_dir).as_posix()
    manifest_payload["payload_root"] = payload_root.relative_to(project_dir).as_posix()

    readme_path = root / "README.md"
    manifest_path = root / "vhk_publish_handoff.json"
    refresh_path = root / "refresh_publish_inputs.sh"
    bundle_path = root / "bundle_release.sh"
    _write_if_allowed(readme_path, render_publish_handoff_readme(plan), force=force)
    _write_if_allowed(manifest_path, json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", force=force)
    _write_if_allowed(refresh_path, render_publish_handoff_refresh_script(plan, handoff_root=root, project_dir=project_dir), force=force)
    _write_if_allowed(bundle_path, render_publish_handoff_bundle_script(plan, handoff_root=root, project_dir=project_dir), force=force)
    refresh_path.chmod(0o755)
    bundle_path.chmod(0o755)
    return {
        "handoff_root": root,
        "handoff_manifest": manifest_path,
        "handoff_readme": readme_path,
        "handoff_refresh_script": refresh_path,
        "handoff_bundle_script": bundle_path,
        "handoff_payload_root": payload_root,
    }


def build_publish_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    bundle_target_profile: str | None = None,
) -> dict[str, Any]:
    """Load a VHK project and emit a publish/distribution pack payload."""

    project_dir = project_dir.expanduser().resolve()
    plan = build_claim_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    claims_file = project_dir / "docs" / "VHK_TARGET_CLAIMS.yaml"
    claim_source = "planner_recommendations"
    audit_payload: dict[str, Any] | None = None
    audit_by_target: dict[str, dict[str, Any]] = {}
    if claims_file.exists():
        claim_source = "claims_file"
        claim_rows = _load_claim_rows(claims_file)
        audit_payload = audit_target_claims(
            project_dir,
            claims_file=claims_file,
            capability_usage=capability_usage,
            capability_matrix=capability_matrix,
            capability_issues=capability_issues,
        )
        audit_by_target = {
            str(item.get("target") or ""): dict(item)
            for item in list(audit_payload.get("results") or [])
            if isinstance(item, dict) and str(item.get("target") or "")
        }
    else:
        claim_rows = [dict(item) for item in list(plan.get("recommended_claims") or []) if isinstance(item, dict)]

    recommended = {
        str(item.get("target") or ""): dict(item)
        for item in list(plan.get("recommended_claims") or [])
        if isinstance(item, dict) and str(item.get("target") or "")
    }

    public_support_matrix: list[dict[str, Any]] = []
    for row in claim_rows:
        target = str(row.get("target") or "").strip()
        if not target:
            continue
        rec = recommended.get(target, {})
        audit_row = audit_by_target.get(target, {})
        claim_level = str(row.get("claim_level") or row.get("recommended_level") or rec.get("recommended_level") or "unsupported").strip().lower()
        recommended_level = str(rec.get("recommended_level") or row.get("recommended_level") or "unsupported").strip().lower()
        title = str(row.get("title") or rec.get("title") or target)
        required_artifacts = [str(x) for x in list(row.get("required_artifacts") or rec.get("required_artifacts") or []) if str(x)]
        present_artifacts = [path for path in required_artifacts if (project_dir / path).exists()]
        missing_artifacts = [path for path in required_artifacts if not (project_dir / path).exists()]
        caveats = _dedupe_keep_order([
            *[str(x) for x in list(row.get("caveats") or []) if str(x)],
            *[str(x) for x in list(rec.get("caveats") or []) if str(x)],
            *[str(x) for x in list(audit_row.get("warnings") or []) if str(x)],
        ])
        public_support_matrix.append(
            {
                "target": target,
                "title": title,
                "score": int(rec.get("score") or row.get("score") or 0),
                "fit": str(rec.get("fit") or row.get("fit") or "unknown"),
                "claim_level": claim_level,
                "recommended_level": recommended_level,
                "audit_status": str(audit_row.get("status") or ("recommended" if claim_source != "claims_file" else "unknown")),
                "summary": _first_text(row, "summary", "why", "description", "notes") or _first_text(rec, "summary", "why", "description", "notes"),
                "preferred_surfaces": [dict(x) for x in list(rec.get("preferred_surfaces") or []) if isinstance(x, dict)][:4],
                "blocking_capabilities": [str(x) for x in list(rec.get("blocking_capabilities") or []) if str(x)],
                "caveats": caveats[:6],
                "required_artifacts": required_artifacts,
                "present_artifacts": present_artifacts,
                "missing_artifacts": missing_artifacts,
                "required_commands": [str(x) for x in list(row.get("required_commands") or rec.get("required_commands") or []) if str(x)][:6],
                "maintainer_notes": str(row.get("maintainer_notes") or "").strip(),
                "evidence_status": str(row.get("evidence_status") or rec.get("evidence_status") or "").strip().lower() or None,
                "issues": [str(x) for x in list(audit_row.get("issues") or []) if str(x)],
            }
        )

    public_support_matrix.sort(
        key=lambda item: (
            -_CLAIM_STRENGTH.get(str(item.get("claim_level") or "unsupported"), 0),
            -int(item.get("score") or 0),
            str(item.get("title") or ""),
        )
    )

    rollout = _rollout_from_environment_diffs(plan)
    deployable_surfaces = _trim_items(plan.get("deployable_surfaces"), limit=6)
    setup_recipes = _trim_items(plan.get("setup_recipes"), limit=5)
    toolchain_choices = _trim_items(plan.get("toolchain_choices"), limit=5)

    level_counts: dict[str, int] = {}
    for item in public_support_matrix:
        level = str(item.get("claim_level") or "unsupported")
        level_counts[level] = level_counts.get(level, 0) + 1

    reference_targets = [str(item.get("title") or item.get("target") or "target") for item in public_support_matrix if item.get("claim_level") == "reference"]
    supported_targets = [str(item.get("title") or item.get("target") or "target") for item in public_support_matrix if item.get("claim_level") == "supported"]
    caveated_targets = [str(item.get("title") or item.get("target") or "target") for item in public_support_matrix if item.get("claim_level") == "caveated"]
    experimental_targets = [str(item.get("title") or item.get("target") or "target") for item in public_support_matrix if item.get("claim_level") == "experimental"]

    if reference_targets:
        headline = "Reference lane: " + ", ".join(reference_targets[:2])
    elif supported_targets:
        headline = "Supported lane(s): " + ", ".join(supported_targets[:3])
    elif caveated_targets:
        headline = "Caveated lane(s): " + ", ".join(caveated_targets[:3])
    elif experimental_targets:
        headline = "Experimental lane(s): " + ", ".join(experimental_targets[:3])
    else:
        headline = "No audited support lanes beyond unsupported recommendations yet."

    project_name = str((plan.get("project") or {}).get("name") or project_dir.name)
    bundle_story = _resolve_bundle_release_story(
        project_dir,
        project_name=project_name,
        bundle_target_profile=bundle_target_profile,
        capability_usage=capability_usage,
    )
    publish_handoff = _build_publish_handoff_story(bundle_story)
    publish_commands = [
        "vhk gen-claim-pack . --force",
        "vhk audit-target-claims .",
        "vhk gen-publish-pack . --force",
        *[str(x) for x in list(bundle_story.get("prebundle_commands") or []) if str(x)],
        str(bundle_story.get("bundle_command") or ""),
        str(bundle_story.get("inspect_command") or ""),
    ]
    publish_commands = [cmd for cmd in publish_commands if cmd]

    plan["publish_paths"] = {
        "project_root": str(project_dir),
        "docs_dir": "docs",
        "scripts_dir": "scripts",
        "public_support_doc": "docs/VHK_PUBLIC_SUPPORT.md",
        "install_quickstart_doc": "docs/VHK_INSTALL_QUICKSTART.md",
        "plan_json": "docs/VHK_PUBLISH_PLAN.json",
        "refresh_script": "scripts/vhk_refresh_publish_pack.sh",
        "handoff_root": str(publish_handoff.get("root") or ""),
        "handoff_manifest": str(publish_handoff.get("manifest_path") or ""),
        "handoff_readme": str(publish_handoff.get("readme_path") or ""),
        "handoff_bundle_script": str(publish_handoff.get("bundle_script_path") or ""),
        "handoff_refresh_script": str(publish_handoff.get("refresh_script_path") or ""),
    }
    plan["publish_summary"] = {
        "target_count": len(public_support_matrix),
        "deployable_surface_count": len(list(plan.get("deployable_surfaces") or [])),
        "setup_recipe_count": len(list(plan.get("setup_recipes") or [])),
        "reference_count": level_counts.get("reference", 0),
        "supported_count": level_counts.get("supported", 0),
        "caveated_count": level_counts.get("caveated", 0),
        "experimental_count": level_counts.get("experimental", 0),
        "unsupported_count": level_counts.get("unsupported", 0),
        "bundle_kind": str(bundle_story.get("bundle_kind") or "project"),
    }
    plan["publish_headline"] = headline
    plan["claim_source"] = claim_source
    plan["publish_commands"] = publish_commands
    plan["public_support_matrix"] = public_support_matrix
    plan["recommended_rollout"] = rollout
    plan["language_guardrails"] = _language_guardrails(public_support_matrix)
    plan["bundle_release_story"] = {
        "headline": headline,
        "reference_targets": reference_targets,
        "supported_targets": supported_targets,
        "caveated_targets": caveated_targets,
        "experimental_targets": experimental_targets,
        **bundle_story,
    }
    plan["publish_artifacts"] = {
        "deployable_surfaces": deployable_surfaces,
        "setup_recipes": setup_recipes,
        "toolchain_choices": toolchain_choices,
    }
    plan["publish_handoff"] = publish_handoff
    if audit_payload is not None:
        plan["claim_audit"] = audit_payload
    return plan


def render_public_support_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    matrix = _trim_items(plan.get("public_support_matrix"), limit=10)
    guardrails = [str(x) for x in list(plan.get("language_guardrails") or []) if str(x)]
    story = dict(plan.get("bundle_release_story") or {})

    lines: list[str] = []
    lines.append(f"# VHK public support for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-publish-pack`. Use it as the public-facing support note that travels with bundles, release notes, or README fragments.")
    lines.append("")
    lines.append("## Release posture")
    lines.append("")
    lines.append(f"- Headline: **{plan.get('publish_headline') or 'Support posture unavailable'}**")
    lines.append(f"- Claim source: `{plan.get('claim_source') or 'planner_recommendations'}`")
    lines.append(f"- Desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Bundle kind: `{story.get('bundle_kind') or 'project'}`")
    handoff = dict(plan.get("publish_handoff") or {})
    if handoff.get("root"):
        lines.append(f"- Publish handoff root: `{handoff.get('root')}`")
    if story.get("bundle_profile_id"):
        lines.append(f"- Bundle target profile: `{story.get('bundle_profile_id')}` ({story.get('bundle_profile_title') or story.get('bundle_profile_id')})")
    if story.get("reference_targets"):
        lines.append(f"- Reference lane(s): {', '.join(str(x) for x in story.get('reference_targets')[:3])}")
    if story.get("supported_targets"):
        lines.append(f"- Supported lane(s): {', '.join(str(x) for x in story.get('supported_targets')[:4])}")
    if story.get("caveated_targets"):
        lines.append(f"- Caveated lane(s): {', '.join(str(x) for x in story.get('caveated_targets')[:4])}")
    if story.get("experimental_targets"):
        lines.append(f"- Experimental lane(s): {', '.join(str(x) for x in story.get('experimental_targets')[:4])}")
    lines.append("")

    if matrix:
        lines.append("## Public support matrix")
        lines.append("")
        lines.append("| Target | Claim | Audit | Proof |")
        lines.append("| --- | --- | --- | --- |")
        for item in matrix:
            proof = f"{len(list(item.get('present_artifacts') or []))}/{len(list(item.get('required_artifacts') or []))}"
            lines.append(
                f"| {item.get('title') or item.get('target') or 'target'} | `{item.get('claim_level') or 'unsupported'}` | `{item.get('audit_status') or 'recommended'}` | {proof} |"
            )
        lines.append("")
        lines.append("The matrix above is intentionally explicit: if a lane depends on extra remappers, services, or helper layers, the project should say so in public docs instead of implying one flat Linux support tier.")
        lines.append("")

        for item in matrix[:6]:
            title = item.get("title") or item.get("target") or "target"
            lines.append(f"### {title}")
            lines.append(f"Claim: `{item.get('claim_level') or 'unsupported'}` · Recommended: `{item.get('recommended_level') or 'unsupported'}` · Audit: `{item.get('audit_status') or 'recommended'}` · Fit: `{item.get('fit') or 'unknown'}`")
            summary = _first_text(item, "summary")
            if summary:
                lines.append("")
                lines.append(summary)
            preferred = [dict(x) for x in list(item.get("preferred_surfaces") or []) if isinstance(x, dict)]
            if preferred:
                lines.append("")
                lines.append("Preferred surfaces:")
                for surface in preferred[:4]:
                    lines.append(f"- {surface.get('title') or surface.get('id') or 'surface'}")
            blockers = [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)]
            if blockers:
                lines.append("")
                lines.append("Known blockers:")
                for blocker in blockers[:4]:
                    lines.append(f"- `{blocker}`")
            caveats = [str(x) for x in list(item.get("caveats") or []) if str(x)]
            if caveats:
                lines.append("")
                lines.append("Public caveats:")
                for caveat in caveats[:4]:
                    lines.append(f"- {caveat}")
            issues = [str(x) for x in list(item.get("issues") or []) if str(x)]
            if issues:
                lines.append("")
                lines.append("Audit issues:")
                for text in issues[:4]:
                    lines.append(f"- {text}")
            artifacts = [str(x) for x in list(item.get("required_artifacts") or []) if str(x)]
            if artifacts:
                lines.append("")
                lines.append("Proof artifacts expected in a believable release:")
                for path in artifacts[:5]:
                    lines.append(f"- `{path}`")
            lines.append("")

    if guardrails:
        lines.append("## Language guardrails")
        lines.append("")
        for text in guardrails[:8]:
            lines.append(f"- {text}")
        lines.append("")

    commands = [str(x) for x in list(plan.get("publish_commands") or []) if str(x)]
    if commands:
        lines.append("## Refresh + bundle commands")
        lines.append("")
        for cmd in commands[:6]:
            lines.append(f"- `{cmd}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_install_quickstart(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    rollout = _trim_items(plan.get("recommended_rollout"), limit=5)
    deployable_surfaces = _trim_items((plan.get("publish_artifacts") or {}).get("deployable_surfaces"), limit=5)
    setup_recipes = _trim_items((plan.get("publish_artifacts") or {}).get("setup_recipes"), limit=4)
    toolchain_choices = _trim_items((plan.get("publish_artifacts") or {}).get("toolchain_choices"), limit=4)
    guardrails = [str(x) for x in list(plan.get("language_guardrails") or []) if str(x)]

    lines: list[str] = []
    lines.append(f"# VHK install quickstart for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-publish-pack`. This is the short install/review note meant to travel with a shared bundle or release artifact.")
    lines.append("")
    bundle_story = dict(plan.get("bundle_release_story") or {})
    handoff = dict(plan.get("publish_handoff") or {})
    lines.append(f"Bundle shape: `{bundle_story.get('bundle_kind') or 'project'}`")
    if handoff.get("root"):
        lines.append(f"Publish handoff: `{handoff.get('root')}`")
    if bundle_story.get("bundle_profile_id"):
        lines.append(f"Target profile: `{bundle_story.get('bundle_profile_id')}` ({bundle_story.get('bundle_profile_title') or bundle_story.get('bundle_profile_id')})")
    lines.append("")

    if rollout:
        lines.append("## Recommended rollout order")
        lines.append("")
        lines.append("Start with the strongest-fit desktop/session lane before trying the weaker or more caveated lanes.")
        lines.append("")
        for idx, item in enumerate(rollout, start=1):
            lines.append(f"### {idx}. {item.get('title') or item.get('id') or 'target'}")
            lines.append(f"Fit: `{item.get('fit') or 'unknown'}` · Score: {item.get('score') or 0}")
            summary = _first_text(item, "summary")
            if summary:
                lines.append("")
                lines.append(summary)
            preferred = [dict(x) for x in list(item.get("preferred_surfaces") or []) if isinstance(x, dict)]
            if preferred:
                lines.append("")
                lines.append("Suggested surfaces:")
                for surface in preferred[:4]:
                    lines.append(f"- {surface.get('title') or surface.get('id') or 'surface'}")
            commands = [str(x) for x in list(item.get("commands") or []) if str(x)]
            if commands:
                lines.append("")
                lines.append("Starter commands:")
                for cmd in commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")

    if deployable_surfaces:
        lines.append("## Install surfaces")
        lines.append("")
        for item in deployable_surfaces:
            title = item.get("title") or item.get("id") or "surface"
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(summary)
            entrypoint = str(item.get("entrypoint") or "").strip()
            if entrypoint:
                lines.append("")
                lines.append(f"Entrypoint: `{entrypoint}`")
            targets = [str(x) for x in list(item.get("install_targets") or []) if str(x)]
            if targets:
                lines.append("")
                lines.append("Typical install targets:")
                for target in targets[:4]:
                    lines.append(f"- `{target}`")
            artifacts = list(item.get("artifacts") or [])
            if artifacts:
                lines.append("")
                lines.append("Representative artifacts:")
                for art in artifacts[:4]:
                    lines.append(f"- {_render_artifact_summary(art)}")
            generator_commands = [str(x) for x in list(item.get("generator_commands") or []) if str(x)]
            if generator_commands:
                lines.append("")
                lines.append("Generator commands:")
                for cmd in generator_commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")

    if setup_recipes:
        lines.append("## Setup recipes")
        lines.append("")
        for item in setup_recipes:
            title = item.get("title") or item.get("id") or "recipe"
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(summary)
            install_steps = [str(x) for x in list(item.get("install_steps") or []) if str(x)]
            if install_steps:
                lines.append("")
                lines.append("Install:")
                for step in install_steps[:5]:
                    lines.append(f"- {step}")
            verify_steps = [str(x) for x in list(item.get("verify_steps") or []) if str(x)]
            if verify_steps:
                lines.append("")
                lines.append("Verify:")
                for step in verify_steps[:4]:
                    lines.append(f"- {step}")
            lines.append("")

    if toolchain_choices:
        lines.append("## Toolchain hints")
        lines.append("")
        for item in toolchain_choices:
            title = item.get("title") or item.get("id") or "toolchain"
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(summary)
            names = [str(x) for x in list(item.get("tools") or item.get("packages") or []) if str(x)]
            if names:
                lines.append("")
                lines.append("Likely tools/packages:")
                for name in names[:5]:
                    lines.append(f"- `{name}`")
            lines.append("")

    if guardrails:
        lines.append("## When to stop and caveat")
        lines.append("")
        for text in guardrails[:6]:
            lines.append(f"- {text}")
        lines.append("")

    commands = [str(x) for x in list(plan.get("publish_commands") or []) if str(x)]
    if commands:
        lines.append("## Bundle review commands")
        lines.append("")
        for cmd in commands[:6]:
            lines.append(f"- `{cmd}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_publish_script(plan: dict[str, Any], *, out_dir: Path, script_dir: Path) -> str:
    story = dict(plan.get("bundle_release_story") or {})
    bundle_name_hint = str((story.get("bundle_name_hint") or "project.zip")).strip() or "project.zip"
    bundle_kind = str(story.get("bundle_kind") or "project").strip() or "project"
    lines = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'DIST_DIR="${DIST_DIR:-./dist}"',
        f'BUNDLE_NAME="${{BUNDLE_NAME:-{bundle_name_hint}}}"',
    ]
    if bundle_kind == "release-stage":
        profile_id = str(story.get("bundle_profile_id") or "target").strip() or "target"
        lines.append(f'VHK_STAGE_PROFILE="${{VHK_STAGE_PROFILE:-{profile_id}}}"')
    lines.extend(
        [
            "",
            "vhk gen-operator-pack . --force",
            "vhk gen-verification-pack . --force",
            "vhk gen-support-pack . --force",
            "vhk gen-portability-pack . --force",
            "vhk gen-claim-pack . --force",
            "vhk audit-target-claims . || true",
            f"vhk gen-publish-pack . --out-dir {out_dir} --script-dir {script_dir} --force --quiet"
            + (f" --bundle-target-profile {story.get('bundle_profile_id')}" if bundle_kind == "release-stage" and story.get("bundle_profile_id") else ""),
            'mkdir -p "$DIST_DIR"',
        ]
    )
    if bundle_kind == "release-stage":
        lines.extend(
            [
                'vhk gen-release-stage-pack . --target-profile "$VHK_STAGE_PROFILE" --force --quiet',
                'vhk bundle-stage . "$DIST_DIR/$BUNDLE_NAME" --target-profile "$VHK_STAGE_PROFILE" --deterministic',
            ]
        )
    else:
        lines.append('vhk bundle . "$DIST_DIR/$BUNDLE_NAME" --deterministic')
    lines.append('vhk inspect-bundle "$DIST_DIR/$BUNDLE_NAME" > "$DIST_DIR/${BUNDLE_NAME%.zip}.inspect.txt" 2>&1 || true')
    return "\n".join(lines) + "\n"


def write_publish_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    build_dir: Path | None = None,
    force: bool = False,
    support_doc: bool = True,
    quickstart: bool = True,
    plan_json: bool = True,
    script: bool = True,
    handoff_tree: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    bundle_target_profile: str | None = None,
) -> dict[str, Path]:
    """Write planner-backed publish/distribution artifacts for an existing project."""

    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()
    build_dir = (build_dir or (project_dir / "build" / "publish")).expanduser().resolve()

    plan = build_publish_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        bundle_target_profile=bundle_target_profile,
    )

    written: dict[str, Path] = {}
    if support_doc:
        path = out_dir / "VHK_PUBLIC_SUPPORT.md"
        _write_if_allowed(path, render_public_support_doc(plan), force=force)
        written["support_doc"] = path
    if quickstart:
        path = out_dir / "VHK_INSTALL_QUICKSTART.md"
        _write_if_allowed(path, render_install_quickstart(plan), force=force)
        written["quickstart"] = path
    if plan_json:
        path = out_dir / "VHK_PUBLISH_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_refresh_publish_pack.sh"
        _write_if_allowed(path, render_publish_script(plan, out_dir=out_dir, script_dir=script_dir), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["script"] = path
    if handoff_tree:
        written.update(_materialize_publish_handoff(project_dir, plan, build_dir=build_dir, force=force))
    return written

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.publish_pack import build_publish_plan
from vhk.project.support_posture import summarize_support_posture_from_plan


_COMMENT_LABELS = {
    "hash": "#",
    "double-semicolon": ";;",
}


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 6) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _first_text(item: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def build_trigger_pack_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    plan = build_publish_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )
    plan["support_posture"] = summarize_support_posture_from_plan(plan)
    return plan


def annotate_trigger_surfaces(
    plan: Mapping[str, Any],
    generated_surfaces: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    support_rows = [dict(item) for item in list(plan.get("public_support_matrix") or []) if isinstance(item, dict)]
    surface_choices = {
        str(item.get("id") or ""): dict(item)
        for item in list(plan.get("surface_choices") or [])
        if isinstance(item, dict) and str(item.get("id") or "")
    }
    exported_ids = {str(item.get("id") or "") for item in generated_surfaces if str(item.get("id") or "")}

    def _pref_rows(surface_id: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in support_rows:
            preferred = [dict(x) for x in list(row.get("preferred_surfaces") or []) if isinstance(x, dict)]
            if any(str(pref.get("id") or "") == surface_id for pref in preferred):
                rows.append(row)
        rows.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or item.get("target") or "")))
        return rows

    annotated: list[dict[str, Any]] = []
    for surface in generated_surfaces:
        surface_id = str(surface.get("id") or "")
        choice = surface_choices.get(surface_id, {})
        rows = _pref_rows(surface_id)
        target_mentions = [
            {
                "target": str(row.get("target") or ""),
                "title": str(row.get("title") or row.get("target") or "target"),
                "claim_level": str(row.get("claim_level") or "unsupported"),
                "fit": str(row.get("fit") or "unknown"),
            }
            for row in rows[:6]
        ]
        annotated.append(
            {
                **surface,
                "title": str(surface.get("title") or choice.get("title") or surface_id or "surface"),
                "summary": str(surface.get("summary") or choice.get("summary") or "").strip(),
                "fit": str(surface.get("fit") or choice.get("fit") or "unknown"),
                "strengths": str(surface.get("strengths") or choice.get("strengths") or "").strip(),
                "tradeoffs": str(surface.get("tradeoffs") or choice.get("tradeoffs") or "").strip(),
                "target_mentions": target_mentions,
                "recommended_targets": [item["title"] for item in target_mentions],
            }
        )

    non_file: list[dict[str, Any]] = []
    for surface_id, choice in surface_choices.items():
        if surface_id in exported_ids:
            continue
        rows = _pref_rows(surface_id)
        if not rows:
            continue
        non_file.append(
            {
                "id": surface_id,
                "title": str(choice.get("title") or surface_id),
                "category": str(choice.get("category") or "surface"),
                "fit": str(choice.get("fit") or "unknown"),
                "summary": str(choice.get("summary") or "").strip(),
                "commands": [str(x) for x in list(choice.get("commands") or []) if str(x)][:4],
                "recommended_targets": [str(row.get("title") or row.get("target") or "target") for row in rows[:6]],
            }
        )

    non_file.sort(key=lambda item: (str(item.get("category") or ""), str(item.get("title") or "")))
    return annotated, non_file


def build_trigger_pack_manifest(
    plan: Mapping[str, Any],
    *,
    export_root: Path,
    generated_surfaces: list[dict[str, Any]],
    non_file_surfaces: list[dict[str, Any]],
    docs_dir: Path,
    script_dir: Path,
) -> dict[str, Any]:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    support_posture = dict(plan.get("support_posture") or {})
    return {
        "project": {
            "name": str(project.get("name") or export_root.parent.name),
            "root_dir": str(project.get("root_dir") or "."),
            "desktop_backend": str(project.get("desktop_backend") or "unknown"),
        },
        "overview": {
            "macros": int(overview.get("macros") or 0),
            "bindings": int(overview.get("bindings") or 0),
            "hotstrings": int(overview.get("hotstrings") or 0),
            "presets": int(overview.get("presets") or 0),
            "bus_watchers": int(overview.get("bus_watchers") or 0),
            "clipboard_watchers": int(overview.get("clipboard_watchers") or 0),
            "window_watchers": int(overview.get("window_watchers") or 0),
        },
        "export_root": str(export_root),
        "docs": {
            "surfaces": "docs/VHK_TRIGGER_SURFACES.md",
            "matrix": "docs/VHK_TRIGGER_MATRIX.md",
            "plan_json": "docs/VHK_TRIGGER_PACK.json",
        },
        "script": "scripts/vhk_refresh_trigger_pack.sh",
        "support_headline": str(support_posture.get("headline") or "Support posture unavailable"),
        "reference_targets": [str(x) for x in list(support_posture.get("reference_targets") or []) if str(x)],
        "supported_targets": [str(x) for x in list(support_posture.get("supported_targets") or []) if str(x)],
        "caveated_targets": [str(x) for x in list(support_posture.get("caveated_targets") or []) if str(x)],
        "experimental_targets": [str(x) for x in list(support_posture.get("experimental_targets") or []) if str(x)],
        "generated_surfaces": generated_surfaces,
        "non_file_surfaces": non_file_surfaces,
        "refresh_commands": [
            "vhk gen-trigger-pack . --force",
            *[str(item.get("generator_command") or "") for item in generated_surfaces if str(item.get("generator_command") or "")],
        ],
    }


def render_trigger_surfaces_doc(plan: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    project = dict(manifest.get("project") or {})
    overview = dict(manifest.get("overview") or {})
    support_posture = dict(plan.get("support_posture") or {})
    generated_surfaces = [dict(item) for item in list(manifest.get("generated_surfaces") or []) if isinstance(item, dict)]
    non_file_surfaces = [dict(item) for item in list(manifest.get("non_file_surfaces") or []) if isinstance(item, dict)]
    setup_recipes = _trim_items(plan.get("setup_recipes"), limit=8)

    lines: list[str] = []
    lines.append(f"# VHK trigger surfaces for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-trigger-pack`. This groups exportable Linux trigger layers into one reviewable pack instead of scattering one-off remapper and WM snippets across the repo.")
    lines.append("")
    lines.append("## Project snapshot")
    lines.append("")
    lines.append(f"- Root: `{project.get('root_dir') or '.'}`")
    lines.append(f"- Desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Export root: `{manifest.get('export_root') or './build/trigger_pack'}`")
    lines.append("")

    lines.append("## Public support headline")
    lines.append("")
    lines.append(str(support_posture.get("headline") or "Support posture unavailable."))
    lines.append("")

    guardrails = [str(x) for x in list(support_posture.get("language_guardrails") or []) if str(x)]
    if guardrails:
        lines.append("### Guardrails")
        lines.append("")
        for item in guardrails[:6]:
            lines.append(f"- {item}")
        lines.append("")

    if generated_surfaces:
        lines.append("## Generated trigger configs")
        lines.append("")
        for item in generated_surfaces:
            title = str(item.get("title") or item.get("id") or "surface")
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "strengths")
            if summary:
                lines.append(summary)
            lines.append("")
            lines.append(f"- Surface id: `{item.get('id')}`")
            lines.append(f"- Category: `{item.get('category') or 'surface'}`")
            lines.append(f"- File: `{item.get('relative_path')}`")
            lines.append(f"- Comment style: `{_COMMENT_LABELS.get(str(item.get('comment_style') or ''), str(item.get('comment_style') or 'n/a'))}`")
            lines.append(f"- Generator command: `{item.get('generator_command')}`")
            if item.get("fit"):
                lines.append(f"- Planner fit: `{item.get('fit')}`")
            targets = [dict(x) for x in list(item.get("target_mentions") or []) if isinstance(x, dict)]
            if targets:
                lines.append("- Best target lanes:")
                for target in targets[:4]:
                    lines.append(f"  - {target.get('title')} ({target.get('claim_level')}, fit={target.get('fit')})")
            tradeoffs = str(item.get("tradeoffs") or "").strip()
            if tradeoffs:
                lines.append(f"- Tradeoffs: {tradeoffs}")
            lines.append("")

    if non_file_surfaces:
        lines.append("## Trigger surfaces without static files")
        lines.append("")
        lines.append("Some Linux-native trigger paths are session/permission managed rather than config-file driven. The planner may still prefer them for certain targets even though this pack cannot emit a standalone snippet.")
        lines.append("")
        for item in non_file_surfaces[:6]:
            title = str(item.get("title") or item.get("id") or "surface")
            lines.append(f"### {title}")
            summary = _first_text(item, "summary")
            if summary:
                lines.append(summary)
            targets = [str(x) for x in list(item.get("recommended_targets") or []) if str(x)]
            if targets:
                lines.append("")
                lines.append("Recommended target lanes:")
                for target in targets[:4]:
                    lines.append(f"- {target}")
            commands = [str(x) for x in list(item.get("commands") or []) if str(x)]
            if commands:
                lines.append("")
                lines.append("Review commands:")
                for cmd in commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")

    if setup_recipes:
        lines.append("## Related setup recipes")
        lines.append("")
        for item in setup_recipes:
            title = str(item.get("title") or item.get("id") or "recipe")
            if str(item.get("id") or "") not in {"wm-trigger-install", "launcher-entrypoint-install", "watcher-service-install"}:
                continue
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "why", "description")
            if summary:
                lines.append(summary)
            steps = [str(x) for x in list(item.get("install_steps") or []) if str(x)]
            if steps:
                lines.append("")
                for step in steps[:5]:
                    lines.append(f"- {step}")
            lines.append("")

    lines.append("## Refresh commands")
    lines.append("")
    for cmd in [str(x) for x in list(manifest.get("refresh_commands") or []) if str(x)][:10]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_trigger_matrix_doc(plan: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    project = dict(manifest.get("project") or {})
    generated_by_id = {
        str(item.get("id") or ""): dict(item)
        for item in list(manifest.get("generated_surfaces") or [])
        if isinstance(item, dict) and str(item.get("id") or "")
    }
    rows = [dict(item) for item in list(plan.get("public_support_matrix") or []) if isinstance(item, dict)]

    lines: list[str] = []
    lines.append(f"# VHK trigger matrix for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-trigger-pack`. Read this as a target-by-target handoff for which trigger surfaces belong in each lane and which of those surfaces are actual emitted files versus session-managed integration paths.")
    lines.append("")

    for row in rows:
        title = str(row.get("title") or row.get("target") or "target")
        claim = str(row.get("claim_level") or "unsupported")
        fit = str(row.get("fit") or "unknown")
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"- Claim level: `{claim}`")
        lines.append(f"- Planner fit: `{fit}`")
        summary = _first_text(row, "summary")
        if summary:
            lines.append(f"- Summary: {summary}")
        blockers = [str(x) for x in list(row.get("blocking_capabilities") or []) if str(x)]
        if blockers:
            lines.append(f"- Blocking capabilities: {', '.join(blockers)}")
        caveats = [str(x) for x in list(row.get("caveats") or []) if str(x)]
        if caveats:
            lines.append("- Caveats:")
            for item in caveats[:4]:
                lines.append(f"  - {item}")
        preferred = [dict(x) for x in list(row.get("preferred_surfaces") or []) if isinstance(x, dict)]
        if preferred:
            lines.append("- Preferred trigger surfaces:")
            for pref in preferred:
                pref_id = str(pref.get("id") or "")
                generated = generated_by_id.get(pref_id)
                label = str(pref.get("title") or pref_id or "surface")
                if generated:
                    lines.append(f"  - {label} → `{generated.get('relative_path')}`")
                else:
                    lines.append(f"  - {label} → no static artifact in this pack")
        required = [str(x) for x in list(row.get("required_commands") or []) if str(x)]
        if required:
            lines.append("- Related review commands:")
            for cmd in required[:4]:
                lines.append(f"  - `{cmd}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_trigger_refresh_script(
    *,
    out_dir: str,
    vhk_cmd: str = "vhk",
) -> str:
    return (
        "#!/usr/bin/env sh\n"
        "set -eu\n\n"
        f"OUT_DIR=\"${{OUT_DIR:-{out_dir}}}\"\n\n"
        f"{vhk_cmd} gen-trigger-pack . --out-dir \"$OUT_DIR\" --force --quiet\n"
    )


def write_trigger_pack_artifacts(
    *,
    export_root: Path,
    plan: Mapping[str, Any],
    manifest: Mapping[str, Any],
    force: bool,
    guide: bool,
    matrix: bool,
    plan_json: bool,
    script: bool,
    out_dir_display: str | None = None,
) -> dict[str, Path]:
    docs_dir = export_root / "docs"
    script_dir = export_root / "scripts"
    written: dict[str, Path] = {}

    if guide:
        guide_path = docs_dir / "VHK_TRIGGER_SURFACES.md"
        _write_if_allowed(guide_path, render_trigger_surfaces_doc(plan, manifest), force=force)
        written["guide"] = guide_path

    if matrix:
        matrix_path = docs_dir / "VHK_TRIGGER_MATRIX.md"
        _write_if_allowed(matrix_path, render_trigger_matrix_doc(plan, manifest), force=force)
        written["matrix"] = matrix_path

    if plan_json:
        plan_path = docs_dir / "VHK_TRIGGER_PACK.json"
        _write_if_allowed(plan_path, json.dumps(manifest, indent=2) + "\n", force=force)
        written["plan_json"] = plan_path

    if script:
        script_path = script_dir / "vhk_refresh_trigger_pack.sh"
        rel_root = out_dir_display or f"./{export_root.name}"
        _write_if_allowed(script_path, render_trigger_refresh_script(out_dir=rel_root), force=force)
        script_path.chmod(0o755)
        written["script"] = script_path

    return written

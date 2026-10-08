from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vhk.project.loader import load_project
from vhk.project.strategy import summarize_project_strategy


_CAPABILITY_ORDER = [
    "screen_capture",
    "text_injection",
    "pointer_injection",
    "global_hotkeys",
    "window_introspection",
    "input_capture",
]


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


def _status_cell(status: str) -> str:
    status = str(status or "unknown")
    return {
        "ok": "ok",
        "limited": "limited",
        "missing": "missing",
        "unknown": "unknown",
    }.get(status, status)


def build_portability_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    """Load a VHK project and emit a planner-backed portability payload."""

    project = load_project(project_dir)
    plan = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    environment_diffs = [dict(item) for item in list(plan.get("environment_diffs") or []) if isinstance(item, dict)]
    portability_playbooks = [dict(item) for item in list(plan.get("portability_playbooks") or []) if isinstance(item, dict)]
    capability_coverage = [dict(item) for item in list(plan.get("capability_coverage") or []) if isinstance(item, dict)]
    surface_choices = [dict(item) for item in list(plan.get("surface_choices") or []) if isinstance(item, dict)]

    target_rollout: list[dict[str, Any]] = []
    for item in environment_diffs:
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
        target_rollout.append(
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or item.get("id") or "environment"),
                "score": int(item.get("score") or 0),
                "fit": str(item.get("fit") or "unknown"),
                "summary": _first_text(item, "summary", "why", "description", "notes"),
                "preferred_surfaces": preferred_surfaces,
                "blocking_capabilities": [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)],
                "diff_highlights": [str(x) for x in list(item.get("diff_highlights") or []) if str(x)],
                "commands": [str(x) for x in list(item.get("commands") or []) if str(x)][:6],
            }
        )
    target_rollout.sort(key=lambda item: (-int(item.get("score") or 0), str(item.get("title") or "")))

    portability_commands = [
        "vhk plan-project . --json",
        "vhk validate . --json",
        "vhk gen-operator-pack . --force",
        "vhk gen-verification-pack . --force",
        "vhk gen-support-pack . --force",
        "vhk gen-portability-pack . --force",
    ]

    plan["target_rollout"] = target_rollout
    plan["portability_commands"] = portability_commands
    plan["portability_paths"] = {
        "project_root": str(Path(project.root_dir)),
        "docs_dir": "docs",
        "scripts_dir": "scripts",
        "review_dir": "portability",
    }
    plan["portability_summary"] = {
        "target_count": len(environment_diffs),
        "playbook_count": len(portability_playbooks),
        "coverage_count": len(capability_coverage),
        "surface_choice_count": len(surface_choices),
    }
    return plan


def render_portability_guide(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    target_rollout = _trim_items(plan.get("target_rollout"), limit=6)
    capability_coverage = _trim_items(plan.get("capability_coverage"), limit=6)
    portability_gaps = _trim_items(plan.get("portability_gaps"), limit=5)
    portability_playbooks = _trim_items(plan.get("portability_playbooks"), limit=5)
    surface_choices = _trim_items(plan.get("surface_choices"), limit=6)
    session_capabilities = dict(plan.get("session_capabilities") or {})
    session_issues = list(plan.get("session_issues") or [])
    portability_paths = dict(plan.get("portability_paths") or {})
    portability_commands = [str(item).strip() for item in list(plan.get("portability_commands") or []) if str(item).strip()]

    lines: list[str] = []
    lines.append(f"# VHK portability guide for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-portability-pack`. Use it to review where the same project should land cleanly across X11/i3, GNOME/KDE Wayland, and conservative wlroots/Hyprland-style targets.")
    if session_capabilities:
        lines.append("This guide is session-aware: it includes the current session capability matrix so portability review can start from a real machine while still planning for other target desktops.")
    else:
        lines.append("This guide is capability-agnostic: rerun it with session checks on a real machine before locking down claims about a target desktop.")
    lines.append("")

    lines.append("## Project snapshot")
    lines.append("")
    lines.append(f"- Root: `{project.get('root_dir') or '.'}`")
    lines.append(f"- Desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Clipboard watchers: {overview.get('clipboard_watchers', 0)}")
    lines.append(f"- Bus watchers: {overview.get('bus_watchers', 0)}")
    lines.append(f"- Window watchers: {overview.get('window_watchers', 0)}")
    if portability_paths:
        lines.append(f"- Generated review dir: `{portability_paths.get('review_dir') or 'portability'}`")
    lines.append("")

    if target_rollout:
        lines.append("## Suggested target rollout")
        lines.append("")
        lines.append("Start with the strongest fit and move downward only after the earlier lane is believable in operator/release/support artifacts.")
        lines.append("")
        for idx, item in enumerate(target_rollout, start=1):
            title = item.get("title") or item.get("id") or "target"
            lines.append(f"### {idx}. {title}")
            lines.append(f"Fit: `{item.get('fit') or 'unknown'}` · Score: {item.get('score') or 0}")
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append("")
                lines.append(summary)
            preferred = list(item.get("preferred_surfaces") or [])
            if preferred:
                lines.append("")
                lines.append("Preferred surfaces:")
                for surface in preferred[:4]:
                    lines.append(f"- {surface.get('title') or surface.get('id') or 'surface'}")
            blockers = list(item.get("blocking_capabilities") or [])
            if blockers:
                lines.append("")
                lines.append("Blocking capabilities:")
                for name in blockers[:4]:
                    lines.append(f"- `{name}`")
            highlights = list(item.get("diff_highlights") or [])
            if highlights:
                lines.append("")
                lines.append("Watchouts:")
                for text in highlights[:4]:
                    lines.append(f"- {text}")
            commands = list(item.get("commands") or [])
            if commands:
                lines.append("")
                lines.append("Starter commands:")
                for cmd in commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")

    if capability_coverage:
        lines.append("## Capability coverage hot spots")
        lines.append("")
        for item in capability_coverage:
            title = item.get("title") or item.get("id") or "capability"
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(summary)
            scenario_rows = [dict(row) for row in list(item.get("scenario_rows") or []) if isinstance(row, dict)]
            if scenario_rows:
                lines.append("")
                lines.append("Target statuses:")
                for row in scenario_rows[:6]:
                    lines.append(f"- {row.get('title') or row.get('id') or 'target'} — `{_status_cell(str(row.get('status') or 'unknown'))}`")
            offload = [str(x) for x in list(item.get("offload") or []) if str(x)]
            if offload:
                lines.append("")
                lines.append("Preferred response:")
                for text in offload[:3]:
                    lines.append(f"- {text}")
            lines.append("")

    if portability_gaps:
        lines.append("## Portability gaps to name explicitly")
        lines.append("")
        for item in portability_gaps:
            title = item.get("title") or item.get("id") or "gap"
            baseline = dict(item.get("baseline") or {})
            base_title = baseline.get("title") or baseline.get("id")
            summary = _first_text(item, "summary", "migration_response", "why", "description", "notes")
            if base_title:
                lines.append(f"- **{title}** vs **{base_title}** — {summary or 'portability changes detected'}")
            else:
                lines.append(f"- **{title}** — {summary or 'portability changes detected'}")
        lines.append("")

    if portability_playbooks:
        lines.append("## Migration playbooks")
        lines.append("")
        for item in portability_playbooks:
            title = item.get("title") or item.get("id") or "playbook"
            lines.append(f"### {title}")
            summary = _first_text(item, "summary", "goal", "why", "description", "notes")
            if summary:
                lines.append(summary)
            artifacts = [dict(x) for x in list(item.get("artifacts") or []) if isinstance(x, dict)]
            if artifacts:
                lines.append("")
                lines.append("Artifacts to generate or review:")
                for art in artifacts[:5]:
                    title2 = art.get("title") or art.get("id") or "artifact"
                    path_hint = str(art.get("path_hint") or "").strip()
                    if path_hint:
                        lines.append(f"- {title2} (`{path_hint}`)")
                    else:
                        lines.append(f"- {title2}")
            install_checks = [str(x) for x in list(item.get("install_checks") or []) if str(x)]
            if install_checks:
                lines.append("")
                lines.append("Install / proof checks:")
                for text in install_checks[:4]:
                    lines.append(f"- {text}")
            lines.append("")

    if surface_choices:
        lines.append("## Export surfaces worth preserving")
        lines.append("")
        for item in surface_choices:
            title = item.get("title") or item.get("id") or "surface"
            summary = _first_text(item, "summary", "strengths", "description", "notes")
            lines.append(f"- **{title}** — {summary or 'review this surface while comparing targets'}")
        lines.append("")

    lines.append("## Core review commands")
    lines.append("")
    for cmd in portability_commands:
        lines.append(f"- `{cmd}`")
    lines.append("")

    if session_capabilities:
        lines.append("## Current session fit")
        lines.append("")
        for capability in _CAPABILITY_ORDER:
            item = session_capabilities.get(capability)
            if not isinstance(item, dict):
                continue
            status = str(item.get("status") or "unknown")
            recommended = str(item.get("recommended") or "")
            mechanisms = ", ".join(str(x) for x in (item.get("mechanisms") or [])[:4])
            lines.append(f"- **{capability}** — `{status}`; recommended: `{recommended or 'n/a'}`; mechanisms: {mechanisms or 'n/a'}")
        lines.append("")

    if session_issues:
        lines.append("## Session-specific cautions")
        lines.append("")
        for item in session_issues[:8]:
            message = str(item.get("message") or "session issue")
            suggestion = str(item.get("suggestion") or "").strip()
            if suggestion:
                lines.append(f"- {message} — {suggestion}")
            else:
                lines.append(f"- {message}")
        lines.append("")

    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"



def render_target_rollout(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    target_rollout = _trim_items(plan.get("target_rollout"), limit=6)
    portability_playbooks = _trim_items(plan.get("portability_playbooks"), limit=6)
    capability_coverage = _trim_items(plan.get("capability_coverage"), limit=6)
    session_issues = list(plan.get("session_issues") or [])

    lines: list[str] = []
    lines.append(f"# VHK target rollout for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-portability-pack`. Use it as a cross-desktop rollout worksheet instead of claiming blanket Linux compatibility.")
    lines.append("")

    lines.append("## Baseline refresh")
    lines.append("")
    lines.append("- [ ] Run `vhk plan-project . --json` and review `environment_diffs`, `portability_gaps`, and `portability_playbooks`.")
    lines.append("- [ ] Run `vhk validate . --json` and confirm the project still matches the currently intended product lanes.")
    lines.append("- [ ] Regenerate `docs/VHK_PORTABILITY_PLAN.json` and `scripts/vhk_review_portability.sh`.")
    if session_issues:
        lines.append(f"- [ ] Review {min(len(session_issues), 8)} current-session issue(s) before treating this machine as a reference target.")
    lines.append("")

    if target_rollout:
        lines.append("## Rollout order")
        lines.append("")
        for idx, item in enumerate(target_rollout, start=1):
            title = item.get("title") or item.get("id") or "target"
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append(f"- [ ] {idx}. {title} — {summary}")
            else:
                lines.append(f"- [ ] {idx}. {title}")
        lines.append("")

    if portability_playbooks:
        lines.append("## Migration playbooks")
        lines.append("")
        for item in portability_playbooks:
            title = item.get("title") or item.get("id") or "playbook"
            summary = _first_text(item, "summary", "goal", "why", "description", "notes")
            if summary:
                lines.append(f"- [ ] {title} — {summary}")
            else:
                lines.append(f"- [ ] {title}")
        lines.append("")

    if capability_coverage:
        lines.append("## Capability proof points")
        lines.append("")
        for item in capability_coverage:
            title = item.get("title") or item.get("id") or "capability"
            lines.append(f"### {title}")
            scenario_rows = [dict(row) for row in list(item.get("scenario_rows") or []) if isinstance(row, dict)]
            for row in scenario_rows[:6]:
                lines.append(f"- [ ] {row.get('title') or row.get('id') or 'target'} => `{_status_cell(str(row.get('status') or 'unknown'))}`")
            lines.append("")

    lines.append("## Release-story handoff")
    lines.append("")
    lines.append("- [ ] Pair the chosen target lane with `vhk gen-operator-pack` so install/review/rollback docs match the target desktop.")
    lines.append("- [ ] Pair it with `vhk gen-verification-pack` so release gates match the target desktop.")
    lines.append("- [ ] Pair it with `vhk gen-support-pack` so support capture reflects the target desktop's expected helper and portal seams.")
    lines.append("")

    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"



def render_review_script(plan: dict[str, Any]) -> str:
    target_rollout = _trim_items(plan.get("target_rollout"), limit=6)

    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST_ROOT="${1:-./portability}"')
    lines.append('STAMP="$(date +%Y%m%d_%H%M%S 2>/dev/null || printf unknown)"')
    lines.append('DEST="$DEST_ROOT/review_$STAMP"')
    lines.append('mkdir -p "$DEST/reports" "$DEST/docs" "$DEST/scripts" "$DEST/meta"')
    lines.append("")
    lines.append('echo "[1/4] Capturing current planning baseline"')
    lines.append('vhk doctor --json > "$DEST/reports/doctor.json" 2> "$DEST/reports/doctor.stderr" || true')
    lines.append('vhk validate . --json > "$DEST/reports/validate.json" 2> "$DEST/reports/validate.stderr" || true')
    lines.append('vhk plan-project . --json > "$DEST/reports/plan-project.json" 2> "$DEST/reports/plan-project.stderr" || true')
    lines.append("")
    lines.append('echo "[2/4] Regenerating handoff artifacts"')
    lines.append('vhk gen-operator-pack . --out-dir "$DEST/docs" --force --quiet --no-session-check || true')
    lines.append('vhk gen-verification-pack . --out-dir "$DEST/docs" --script-dir "$DEST/scripts" --force --quiet --no-session-check || true')
    lines.append('vhk gen-support-pack . --out-dir "$DEST/docs" --script-dir "$DEST/scripts" --force --quiet --no-session-check || true')
    lines.append('vhk gen-portability-pack . --out-dir "$DEST/docs" --script-dir "$DEST/scripts" --force --quiet --no-session-check || true')
    lines.append("")
    lines.append('echo "[3/4] Capturing session metadata"')
    lines.append('{')
    lines.append('  printf "pwd=%s\\n" "$PWD"')
    lines.append('  printf "uname="; uname -a 2>/dev/null || true')
    lines.append('  printf "XDG_SESSION_TYPE=%s\\n" "${XDG_SESSION_TYPE:-}"')
    lines.append('  printf "XDG_CURRENT_DESKTOP=%s\\n" "${XDG_CURRENT_DESKTOP:-}"')
    lines.append('  printf "DESKTOP_SESSION=%s\\n" "${DESKTOP_SESSION:-}"')
    lines.append('  printf "DISPLAY=%s\\n" "${DISPLAY:-}"')
    lines.append('  printf "WAYLAND_DISPLAY=%s\\n" "${WAYLAND_DISPLAY:-}"')
    lines.append('} > "$DEST/meta/session_env.txt"')
    lines.append("")
    lines.append('echo "[4/4] Writing review summary"')
    lines.append('cat > "$DEST/README.txt" <<EOF')
    lines.append('VHK portability review bundle complete.')
    lines.append('')
    lines.append('Use this folder to compare cross-desktop claims before promising broad Linux support.')
    lines.append('')
    lines.append('Key files:')
    lines.append('- reports/doctor.json')
    lines.append('- reports/validate.json')
    lines.append('- reports/plan-project.json')
    lines.append('- docs/VHK_PORTABILITY_PLAN.json')
    lines.append('- docs/VHK_PORTABILITY_GUIDE.md')
    lines.append('- docs/VHK_TARGET_ROLLOUT.md')
    lines.append('- docs/VHK_OPERATOR_PLAN.json')
    lines.append('- docs/VHK_VERIFICATION_PLAN.json')
    lines.append('- docs/VHK_SUPPORT_PLAN.json')
    if target_rollout:
        lines.append('')
        lines.append('Suggested rollout order:')
        for idx, item in enumerate(target_rollout, start=1):
            title = str(item.get('title') or item.get('id') or 'target')
            lines.append(f'- {idx}. {title}')
    lines.append('EOF')
    lines.append("")
    lines.append('echo "Portability review complete: $DEST"')
    lines.append("")
    return "\n".join(lines)



def write_portability_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool,
    guide: bool = True,
    rollout: bool = True,
    plan_json: bool = True,
    script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Path]:
    """Write planner-backed portability artifacts for an existing project."""

    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    script_dir.mkdir(parents=True, exist_ok=True)

    plan = build_portability_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    written: dict[str, Path] = {}
    if plan_json:
        path = out_dir / "VHK_PORTABILITY_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if guide:
        path = out_dir / "VHK_PORTABILITY_GUIDE.md"
        _write_if_allowed(path, render_portability_guide(plan), force=force)
        written["guide"] = path
    if rollout:
        path = out_dir / "VHK_TARGET_ROLLOUT.md"
        _write_if_allowed(path, render_target_rollout(plan), force=force)
        written["rollout"] = path
    if script:
        path = script_dir / "vhk_review_portability.sh"
        _write_if_allowed(path, render_review_script(plan), force=force)
        try:
            path.chmod(0o755)
        except Exception:
            pass
        written["script"] = path
    return written

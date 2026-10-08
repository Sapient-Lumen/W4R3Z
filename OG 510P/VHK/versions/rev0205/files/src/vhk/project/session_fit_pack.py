from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.loader import load_project
from vhk.project.setup_pack import _build_toolchain_package_plan
from vhk.project.strategy import summarize_project_strategy


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _first_text(item: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 6) -> list[dict[str, Any]]:
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


def _usage_examples(refs: list[dict[str, object]] | None, *, limit: int = 4) -> list[str]:
    examples: list[str] = []
    for ref in list(refs or [])[:limit]:
        source = str(ref.get("source") or "")
        if source == "step":
            macro = str(ref.get("macro") or "macro")
            step_id = str(ref.get("step_id") or "?")
            step_type = str(ref.get("step_type") or "step")
            examples.append(f"{macro}:{step_id}:{step_type}")
        elif source == "bindings":
            examples.append(f"{ref.get('count') or 0} binding(s)")
        elif source == "window_watcher":
            examples.append(f"window-watcher:{ref.get('watcher')}")
        elif source:
            examples.append(source)
    return examples


def _track_status(status: str) -> str:
    lowered = str(status or "unknown").strip().lower()
    if lowered == "ok":
        return "ready"
    if lowered == "limited":
        return "degraded"
    if lowered == "missing":
        return "blocked"
    return "unknown"


def _overall_status(tracks: list[dict[str, Any]], *, session_available: bool) -> str:
    if not tracks:
        return "ready" if session_available else "unknown"
    states = {str(item.get("fit") or "unknown") for item in tracks}
    if "blocked" in states:
        return "blocked"
    if "degraded" in states:
        return "degraded"
    if states == {"ready"}:
        return "ready"
    return "unknown"


def _toolchain_by_capability(strategy: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("capability") or ""): dict(item)
        for item in list(strategy.get("toolchain_choices") or [])
        if isinstance(item, dict) and str(item.get("capability") or "")
    }


def _package_group_by_capability(package_plan: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("capability") or ""): dict(item)
        for item in list(package_plan.get("package_groups") or [])
        if isinstance(item, dict) and str(item.get("capability") or "")
    }


def build_session_fit_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )
    package_plan = _build_toolchain_package_plan(strategy)
    toolchain_by_capability = _toolchain_by_capability(strategy)
    package_group_by_capability = _package_group_by_capability(package_plan)
    issue_by_capability = {
        str(item.get("capability") or ""): dict(item)
        for item in list(capability_issues or [])
        if isinstance(item, dict) and str(item.get("capability") or "")
    }
    usage = capability_usage or {}

    capability_tracks: list[dict[str, Any]] = []
    used_capabilities = [cap for cap, refs in usage.items() if refs]
    for capability in used_capabilities:
        refs = list(usage.get(capability) or [])
        session_item = dict((capability_matrix or {}).get(capability) or {})
        session_status = str(session_item.get("status") or ("unknown" if capability_matrix else "not_checked"))
        fit = _track_status(session_status)
        toolchain = dict(toolchain_by_capability.get(capability) or {})
        package_group = dict(package_group_by_capability.get(capability) or {})
        issue = dict(issue_by_capability.get(capability) or {})
        capability_tracks.append(
            {
                "capability": capability,
                "usage_count": len(refs),
                "usage_examples": _usage_examples(refs),
                "fit": fit,
                "session_status": session_status,
                "recommended_session_mechanism": str(session_item.get("recommended") or "").strip() or None,
                "session_mechanisms": [str(x) for x in list(session_item.get("mechanisms") or []) if str(x)],
                "session_notes": [str(x) for x in list(session_item.get("notes") or []) if str(x)],
                "portal_backends": [str(x) for x in list(session_item.get("portal_backends") or []) if str(x)],
                "toolchain_choice": toolchain,
                "package_group": package_group,
                "issue": issue,
            }
        )

    overall = _overall_status(capability_tracks, session_available=bool(capability_matrix))
    focus_caps = [
        str(item.get("capability") or "")
        for item in capability_tracks
        if str(item.get("fit") or "") in {"blocked", "degraded"}
    ]
    if not focus_caps:
        focus_caps = [str(item.get("capability") or "") for item in capability_tracks]

    relevant_toolchains = [
        dict(toolchain_by_capability[cap])
        for cap in focus_caps
        if cap in toolchain_by_capability
    ]
    relevant_package_groups = [
        dict(package_group_by_capability[cap])
        for cap in focus_caps
        if cap in package_group_by_capability
    ]
    relevant_packages = _dedupe_keep_order(
        [pkg for group in relevant_package_groups for pkg in [str(x) for x in list(group.get("packages") or []) if str(x)]]
    )
    relevant_install_commands = {
        manager: f"{prefix} {' '.join(packages)}"
        for manager, prefix in {
            "apt": "sudo apt-get install -y",
            "dnf": "sudo dnf install -y",
            "pacman": "sudo pacman -S --needed",
            "zypper": "sudo zypper install -y",
        }.items()
        if (packages := _dedupe_keep_order([
            str((group.get("install_commands") or {}).get(manager) or "").strip().split(prefix, 1)[-1].strip()
            for group in relevant_package_groups
            if str((group.get("install_commands") or {}).get(manager) or "").strip()
        ]))
    }
    # The aggregation above can leave grouped strings. Normalize back into a single command.
    for manager, prefix in {
        "apt": "sudo apt-get install -y",
        "dnf": "sudo dnf install -y",
        "pacman": "sudo pacman -S --needed",
        "zypper": "sudo zypper install -y",
    }.items():
        tokens: list[str] = []
        for group in relevant_package_groups:
            cmd = str((group.get("install_commands") or {}).get(manager) or "").strip()
            if not cmd:
                continue
            tail = cmd.split(prefix, 1)[-1].strip()
            tokens.extend(tail.split())
        tokens = _dedupe_keep_order(tokens)
        if tokens:
            relevant_install_commands[manager] = f"{prefix} {' '.join(tokens)}"

    remediation_lanes: list[dict[str, Any]] = []
    for track in capability_tracks:
        fit = str(track.get("fit") or "unknown")
        if focus_caps and str(track.get("capability") or "") not in focus_caps:
            continue
        toolchain = dict(track.get("toolchain_choice") or {})
        package_group = dict(track.get("package_group") or {})
        issue = dict(track.get("issue") or {})
        notes = _dedupe_keep_order(
            [
                _first_text(issue, "suggestion", "message"),
                *[str(x) for x in list(track.get("session_notes") or []) if str(x)],
                _first_text(toolchain, "why", "risks"),
            ]
        )
        commands = _dedupe_keep_order(
            [
                *[str(x) for x in list(toolchain.get("commands") or []) if str(x)],
                "vhk doctor --json",
                f"vhk validate {project_dir.as_posix()} --json",
                f"vhk plan-project {project_dir.as_posix()} --json",
            ]
        )
        remediation_lanes.append(
            {
                "capability": str(track.get("capability") or ""),
                "fit": fit,
                "session_status": str(track.get("session_status") or "unknown"),
                "title": str(toolchain.get("title") or track.get("capability") or "capability"),
                "summary": _first_text(issue, "message", "summary") or _first_text(toolchain, "why", "summary"),
                "recommended_toolchain": str(toolchain.get("recommended_toolchain") or track.get("recommended_session_mechanism") or "").strip() or None,
                "packages": [str(x) for x in list(package_group.get("packages") or []) if str(x)],
                "install_commands": dict(package_group.get("install_commands") or {}),
                "commands": commands[:6],
                "notes": notes[:6],
                "usage_examples": [str(x) for x in list(track.get("usage_examples") or []) if str(x)],
            }
        )

    review_commands = _dedupe_keep_order(
        [
            "vhk doctor --json",
            f"vhk validate {project_dir.as_posix()} --json",
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-session-fit-pack {project_dir.as_posix()} --force --quiet",
            *[cmd for item in relevant_toolchains for cmd in [str(x) for x in list(item.get("commands") or []) if str(x)]],
        ]
    )

    return {
        "source_contract": "session_fit",
        "project": dict(strategy.get("project") or {}),
        "overview": dict(strategy.get("overview") or {}),
        "project_tags": list(strategy.get("project_tags") or []),
        "session_summary": {
            "overall_status": overall,
            "session_snapshot_attached": bool(capability_matrix),
            "required_capabilities": len(capability_tracks),
            "blocked_capabilities": [item.get("capability") for item in capability_tracks if item.get("fit") == "blocked"],
            "degraded_capabilities": [item.get("capability") for item in capability_tracks if item.get("fit") == "degraded"],
            "ready_capabilities": [item.get("capability") for item in capability_tracks if item.get("fit") == "ready"],
            "unknown_capabilities": [item.get("capability") for item in capability_tracks if item.get("fit") == "unknown"],
            "issue_count": len(list(capability_issues or [])),
        },
        "capability_tracks": capability_tracks,
        "relevant_toolchains": relevant_toolchains,
        "relevant_package_groups": relevant_package_groups,
        "relevant_packages": relevant_packages,
        "relevant_install_commands": relevant_install_commands,
        "remediation_lanes": remediation_lanes,
        "review_commands": review_commands,
        "stack_profiles": list(strategy.get("stack_profiles") or strategy.get("deployment_profiles") or []),
        "runtime_seams": list(strategy.get("runtime_seams") or []),
        "ecosystem_lessons": list(strategy.get("ecosystem_lessons") or []),
        "toolchain_choices": list(strategy.get("toolchain_choices") or []),
        "session_capabilities": dict(capability_matrix or {}),
        "session_issues": [dict(item) for item in list(capability_issues or []) if isinstance(item, dict)],
    }



def render_session_fit(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    session_summary = dict(plan.get("session_summary") or {})
    capability_tracks = _trim_items(plan.get("capability_tracks"), limit=8)
    package_groups = _trim_items(plan.get("relevant_package_groups"), limit=8)
    toolchains = _trim_items(plan.get("relevant_toolchains"), limit=6)
    review_commands = [str(x) for x in list(plan.get("review_commands") or []) if str(x)]

    lines: list[str] = []
    lines.append(f"# VHK session fit for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-session-fit-pack`. This is the planner/doctor handoff that compares what the project needs against what the current desktop session appears to provide.")
    lines.append("")
    lines.append("## Snapshot")
    lines.append("")
    lines.append(f"- Root: `{project.get('root_dir') or '.'}`")
    lines.append(f"- Declared desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Overall session fit: `{session_summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Live session snapshot attached: `{str(bool(session_summary.get('session_snapshot_attached'))).lower()}`")
    lines.append(f"- Session issues captured: {session_summary.get('issue_count', 0)}")
    lines.append("")

    if capability_tracks:
        lines.append("## Required capability fit")
        lines.append("")
        for track in capability_tracks:
            capability = track.get("capability") or "capability"
            lines.append(f"### {capability}")
            lines.append("")
            lines.append(f"- Fit: `{track.get('fit') or 'unknown'}`")
            lines.append(f"- Session status: `{track.get('session_status') or 'unknown'}`")
            lines.append(f"- Usage count: {track.get('usage_count', 0)}")
            recommended = str(track.get("recommended_session_mechanism") or "").strip()
            if recommended:
                lines.append(f"- Recommended mechanism on this host: `{recommended}`")
            mechs = [str(x) for x in list(track.get("session_mechanisms") or []) if str(x)]
            if mechs:
                lines.append(f"- Available mechanisms: `{', '.join(mechs)}`")
            examples = [str(x) for x in list(track.get("usage_examples") or []) if str(x)]
            if examples:
                lines.append("- Project references:")
                for example in examples[:4]:
                    lines.append(f"  - `{example}`")
            package_group = dict(track.get("package_group") or {})
            packages = [str(x) for x in list(package_group.get("packages") or []) if str(x)]
            if packages:
                lines.append(f"- Relevant bootstrap packages: `{', '.join(packages)}`")
            notes = [str(x) for x in list(track.get("session_notes") or []) if str(x)]
            if notes:
                lines.append("- Notes:")
                for note in notes[:3]:
                    lines.append(f"  - {note}")
            lines.append("")

    if toolchains:
        lines.append("## Host-relevant toolchain lanes")
        lines.append("")
        for item in toolchains:
            title = item.get("title") or item.get("id") or "toolchain"
            lines.append(f"### {title}")
            lines.append("")
            summary = _first_text(item, "why", "summary", "risks")
            if summary:
                lines.append(summary)
                lines.append("")
            recommended = str(item.get("recommended_toolchain") or "").strip()
            if recommended:
                lines.append(f"- Recommended: `{recommended}`")
            fallbacks = [str(x) for x in list(item.get("fallback_toolchains") or []) if str(x)]
            if fallbacks:
                lines.append(f"- Fallbacks: `{', '.join(fallbacks[:4])}`")
            commands = [str(x) for x in list(item.get("commands") or []) if str(x)]
            if commands:
                lines.append("- Review commands:")
                for cmd in commands[:4]:
                    lines.append(f"  - `{cmd}`")
            lines.append("")

    if package_groups:
        lines.append("## Relevant bootstrap groups")
        lines.append("")
        install_commands = dict(plan.get("relevant_install_commands") or {})
        for manager in ["apt", "dnf", "pacman", "zypper"]:
            cmd = str(install_commands.get(manager) or "").strip()
            if cmd:
                lines.append(f"- `{manager}` aggregate command: `{cmd}`")
        lines.append("")
        for group in package_groups:
            lines.append(f"### {group.get('title') or group.get('id') or 'Toolchain packages'}")
            lines.append("")
            lines.append(f"- Capability: `{group.get('capability') or 'unknown'}`")
            packages = [str(x) for x in list(group.get("packages") or []) if str(x)]
            if packages:
                lines.append(f"- Packages: `{', '.join(packages)}`")
            commands = dict(group.get("install_commands") or {})
            if commands:
                lines.append("- Example install commands:")
                for manager in ["apt", "dnf", "pacman", "zypper"]:
                    cmd = str(commands.get(manager) or "").strip()
                    if cmd:
                        lines.append(f"  - `{cmd}`")
            lines.append("")

    if review_commands:
        lines.append("## Review loop")
        lines.append("")
        for cmd in review_commands[:8]:
            lines.append(f"- `{cmd}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"



def render_session_fixups(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    session_summary = dict(plan.get("session_summary") or {})
    lanes = _trim_items(plan.get("remediation_lanes"), limit=10)
    session_issues = _trim_items(plan.get("session_issues"), limit=10)

    lines: list[str] = []
    lines.append(f"# VHK session fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-session-fit-pack`. Use this when the project shape is fine but the current host still needs helper installs, portal/backend review, or trigger/capture fallback decisions.")
    lines.append("")
    lines.append("## Priority summary")
    lines.append("")
    lines.append(f"- Overall session fit: `{session_summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Blocked capabilities: {len(list(session_summary.get('blocked_capabilities') or []))}")
    lines.append(f"- Degraded capabilities: {len(list(session_summary.get('degraded_capabilities') or []))}")
    lines.append(f"- Unknown capabilities: {len(list(session_summary.get('unknown_capabilities') or []))}")
    lines.append("")

    if lanes:
        lines.append("## Capability fixup lanes")
        lines.append("")
        for lane in lanes:
            lines.append(f"### {lane.get('title') or lane.get('capability') or 'capability'}")
            lines.append("")
            lines.append(f"- Capability: `{lane.get('capability') or 'unknown'}`")
            lines.append(f"- Fit: `{lane.get('fit') or 'unknown'}`")
            lines.append(f"- Session status: `{lane.get('session_status') or 'unknown'}`")
            recommended = str(lane.get("recommended_toolchain") or "").strip()
            if recommended:
                lines.append(f"- Target toolchain: `{recommended}`")
            summary = _first_text(lane, "summary")
            if summary:
                lines.append(f"- Problem framing: {summary}")
            usage_examples = [str(x) for x in list(lane.get("usage_examples") or []) if str(x)]
            if usage_examples:
                lines.append("- Project references:")
                for example in usage_examples[:4]:
                    lines.append(f"  - `{example}`")
            packages = [str(x) for x in list(lane.get("packages") or []) if str(x)]
            if packages:
                lines.append(f"- Suggested packages: `{', '.join(packages)}`")
            install_commands = dict(lane.get("install_commands") or {})
            if install_commands:
                lines.append("- Install commands:")
                for manager in ["apt", "dnf", "pacman", "zypper"]:
                    cmd = str(install_commands.get(manager) or "").strip()
                    if cmd:
                        lines.append(f"  - `{cmd}`")
            notes = [str(x) for x in list(lane.get("notes") or []) if str(x)]
            if notes:
                lines.append("- Notes:")
                for note in notes[:4]:
                    lines.append(f"  - {note}")
            commands = [str(x) for x in list(lane.get("commands") or []) if str(x)]
            if commands:
                lines.append("- Review commands:")
                for cmd in commands[:5]:
                    lines.append(f"  - `{cmd}`")
            lines.append("")

    if session_issues:
        lines.append("## Captured session issues")
        lines.append("")
        for item in session_issues:
            message = _first_text(item, "message", "summary")
            suggestion = _first_text(item, "suggestion", "notes")
            capability = str(item.get("capability") or "").strip()
            prefix = f"- `{capability}` — " if capability else "- "
            if suggestion:
                lines.append(f"{prefix}{message} — {suggestion}")
            else:
                lines.append(f"{prefix}{message}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"



def render_session_review_script(plan: Mapping[str, Any]) -> str:
    lines: list[str] = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'DEST="${DEST:-./build/session-fit}"',
        'mkdir -p "$DEST"',
        "",
        "run_json() {",
        '  name="$1"',
        '  shift',
        '  printf "+ %s\\n" "$*"',
        '  sh -lc "$*" > "$DEST/$name" 2> "$DEST/${name%.json}.stderr" || true',
        "}",
        "",
        'echo "Collecting VHK session-fit evidence into $DEST"',
        'run_json doctor.json "vhk doctor --json"',
        'run_json validate.json "vhk validate . --json"',
        'run_json plan-project.json "vhk plan-project . --json"',
        'printf "+ %s\\n" "vhk gen-session-fit-pack . --force --quiet"',
        'sh -lc "vhk gen-session-fit-pack . --force --quiet" || true',
        'echo "Session-fit refresh complete."',
        'echo "Review: $DEST/doctor.json, $DEST/validate.json, and $DEST/plan-project.json"',
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"



def write_session_fit_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    fit_doc: bool = True,
    fixups_doc: bool = True,
    plan_json: bool = True,
    review_script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_session_fit_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    written: dict[str, Path] = {}
    if fit_doc:
        path = out_dir / "VHK_SESSION_FIT.md"
        _write_if_allowed(path, render_session_fit(plan), force=force)
        written["fit_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_SESSION_FIXUPS.md"
        _write_if_allowed(path, render_session_fixups(plan), force=force)
        written["fixups_doc"] = path
    if plan_json:
        path = out_dir / "VHK_SESSION_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=False) + "\n", force=force)
        written["plan_json"] = path
    if review_script:
        path = script_dir / "vhk_review_session_fit.sh"
        _write_if_allowed(path, render_session_review_script(plan), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["review_script"] = path
    return written

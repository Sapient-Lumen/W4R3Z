from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from vhk.project.loader import load_project
from vhk.project.publish_pack import build_publish_plan
from vhk.project.strategy import summarize_project_strategy
from vhk.project.support_posture import summarize_support_posture_from_plan


_COMMAND_PREFIXES = (
    "vhk ",
    "python ",
    "python3 ",
    "pip ",
    "pip3 ",
    "uv ",
    "poetry ",
    "sudo ",
    "mkdir ",
    "cp ",
    "mv ",
    "ln ",
    "rm ",
    "chmod ",
    "install ",
    "systemctl ",
    "loginctl ",
    "journalctl ",
    "i3-msg ",
    "swaymsg ",
    "hyprctl ",
    "espanso ",
    "keyd ",
    "kanata ",
    "kmonad ",
    "rofi ",
    "fuzzel ",
    "wofi ",
    "tofi ",
    "dmenu ",
    "xdg-",
    "bash ",
    "sh ",
)


_ID_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")

_PACKAGE_ALIAS_MAP: dict[str, list[str]] = {
    "clipboard": ["wl-clipboard"],
    "helper/uinput seam": ["ydotool", "dotool"],
    "portal/compositor binds": ["xdg-desktop-portal"],
    "portal:globalshortcuts": ["xdg-desktop-portal"],
    "portal:inputcapture": ["xdg-desktop-portal"],
    "portal:remotedesktop(pointer)": ["xdg-desktop-portal"],
    "portal:screencast": ["xdg-desktop-portal"],
    "portal:screenshot": ["xdg-desktop-portal"],
    "grim/slurp": ["grim", "slurp"],
    "hyprctl": ["hyprland"],
    "swaymsg": ["sway"],
    "sway/i3 ipc": ["sway", "i3"],
    "compositor metadata bridge": ["sway", "hyprland", "kdotool"],
    "libei/eis": ["libei"],
    "libei/eis-ready stack": ["libei"],
}

_PACKAGE_MANAGER_INSTALL_PREFIXES: dict[str, str] = {
    "apt": "sudo apt-get install -y",
    "dnf": "sudo dnf install -y",
    "pacman": "sudo pacman -S --needed",
    "zypper": "sudo zypper install -y",
}

_PACKAGE_MANAGER_NAME_ALIASES: dict[str, dict[str, str]] = {
    "apt": {"i3": "i3-wm"},
    "pacman": {"i3": "i3-wm"},
}


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _portable_text(text: str, *, project_dir: Path) -> str:
    value = str(text)
    abs_dir = str(project_dir.resolve())
    try:
        posix_dir = project_dir.resolve().as_posix()
    except Exception:
        posix_dir = abs_dir
    for needle in {abs_dir, posix_dir}:
        if needle:
            value = value.replace(needle, ".")
    return value


def _is_shell_command(text: str) -> bool:
    stripped = str(text).strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    return any(lowered.startswith(prefix) for prefix in _COMMAND_PREFIXES)


def _normalize_commands(values: list[Any] | None, *, project_dir: Path) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in list(values or []):
        text = _portable_text(str(item).strip(), project_dir=project_dir)
        if not text or text in seen or not _is_shell_command(text):
            continue
        seen.add(text)
        out.append(text)
    return out


def _normalize_notes(values: list[Any] | None, *, project_dir: Path) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in list(values or []):
        text = _portable_text(str(item).strip(), project_dir=project_dir)
        if not text or text in seen or _is_shell_command(text):
            continue
        seen.add(text)
        out.append(text)
    return out


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
        value = str(item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _package_tokens_from_hint(value: str) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    lowered = text.lower()
    alias = _PACKAGE_ALIAS_MAP.get(lowered)
    if alias:
        return list(alias)
    if lowered.startswith("portal:"):
        return ["xdg-desktop-portal"]
    if re.fullmatch(r"[a-z0-9][a-z0-9+._-]*", lowered):
        return [lowered]
    return []


def _manager_package_name(package: str, manager: str) -> str:
    aliases = _PACKAGE_MANAGER_NAME_ALIASES.get(manager, {})
    return aliases.get(package, package)


def _build_toolchain_package_plan(strategy: Mapping[str, Any]) -> dict[str, Any]:
    toolchain_choices = [dict(item) for item in list(strategy.get("toolchain_choices") or []) if isinstance(item, dict)]
    package_groups: list[dict[str, Any]] = []
    all_packages: list[str] = []

    for choice in toolchain_choices:
        package_candidates: list[str] = []
        for raw in [
            *[str(x) for x in list(choice.get("package_hints") or []) if str(x)],
            str(choice.get("recommended_toolchain") or ""),
            *[str(x) for x in list(choice.get("fallback_toolchains") or []) if str(x)],
        ]:
            package_candidates.extend(_package_tokens_from_hint(raw))
        packages = _dedupe_keep_order(package_candidates)
        if not packages:
            continue

        manager_commands: dict[str, str] = {}
        for manager, prefix in _PACKAGE_MANAGER_INSTALL_PREFIXES.items():
            translated = _dedupe_keep_order([_manager_package_name(pkg, manager) for pkg in packages])
            if translated:
                manager_commands[manager] = f"{prefix} {' '.join(translated)}"

        group = {
            "id": str(choice.get("id") or str(choice.get("capability") or "packages")).strip() or "packages",
            "title": str(choice.get("title") or choice.get("capability") or "Toolchain packages"),
            "capability": str(choice.get("capability") or ""),
            "recommended_toolchain": str(choice.get("recommended_toolchain") or ""),
            "packages": packages,
            "package_hints": [str(x) for x in list(choice.get("package_hints") or []) if str(x)][:8],
            "install_commands": manager_commands,
        }
        package_groups.append(group)
        all_packages.extend(packages)

    all_packages = _dedupe_keep_order(all_packages)
    aggregate_commands = {
        manager: f"{prefix} {' '.join(_dedupe_keep_order([_manager_package_name(pkg, manager) for pkg in all_packages]))}"
        for manager, prefix in _PACKAGE_MANAGER_INSTALL_PREFIXES.items()
        if all_packages
    }

    return {
        "package_count": len(all_packages),
        "package_groups": package_groups,
        "packages": all_packages,
        "install_commands": aggregate_commands,
        "notes": [
            "Package names are best-effort hints derived from planner toolchain choices; verify distro-specific names before using them in a bootstrap script.",
            "Conceptual hints like portal consent flows or compositor config are intentionally kept in docs even when they do not map to a single package.",
        ],
    }


def build_setup_pack_plan(
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
    publish_plan = build_publish_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )
    support_posture = summarize_support_posture_from_plan(publish_plan)
    toolchain_packages = _build_toolchain_package_plan(strategy)

    recipes: list[dict[str, Any]] = []
    for raw in [dict(item) for item in list(strategy.get("setup_recipes") or []) if isinstance(item, dict)]:
        recipe_id = str(raw.get("id") or "").strip()
        if not recipe_id:
            continue
        recipes.append(
            {
                "id": recipe_id,
                "title": str(raw.get("title") or recipe_id),
                "category": str(raw.get("category") or "setup"),
                "audience": str(raw.get("audience") or "author"),
                "priority": str(raw.get("priority") or "medium"),
                "summary": _portable_text(_first_text(raw, "summary", "why", "description", "notes"), project_dir=project_dir),
                "surface_ids": [str(x) for x in list(raw.get("surface_ids") or []) if str(x)],
                "artifacts": [_portable_text(str(x), project_dir=project_dir) for x in list(raw.get("install_targets") or raw.get("artifacts") or []) if str(x)][:8],
                "install_steps": [_portable_text(str(x), project_dir=project_dir) for x in list(raw.get("install_steps") or []) if str(x)][:8],
                "verify_steps": [_portable_text(str(x), project_dir=project_dir) for x in list(raw.get("verify_steps") or []) if str(x)][:8],
                "rollback_steps": [_portable_text(str(x), project_dir=project_dir) for x in list(raw.get("rollback_steps") or []) if str(x)][:8],
                "acceptance_checks": [_portable_text(str(x), project_dir=project_dir) for x in list(raw.get("acceptance_checks") or []) if str(x)][:8],
                "generator_commands": _normalize_commands(list(raw.get("generator_commands") or []), project_dir=project_dir),
                "generator_notes": _normalize_notes(list(raw.get("generator_commands") or []), project_dir=project_dir),
                "validation_commands": _normalize_commands(list(raw.get("validation_commands") or []), project_dir=project_dir),
                "validation_notes": _normalize_notes(list(raw.get("validation_commands") or []), project_dir=project_dir),
                "first_wave": bool(raw.get("first_wave") or False),
            }
        )

    recipe_summary = {
        "recipe_count": len(recipes),
        "first_wave_count": sum(1 for item in recipes if item.get("first_wave")),
        "generator_command_count": sum(len(list(item.get("generator_commands") or [])) for item in recipes),
        "validation_command_count": sum(len(list(item.get("validation_commands") or [])) for item in recipes),
        "categories": sorted({str(item.get("category") or "setup") for item in recipes}),
        "audiences": sorted({str(item.get("audience") or "author") for item in recipes}),
    }

    return {
        "project": dict(strategy.get("project") or {}),
        "overview": dict(strategy.get("overview") or {}),
        "support_posture": support_posture,
        "recommended_rollout": _trim_items(publish_plan.get("recommended_rollout"), limit=6),
        "setup_recipes": recipes,
        "setup_summary": recipe_summary,
        "publish_commands": [str(x) for x in list(publish_plan.get("publish_commands") or []) if str(x)][:8],
        "toolchain_packages": toolchain_packages,
        "session_issues": [dict(x) for x in list(strategy.get("session_issues") or []) if isinstance(x, dict)][:8],
        "source_contract": "setup_recipes",
        "script_paths": {
            "apply_script": "scripts/vhk_apply_setup_recipes.sh",
            "verify_script": "scripts/vhk_verify_setup_recipes.sh",
            "package_script": "scripts/vhk_install_toolchain_packages.sh",
        },
    }


def render_setup_guide(plan: Mapping[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    posture = dict(plan.get("support_posture") or {})
    recipes = [dict(item) for item in list(plan.get("setup_recipes") or []) if isinstance(item, dict)]
    rollout = [dict(item) for item in list(plan.get("recommended_rollout") or []) if isinstance(item, dict)]
    summary = dict(plan.get("setup_summary") or {})
    toolchain_packages = dict(plan.get("toolchain_packages") or {})
    package_groups = [dict(item) for item in list(toolchain_packages.get("package_groups") or []) if isinstance(item, dict)]
    script_paths = dict(plan.get("script_paths") or {})
    session_issues = [dict(item) for item in list(plan.get("session_issues") or []) if isinstance(item, dict)]

    lines: list[str] = []
    lines.append(f"# VHK setup guide for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-setup-pack`. This turns planner-backed `setup_recipes` into a concrete install/review handoff instead of leaving them trapped inside `vhk plan-project --json` output.")
    lines.append("")
    lines.append("## Project snapshot")
    lines.append("")
    lines.append(f"- Root: `{project.get('root_dir') or '.'}`")
    lines.append(f"- Desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Setup recipes: {summary.get('recipe_count', 0)}")
    lines.append(f"- First-wave recipes: {summary.get('first_wave_count', 0)}")
    lines.append("")

    headline = str(posture.get("headline") or "").strip()
    if headline:
        lines.append("## Public support headline")
        lines.append("")
        lines.append(headline)
        lines.append("")

    if package_groups:
        lines.append("## Toolchain package bootstrap")
        lines.append("")
        lines.append("These package hints are derived from planner `toolchain_choices`, then normalized into distro-oriented install commands. They are a bootstrap lane, not a portability guarantee.")
        lines.append("")
        lines.append(f"- Suggested packages: {toolchain_packages.get('package_count', 0)}")
        lines.append(f"- Helper script: `{script_paths.get('package_script') or 'scripts/vhk_install_toolchain_packages.sh'}`")
        lines.append("")
        aggregate_commands = dict(toolchain_packages.get("install_commands") or {})
        if aggregate_commands:
            lines.append("Aggregate install commands:")
            for manager in ["apt", "dnf", "pacman", "zypper"]:
                cmd = str(aggregate_commands.get(manager) or "").strip()
                if cmd:
                    lines.append(f"- `{manager}`: `{cmd}`")
            lines.append("")
        for group in package_groups:
            lines.append(f"### {group.get('title') or group.get('id') or 'Toolchain packages'}")
            lines.append("")
            lines.append(f"- Capability: `{group.get('capability') or 'unknown'}`")
            lines.append(f"- Recommended toolchain: `{group.get('recommended_toolchain') or 'unknown'}`")
            packages = [str(x) for x in list(group.get("packages") or []) if str(x)]
            if packages:
                lines.append(f"- Suggested packages: `{', '.join(packages)}`")
            hints = [str(x) for x in list(group.get("package_hints") or []) if str(x)]
            if hints:
                lines.append(f"- Raw planner hints: `{', '.join(hints[:6])}`")
            commands = dict(group.get("install_commands") or {})
            if commands:
                lines.append("- Example install commands:")
                for manager in ["apt", "dnf", "pacman", "zypper"]:
                    cmd = str(commands.get(manager) or "").strip()
                    if cmd:
                        lines.append(f"  - `{manager}`: `{cmd}`")
            lines.append("")
        for note in [str(x) for x in list(toolchain_packages.get("notes") or []) if str(x)][:3]:
            lines.append(f"- {note}")
        lines.append("")

    if rollout:
        lines.append("## Recommended rollout order")
        lines.append("")
        lines.append("Start with the strongest-fit lane before attempting weaker or more caveated environments.")
        lines.append("")
        for idx, item in enumerate(rollout, start=1):
            lines.append(f"### {idx}. {item.get('title') or item.get('id') or 'target'}")
            lines.append(f"Fit: `{item.get('fit') or 'unknown'}` · Score: {item.get('score') or 0}")
            summary_text = _first_text(item, "summary")
            if summary_text:
                lines.append("")
                lines.append(summary_text)
            commands = [str(x) for x in list(item.get("commands") or []) if str(x)]
            if commands:
                lines.append("")
                lines.append("Starter commands:")
                for cmd in commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")

    if recipes:
        lines.append("## Setup recipes")
        lines.append("")
        lines.append("The generated scripts in `scripts/` are derived from these recipes. Use them for repeatable export/verification loops, then keep the install/rollback notes visible during rollout.")
        lines.append("")
        for recipe in recipes:
            lines.append(f"### {recipe.get('title') or recipe.get('id') or 'recipe'}")
            lines.append("")
            lines.append(f"- Recipe id: `{recipe.get('id')}`")
            lines.append(f"- Priority: `{recipe.get('priority') or 'medium'}` · Audience: `{recipe.get('audience') or 'author'}` · Category: `{recipe.get('category') or 'setup'}`")
            summary_text = str(recipe.get("summary") or "").strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            surface_ids = [str(x) for x in list(recipe.get("surface_ids") or []) if str(x)]
            if surface_ids:
                lines.append(f"- Surface ids: `{', '.join(surface_ids)}`")
            artifacts = [str(x) for x in list(recipe.get("artifacts") or []) if str(x)]
            if artifacts:
                lines.append("- Install targets/artifacts:")
                for item in artifacts[:5]:
                    lines.append(f"  - `{item}`")
            gen_cmds = [str(x) for x in list(recipe.get("generator_commands") or []) if str(x)]
            if gen_cmds:
                lines.append("- Generator commands:")
                for cmd in gen_cmds[:6]:
                    lines.append(f"  - `{cmd}`")
            gen_notes = [str(x) for x in list(recipe.get("generator_notes") or []) if str(x)]
            if gen_notes:
                lines.append("- Generator notes:")
                for note in gen_notes[:4]:
                    lines.append(f"  - {note}")
            val_cmds = [str(x) for x in list(recipe.get("validation_commands") or []) if str(x)]
            if val_cmds:
                lines.append("- Verification commands:")
                for cmd in val_cmds[:6]:
                    lines.append(f"  - `{cmd}`")
            val_notes = [str(x) for x in list(recipe.get("validation_notes") or []) if str(x)]
            if val_notes:
                lines.append("- Verification notes:")
                for note in val_notes[:4]:
                    lines.append(f"  - {note}")
            install_steps = [str(x) for x in list(recipe.get("install_steps") or []) if str(x)]
            if install_steps:
                lines.append("- Install steps:")
                for step in install_steps[:5]:
                    lines.append(f"  - {step}")
            verify_steps = [str(x) for x in list(recipe.get("verify_steps") or []) if str(x)]
            if verify_steps:
                lines.append("- Acceptance checks:")
                for step in verify_steps[:5]:
                    lines.append(f"  - {step}")
            rollback_steps = [str(x) for x in list(recipe.get("rollback_steps") or []) if str(x)]
            if rollback_steps:
                lines.append("- Rollback steps:")
                for step in rollback_steps[:4]:
                    lines.append(f"  - {step}")
            lines.append("")

    if session_issues:
        lines.append("## Current session mismatches")
        lines.append("")
        lines.append("These come from the optional session check. Treat them as local rollout warnings, not universal Linux facts.")
        lines.append("")
        for item in session_issues[:6]:
            msg = str(item.get("message") or "session issue")
            sev = str(item.get("severity") or "warning")
            suggestion = str(item.get("suggestion") or "").strip()
            lines.append(f"- `{sev}` — {msg}")
            if suggestion:
                lines.append(f"  - {suggestion}")
        lines.append("")

    lines.append("## Generated script entrypoints")
    lines.append("")
    lines.append("- `scripts/vhk_apply_setup_recipes.sh` — rerun planner-backed generator commands, optionally filtered by recipe id")
    lines.append("- `scripts/vhk_verify_setup_recipes.sh` — rerun planner-backed verification commands, optionally filtered by recipe id")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_setup_matrix(plan: Mapping[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    recipes = [dict(item) for item in list(plan.get("setup_recipes") or []) if isinstance(item, dict)]
    toolchain_packages = dict(plan.get("toolchain_packages") or {})
    package_groups = [dict(item) for item in list(toolchain_packages.get("package_groups") or []) if isinstance(item, dict)]
    lines: list[str] = []
    lines.append(f"# VHK setup recipe matrix for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-setup-pack`. Read this as the short queue of which setup recipes exist, what they touch, and whether they already have shell-runnable generator/verification commands.")
    lines.append("")
    if package_groups:
        lines.append("## Toolchain package groups")
        lines.append("")
        lines.append(f"- Normalized packages: {toolchain_packages.get('package_count', 0)}")
        aggregate_commands = dict(toolchain_packages.get("install_commands") or {})
        for manager in ["apt", "dnf", "pacman", "zypper"]:
            cmd = str(aggregate_commands.get(manager) or "").strip()
            if cmd:
                lines.append(f"- `{manager}` aggregate command: `{cmd}`")
        lines.append("")
        for group in package_groups:
            lines.append(f"### {group.get('title') or group.get('id') or 'Toolchain packages'}")
            lines.append("")
            lines.append(f"- Capability: `{group.get('capability') or 'unknown'}`")
            lines.append(f"- Package count: {len(list(group.get('packages') or []))}")
            packages = [str(x) for x in list(group.get("packages") or []) if str(x)]
            if packages:
                lines.append(f"- Packages: `{', '.join(packages)}`")
            lines.append("")
    for recipe in recipes:
        lines.append(f"## {recipe.get('title') or recipe.get('id') or 'recipe'}")
        lines.append("")
        lines.append(f"- Recipe id: `{recipe.get('id')}`")
        lines.append(f"- Category: `{recipe.get('category') or 'setup'}`")
        lines.append(f"- Priority: `{recipe.get('priority') or 'medium'}`")
        lines.append(f"- First wave: `{str(bool(recipe.get('first_wave'))).lower()}`")
        lines.append(f"- Runnable generator commands: {len(list(recipe.get('generator_commands') or []))}")
        lines.append(f"- Runnable verification commands: {len(list(recipe.get('validation_commands') or []))}")
        note = str(recipe.get("summary") or "").strip()
        if note:
            lines.append(f"- Summary: {note}")
        artifacts = [str(x) for x in list(recipe.get("artifacts") or []) if str(x)]
        if artifacts:
            lines.append("- Artifacts/targets:")
            for item in artifacts[:5]:
                lines.append(f"  - `{item}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_recipe_case_script(plan: Mapping[str, Any], *, stage: str) -> str:
    recipes = [dict(item) for item in list(plan.get("setup_recipes") or []) if isinstance(item, dict)]
    label = "generator" if stage == "generator" else "verification"
    command_key = "generator_commands" if stage == "generator" else "validation_commands"
    note_key = "generator_notes" if stage == "generator" else "validation_notes"

    lines: list[str] = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'RECIPE_FILTER="${RECIPE_FILTER:-all}"',
        "",
        "selected() {",
        '  if [ "$RECIPE_FILTER" = "all" ] || [ -z "$RECIPE_FILTER" ]; then',
        "    return 0",
        "  fi",
        '  case ",${RECIPE_FILTER}," in',
        "    *,${1},*) return 0 ;;",
        "    *) return 1 ;;",
        "  esac",
        "}",
        "",
        "run_cmd() {",
        '  printf "+ %s\n" "$1"',
        '  sh -lc "$1"',
        "}",
        "",
        f'echo "Running VHK {label} recipe commands (filter=$RECIPE_FILTER)"',
        "",
    ]
    for recipe in recipes:
        recipe_id = _ID_SLUG_RE.sub("-", str(recipe.get("id") or "").strip()) or "recipe"
        title = str(recipe.get("title") or recipe_id)
        cmds = [str(x) for x in list(recipe.get(command_key) or []) if str(x)]
        notes = [str(x) for x in list(recipe.get(note_key) or []) if str(x)]
        lines.extend([
            f"if selected '{recipe_id}'; then",
            "  echo ''",
            f"  echo '== {title} ({recipe_id}) =='",
        ])
        if cmds:
            for cmd in cmds:
                lines.append(f"  run_cmd {json.dumps(cmd)}")
        else:
            lines.append(f"  echo 'No runnable {label} commands captured for {recipe_id}.'")
        if notes:
            lines.append("  echo 'Notes:'")
            for note in notes[:4]:
                lines.append(f"  printf '  - %s\\n' {json.dumps(note)}")
        lines.append("fi")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def render_apply_setup_script(plan: Mapping[str, Any]) -> str:
    return _render_recipe_case_script(plan, stage="generator")


def render_verify_setup_script(plan: Mapping[str, Any]) -> str:
    return _render_recipe_case_script(plan, stage="validation")


def render_package_setup_script(plan: Mapping[str, Any]) -> str:
    toolchain_packages = dict(plan.get("toolchain_packages") or {})
    package_groups = [dict(item) for item in list(toolchain_packages.get("package_groups") or []) if isinstance(item, dict)]

    lines: list[str] = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'PACKAGE_FILTER="${PACKAGE_FILTER:-all}"',
        'PACKAGE_MANAGER="${PACKAGE_MANAGER:-auto}"',
        'RUN_INSTALL="${RUN_INSTALL:-0}"',
        "",
        "selected() {",
        '  if [ "$PACKAGE_FILTER" = "all" ] || [ -z "$PACKAGE_FILTER" ]; then',
        "    return 0",
        "  fi",
        '  case ",$PACKAGE_FILTER," in',
        "    *,$1,*) return 0 ;;",
        "    *) return 1 ;;",
        "  esac",
        "}",
        "",
        "detect_manager() {",
        '  if [ "$PACKAGE_MANAGER" != "auto" ]; then',
        '    printf "%s\n" "$PACKAGE_MANAGER"',
        "    return 0",
        "  fi",
        "  if command -v apt-get >/dev/null 2>&1; then printf 'apt\n'; return 0; fi",
        "  if command -v dnf >/dev/null 2>&1; then printf 'dnf\n'; return 0; fi",
        "  if command -v pacman >/dev/null 2>&1; then printf 'pacman\n'; return 0; fi",
        "  if command -v zypper >/dev/null 2>&1; then printf 'zypper\n'; return 0; fi",
        "  printf 'none\n'",
        "}",
        "",
        "run_cmd() {",
        '  printf "+ %s\n" "$1"',
        '  if [ "$RUN_INSTALL" = "1" ]; then',
        '    sh -lc "$1"',
        "  else",
        "    echo '(dry-run; set RUN_INSTALL=1 to execute)'",
        "  fi",
        "}",
        "",
        'echo "Running VHK toolchain package bootstrap (filter=$PACKAGE_FILTER manager=$PACKAGE_MANAGER run_install=$RUN_INSTALL)"',
        "MANAGER=$(detect_manager)",
        'echo "Detected package manager: $MANAGER"',
        'if [ "$MANAGER" = "none" ]; then',
        '  echo "No supported package manager detected. Set PACKAGE_MANAGER=apt|dnf|pacman|zypper to print commands explicitly."',
        "  exit 0",
        "fi",
        "",
    ]

    for group in package_groups:
        group_id = _ID_SLUG_RE.sub("-", str(group.get("id") or "packages").strip()) or "packages"
        title = str(group.get("title") or group_id)
        packages = [str(x) for x in list(group.get("packages") or []) if str(x)]
        commands = dict(group.get("install_commands") or {})
        lines.extend([
            f"if selected '{group_id}'; then",
            "  echo ''",
            f"  echo '== {title} ({group_id}) =='",
        ])
        if packages:
            lines.append(f"  printf 'Packages: %s\n' {json.dumps(', '.join(packages))}")
        lines.extend([
            '  case "$MANAGER" in',
        ])
        for manager in ["apt", "dnf", "pacman", "zypper"]:
            cmd = str(commands.get(manager) or "").strip()
            if cmd:
                lines.append(f"    {manager}) run_cmd {json.dumps(cmd)} ;;")
        lines.extend([
            "    *) echo 'No generated install command for this package manager.' ;;",
            "  esac",
            "fi",
            "",
        ])

    return "\n".join(lines).rstrip() + "\n"


def write_setup_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    guide: bool = True,
    matrix: bool = True,
    plan_json: bool = True,
    apply_script: bool = True,
    verify_script: bool = True,
    package_script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_setup_pack_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    written: dict[str, Path] = {}
    if guide:
        path = out_dir / "VHK_SETUP_GUIDE.md"
        _write_if_allowed(path, render_setup_guide(plan), force=force)
        written["guide"] = path
    if matrix:
        path = out_dir / "VHK_SETUP_MATRIX.md"
        _write_if_allowed(path, render_setup_matrix(plan), force=force)
        written["matrix"] = path
    if plan_json:
        path = out_dir / "VHK_SETUP_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if apply_script:
        path = script_dir / "vhk_apply_setup_recipes.sh"
        _write_if_allowed(path, render_apply_setup_script(plan), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["apply_script"] = path
    if verify_script:
        path = script_dir / "vhk_verify_setup_recipes.sh"
        _write_if_allowed(path, render_verify_setup_script(plan), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["verify_script"] = path
    if package_script:
        path = script_dir / "vhk_install_toolchain_packages.sh"
        _write_if_allowed(path, render_package_setup_script(plan), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["package_script"] = path
    return written

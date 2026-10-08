from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from vhk.project.authority_policy import build_project_authority_policy
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


def _group_filter_id(value: str) -> str:
    return _ID_SLUG_RE.sub("-", str(value or "packages").strip()) or "packages"


def _lane_filter_id(group_id: str, member_id: str) -> str:
    return f"{_group_filter_id(group_id)}__{_group_filter_id(member_id or 'lane')}"


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


def _install_commands_for_packages(packages: list[str]) -> dict[str, str]:
    commands: dict[str, str] = {}
    for manager, prefix in _PACKAGE_MANAGER_INSTALL_PREFIXES.items():
        translated = _dedupe_keep_order([_manager_package_name(pkg, manager) for pkg in packages])
        if translated:
            commands[manager] = f"{prefix} {' '.join(translated)}"
    return commands


def _alternative_order(item: Mapping[str, Any]) -> int:
    value = item.get("alternative_order")
    try:
        return int(value)
    except (TypeError, ValueError):
        return 999


def _observed_status_bucket(value: str | None) -> str:
    lowered = str(value or "unknown").strip().lower()
    if lowered in {"ready", "ok", "pass"}:
        return "ready"
    if lowered in {"degraded", "warning", "limited", "unknown"}:
        return "degraded"
    if lowered in {"missing", "blocked", "permission_denied", "service_missing", "interface_missing", "backend_missing", "fail"}:
        return "blocked"
    return "degraded"


def _summarize_host_truth(requirements: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = [dict(item) for item in list(requirements or []) if isinstance(item, dict)]
    buckets = {"blocked": [], "degraded": [], "ready": []}
    for row in rows:
        buckets.setdefault(_observed_status_bucket(str(row.get("observed_status") or "unknown")), []).append(row)

    if buckets["blocked"]:
        status = "blocked"
    elif buckets["degraded"]:
        status = "degraded"
    elif buckets["ready"]:
        status = "ready"
    else:
        status = "unknown"

    return {
        "status": status,
        "requirement_count": len(rows),
        "blocked_count": len(buckets["blocked"]),
        "degraded_count": len(buckets["degraded"]),
        "ready_count": len(buckets["ready"]),
        "top_blocked_requirement_ids": [str(item.get("id") or "") for item in buckets["blocked"][:6] if str(item.get("id") or "")],
        "top_degraded_requirement_ids": [str(item.get("id") or "") for item in buckets["degraded"][:6] if str(item.get("id") or "")],
    }


def _build_requirement_alternative_groups(strategy: Mapping[str, Any]) -> list[dict[str, Any]]:
    requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
    grouped: dict[str, dict[str, Any]] = {}
    for item in requirements:
        group_id = str(item.get("alternative_group") or "").strip()
        if not group_id:
            continue
        group = grouped.setdefault(
            group_id,
            {
                "id": group_id,
                "title": str(item.get("alternative_title") or group_id).strip() or group_id,
                "policy": str(item.get("alternative_policy") or "one_of").strip() or "one_of",
                "capability": str(item.get("capability") or "").strip() or None,
                "members": [],
            },
        )
        group["members"].append(dict(item))

    out: list[dict[str, Any]] = []
    for group in grouped.values():
        members = [dict(item) for item in list(group.get("members") or []) if isinstance(item, dict)]
        if not members:
            continue
        members.sort(
            key=lambda item: (
                _alternative_order(item),
                {"required": 0, "recommended": 1, "conditional": 2}.get(str(item.get("priority") or "conditional"), 2),
                str(item.get("title") or item.get("id") or ""),
            )
        )
        out.append(
            {
                "id": str(group.get("id") or ""),
                "title": str(group.get("title") or group.get("id") or ""),
                "policy": str(group.get("policy") or "one_of"),
                "capability": group.get("capability"),
                "members": members,
            }
        )
    out.sort(key=lambda item: str(item.get("title") or item.get("id") or ""))
    return out


def _build_toolchain_package_plan(strategy: Mapping[str, Any]) -> dict[str, Any]:
    toolchain_choices = [dict(item) for item in list(strategy.get("toolchain_choices") or []) if isinstance(item, dict)]
    alternative_groups = _build_requirement_alternative_groups(strategy)
    alternative_groups_by_capability: dict[str, list[dict[str, Any]]] = {}
    for group in alternative_groups:
        capability = str(group.get("capability") or "").strip()
        if not capability:
            continue
        alternative_groups_by_capability.setdefault(capability, []).append(dict(group))

    package_groups: list[dict[str, Any]] = []
    all_packages: list[str] = []

    for choice in toolchain_choices:
        capability = str(choice.get("capability") or "").strip()
        group_id = str(choice.get("id") or str(choice.get("capability") or "packages")).strip() or "packages"
        recommended_toolchain = str(choice.get("recommended_toolchain") or "").strip()
        recommended_tokens = _dedupe_keep_order(_package_tokens_from_hint(recommended_toolchain))
        recommended_lower = recommended_toolchain.lower()
        fallback_toolchains = [str(x) for x in list(choice.get("fallback_toolchains") or []) if str(x)]
        package_hints = [str(x) for x in list(choice.get("package_hints") or []) if str(x)]

        package_candidates: list[str] = []
        for raw in [*package_hints, recommended_toolchain, *fallback_toolchains]:
            package_candidates.extend(_package_tokens_from_hint(raw))
        all_candidate_packages = _dedupe_keep_order(package_candidates)

        synthetic_alternative_groups: list[dict[str, Any]] = []
        if {"dotool", "ydotool"}.intersection(all_candidate_packages):
            helper_members: list[dict[str, Any]] = []
            if "dotool" in all_candidate_packages or "dotoolc" in all_candidate_packages:
                helper_members.append(
                    {
                        "id": "dotool-daemon",
                        "title": "Persistent dotool daemon",
                        "packages": ["dotool", "dotoolc"],
                        "priority": "recommended",
                        "alternative_order": 0,
                    }
                )
            if "ydotool" in all_candidate_packages:
                helper_members.append(
                    {
                        "id": "ydotool-daemon",
                        "title": "Persistent ydotool daemon",
                        "packages": ["ydotool"],
                        "priority": "recommended",
                        "alternative_order": 1,
                    }
                )
            if len(helper_members) > 1:
                synthetic_alternative_groups.append(
                    {
                        "id": "wayland-uinput-helper-daemon",
                        "title": "Wayland uinput helper daemon lane",
                        "policy": "one_of",
                        "capability": capability,
                        "members": helper_members,
                    }
                )

        alternative_package_groups: list[dict[str, Any]] = []
        alternative_package_union: set[str] = set()
        selected_alternative_packages: list[str] = []
        selected_alternative_ids: list[str] = []

        candidate_alt_groups: list[dict[str, Any]] = [dict(item) for item in synthetic_alternative_groups]
        for raw_alt_group in alternative_groups:
            alt_group = dict(raw_alt_group)
            alt_capability = str(alt_group.get("capability") or "").strip()
            members = [dict(item) for item in list(alt_group.get("members") or []) if isinstance(item, dict)]
            member_package_union = {
                str(x)
                for member in members
                for x in [str(v) for v in list(member.get("packages") or []) if str(v)]
                if str(x)
            }
            if alt_capability == capability or member_package_union.intersection(all_candidate_packages):
                candidate_alt_groups.append({**alt_group, "members": members})

        for alt_group in candidate_alt_groups:
            members = [dict(item) for item in list(alt_group.get("members") or []) if isinstance(item, dict)]
            members.sort(
                key=lambda item: (
                    _alternative_order(item),
                    {"required": 0, "recommended": 1, "conditional": 2}.get(str(item.get("priority") or "conditional"), 2),
                    str(item.get("title") or item.get("id") or ""),
                )
            )
            rendered_members: list[dict[str, Any]] = []
            matching_members: list[dict[str, Any]] = []
            for member in members:
                member_id = str(member.get("id") or "").strip()
                member_packages = _dedupe_keep_order(
                    [str(x) for x in list(member.get("packages") or []) if str(x)]
                )
                if not member_packages:
                    continue
                alternative_package_union.update(member_packages)
                rendered = {
                    "id": member_id,
                    "title": str(member.get("title") or member_id).strip() or member_id,
                    "packages": member_packages,
                    "package_count": len(member_packages),
                    "install_commands": _install_commands_for_packages(member_packages),
                    "alternative_order": _alternative_order(member),
                    "priority": str(member.get("priority") or "conditional"),
                    "filter_id": _lane_filter_id(group_id, member_id),
                    "matches_recommended_toolchain": bool(set(member_packages).intersection(recommended_tokens)) or (member_id and member_id in recommended_lower),
                }
                rendered_members.append(rendered)
                if rendered["matches_recommended_toolchain"]:
                    matching_members.append(rendered)

            if not rendered_members:
                continue

            selected_member: dict[str, Any] | None = None
            if matching_members:
                selected_member = sorted(
                    matching_members,
                    key=lambda item: (int(item.get("alternative_order")) if item.get("alternative_order") is not None else 999, str(item.get("id") or "")),
                )[0]
            elif "helper" in recommended_lower or "uinput" in recommended_lower or "daemon" in recommended_lower:
                selected_member = rendered_members[0]
            elif str(alt_group.get("policy") or "").strip().lower() == "one_of" and (
                capability == "global_hotkeys" or "remapper" in str(alt_group.get("id") or "").lower() or "remapper" in str(alt_group.get("title") or "").lower()
            ):
                selected_member = rendered_members[0]

            selected_member_id = str(selected_member.get("id") or "") if selected_member else ""
            if selected_member_id:
                selected_alternative_ids.append(selected_member_id)
                selected_alternative_packages.extend([str(x) for x in list(selected_member.get("packages") or []) if str(x)])

            alt_member_packages = {
                str(x)
                for member in rendered_members
                for x in list(member.get("packages") or [])
                if str(x)
            }
            base_packages_for_group = [pkg for pkg in all_candidate_packages if pkg not in alt_member_packages]
            rendered_group = {
                "id": str(alt_group.get("id") or ""),
                "title": str(alt_group.get("title") or alt_group.get("id") or ""),
                "policy": str(alt_group.get("policy") or "one_of"),
                "capability": capability,
                "selected_by_default": bool(selected_member_id),
                "selected_member_id": selected_member_id or None,
                "selected_member_title": (str(selected_member.get("title") or selected_member_id or "") if selected_member else None) or None,
                "selected_filter_id": (_lane_filter_id(group_id, selected_member_id) if selected_member_id else None),
                "members": [],
            }
            for member in rendered_members:
                effective_packages = _dedupe_keep_order(base_packages_for_group + [str(x) for x in list(member.get("packages") or []) if str(x)])
                rendered_group["members"].append(
                    {
                        **member,
                        "selected_by_default": str(member.get("id") or "") == selected_member_id,
                        "effective_packages": effective_packages,
                        "effective_install_commands": _install_commands_for_packages(effective_packages),
                    }
                )
            alternative_package_groups.append(rendered_group)

        base_packages = [pkg for pkg in all_candidate_packages if pkg not in alternative_package_union]
        packages = _dedupe_keep_order(base_packages + selected_alternative_packages)
        if not packages and all_candidate_packages:
            packages = list(all_candidate_packages)
        if not packages:
            continue

        group = {
            "id": group_id,
            "title": str(choice.get("title") or choice.get("capability") or "Toolchain packages"),
            "capability": capability,
            "recommended_toolchain": recommended_toolchain,
            "packages": packages,
            "base_packages": base_packages,
            "package_hints": package_hints[:8],
            "install_commands": _install_commands_for_packages(packages),
            "alternative_package_groups": alternative_package_groups,
            "selected_alternative_ids": _dedupe_keep_order(selected_alternative_ids),
            "selected_filter_ids": [_lane_filter_id(group_id, member_id) for member_id in _dedupe_keep_order(selected_alternative_ids)],
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
            "Alternative helper families are kept as explicit choose-one lanes when planner host requirements already model them that way, so bootstrap output stops implying every fallback helper belongs on the same host.",
            "Conceptual hints like portal consent flows or compositor config are intentionally kept in docs even when they do not map to a single package.",
        ],
    }


def build_setup_pack_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
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
    from vhk.project.host_contract_pack import build_host_contract_plan

    support_posture = summarize_support_posture_from_plan(publish_plan)
    toolchain_packages = _build_toolchain_package_plan(strategy)
    host_plan = build_host_contract_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )
    host_requirements = [dict(item) for item in list(host_plan.get("host_requirements") or []) if isinstance(item, dict)]
    host_truth = _summarize_host_truth(host_requirements)
    portal_route_contract = dict(host_plan.get("portal_route_contract") or {})
    authority_policy = build_project_authority_policy(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

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
        "authority_policy": authority_policy,
        "host_truth": host_truth,
        "host_requirements": host_requirements,
        "portal_route_contract": portal_route_contract,
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
    host_truth = dict(plan.get("host_truth") or {})
    host_requirements = [dict(item) for item in list(plan.get("host_requirements") or []) if isinstance(item, dict)]
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    authority_policy = dict(plan.get("authority_policy") or {})
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
            base_packages = [str(x) for x in list(group.get("base_packages") or []) if str(x)]
            if packages:
                lines.append(f"- Default bootstrap packages: `{', '.join(packages)}`")
            if base_packages and base_packages != packages:
                lines.append(f"- Base packages shared across helper choices: `{', '.join(base_packages)}`")
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
            alternative_groups = [dict(item) for item in list(group.get("alternative_package_groups") or []) if isinstance(item, dict)]
            if alternative_groups:
                lines.append("- Alternative package lanes:")
                for alt_group in alternative_groups:
                    selected_filter = str(alt_group.get("selected_filter_id") or "").strip()
                    line = f"  - `{alt_group.get('title') or alt_group.get('id')}` ({alt_group.get('policy') or 'one_of'})"
                    if selected_filter:
                        line += f" — default filter: `{selected_filter}`"
                    lines.append(line)
                    for member in [dict(x) for x in list(alt_group.get("members") or []) if isinstance(x, dict)]:
                        effective = [str(x) for x in list(member.get("effective_packages") or []) if str(x)]
                        lane_filter = str(member.get("filter_id") or "").strip()
                        marker = "default" if member.get("selected_by_default") else "optional"
                        lines.append(f"    - `{member.get('id') or ''}` → `{', '.join(effective)}` ({marker}; script filter: `{lane_filter}`)")
            lines.append("")
        for note in [str(x) for x in list(toolchain_packages.get("notes") or []) if str(x)][:3]:
            lines.append(f"- {note}")
        lines.append("")

    if authority_policy:
        lines.append("## Authority-aware setup boundaries")
        lines.append("")
        lines.append(str(authority_policy.get("summary") or "Authority posture unavailable"))
        lines.append("")
        lines.append(f"- Authority mode: `{authority_policy.get('primary_mode') or 'xdg-local-userland-only'}`")
        for label, key in [("Session-userland surfaces", "session_userland_surface_ids"), ("Desktop-mediated surfaces", "desktop_mediated_surface_ids"), ("Adjacent privileged surfaces", "adjacent_privileged_surface_ids"), ("Launch-userland surfaces", "launch_userland_surface_ids"), ("Review-only surfaces", "review_surface_ids")]:
            values = [str(x) for x in list(authority_policy.get(key) or []) if str(x)]
            if values:
                lines.append(f"- {label}: " + ", ".join(f"`{value}`" for value in values[:8]))
        for item in [str(x) for x in list(authority_policy.get("guardrails") or []) if str(x)][:4]:
            lines.append(f"- Guardrail: {item}")
        lines.append("")

    if host_truth or portal_route_contract:
        lines.append("## Observed deployment truth")
        lines.append("")
        lines.append(f"- Host truth status: `{host_truth.get('status') or 'unknown'}`")
        lines.append(f"- Observed host requirements: {host_truth.get('requirement_count') or 0}")
        lines.append(f"- Blocked requirements: {host_truth.get('blocked_count') or 0}")
        lines.append(f"- Degraded requirements: {host_truth.get('degraded_count') or 0}")
        if portal_route_contract:
            lines.append(f"- Portal route status: `{portal_route_contract.get('status') or 'unknown'}`")
            lines.append(f"- Portal config status: `{portal_route_contract.get('config_status') or 'unknown'}`")
            lines.append(f"- Portal manifest status: `{portal_route_contract.get('manifest_status') or 'unknown'}`")
            installed_backends = [str(x) for x in list(portal_route_contract.get('installed_backends') or []) if str(x)]
            if installed_backends:
                lines.append(f"- Installed portal backends: `{', '.join(installed_backends[:8])}`")
            for item in [dict(x) for x in list(portal_route_contract.get('issues') or []) if isinstance(x, dict)][:4]:
                lines.append(f"- Portal issue: `{item.get('short_name') or item.get('interface') or 'portal'}` → `{item.get('status') or 'unknown'}` — {item.get('message') or item.get('note') or 'review current portal routing'}")
        blockers = [item for item in host_requirements if _observed_status_bucket(str(item.get('observed_status') or 'unknown')) in {'blocked', 'degraded'}]
        if blockers:
            lines.append("")
            lines.append("Observed blockers / caveats:")
            for item in blockers[:6]:
                lines.append(f"- `{item.get('id') or ''}` — `{item.get('observed_status') or 'unknown'}` — {_first_text(item, 'observed_note', 'why', 'title')}")
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
    host_truth = dict(plan.get("host_truth") or {})
    host_requirements = [dict(item) for item in list(plan.get("host_requirements") or []) if isinstance(item, dict)]
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
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
                lines.append(f"- Default packages: `{', '.join(packages)}`")
            alternative_groups = [dict(item) for item in list(group.get("alternative_package_groups") or []) if isinstance(item, dict)]
            if alternative_groups:
                lines.append(f"- Alternative lane groups: {len(alternative_groups)}")
                for alt_group in alternative_groups:
                    lines.append(f"  - `{alt_group.get('id') or ''}` ({alt_group.get('policy') or 'one_of'})")
                    for member in [dict(x) for x in list(alt_group.get('members') or []) if isinstance(x, dict)]:
                        effective = [str(x) for x in list(member.get('effective_packages') or []) if str(x)]
                        marker = "default" if member.get("selected_by_default") else "optional"
                        lines.append(f"    - `{member.get('id') or ''}` → `{', '.join(effective)}` ({marker})")
            lines.append("")
    if host_truth or portal_route_contract:
        lines.append("## Observed host truth")
        lines.append("")
        lines.append(f"- Overall host truth: `{host_truth.get('status') or 'unknown'}`")
        lines.append(f"- Observed requirements: {host_truth.get('requirement_count') or 0}")
        if portal_route_contract:
            lines.append(f"- Portal route status: `{portal_route_contract.get('status') or 'unknown'}`")
            lines.append(f"- Portal manifest status: `{portal_route_contract.get('manifest_status') or 'unknown'}`")
        blockers = [item for item in host_requirements if _observed_status_bucket(str(item.get('observed_status') or 'unknown')) in {'blocked', 'degraded'}]
        if blockers:
            lines.append("- Top blockers / caveats:")
            for item in blockers[:5]:
                lines.append(f"  - `{item.get('id') or ''}` → `{item.get('observed_status') or 'unknown'}`")
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

    def emit_case(case_id: str, title: str, packages: list[str], commands: dict[str, Any], *, note_lines: list[str] | None = None) -> None:
        lines.extend([
            f"if selected '{case_id}'; then",
            "  echo ''",
            f"  echo '== {title} ({case_id}) =='",
        ])
        if packages:
            lines.append(f"  printf 'Packages: %s\n' {json.dumps(', '.join(packages))}")
        for note in list(note_lines or []):
            lines.append(f"  printf '  - %s\n' {json.dumps(str(note))}")
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

    for group in package_groups:
        group_id = _group_filter_id(str(group.get("id") or "packages"))
        title = str(group.get("title") or group_id)
        packages = [str(x) for x in list(group.get("packages") or []) if str(x)]
        commands = dict(group.get("install_commands") or {})
        alternative_groups = [dict(item) for item in list(group.get("alternative_package_groups") or []) if isinstance(item, dict)]
        note_lines: list[str] = []
        if alternative_groups:
            filters: list[str] = []
            for alt_group in alternative_groups:
                for member in [dict(x) for x in list(alt_group.get("members") or []) if isinstance(x, dict)]:
                    filters.append(str(member.get("filter_id") or _lane_filter_id(group_id, str(member.get("id") or "lane"))))
            if filters:
                note_lines.append(f"Alternative lane filters: {', '.join(filters)}")
        emit_case(group_id, title, packages, commands, note_lines=note_lines)
        for alt_group in alternative_groups:
            for member in [dict(x) for x in list(alt_group.get("members") or []) if isinstance(x, dict)]:
                case_id = str(member.get("filter_id") or _lane_filter_id(group_id, str(member.get("id") or "lane")))
                member_id = case_id.rsplit("__", 1)[-1]
                member_title = f"{title} / {member.get('title') or member.get('id') or member_id}"
                effective_packages = [str(x) for x in list(member.get("effective_packages") or []) if str(x)]
                effective_commands = dict(member.get("effective_install_commands") or {})
                notes = [f"Alternative lane from {alt_group.get('title') or alt_group.get('id') or 'lane'}"]
                if member.get("selected_by_default"):
                    notes.append("This lane is selected by default in the parent bootstrap group.")
                emit_case(case_id, member_title, effective_packages, effective_commands, note_lines=notes)

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
    host_snapshot: dict[str, object] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_setup_pack_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
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

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.loader import load_project
from vhk.project.route_selection_pack import (
    _GROUP_META,
    _candidate_sort_key,
    _group_overall_status,
    _group_priority,
    _selection_group,
    _selection_note,
    _selection_score,
)
from vhk.project.strategy import summarize_project_strategy


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


def _default_target_profiles() -> list[dict[str, Any]]:
    return [
        {
            "id": "x11-desktop",
            "title": "Generic X11 desktop",
            "backend": "x11",
            "desktop_family": "x11",
            "summary": "Assume an X11-oriented desktop where WM/compositor-native bindings are the cleanest hotkey surface and portal shortcut plumbing is not central.",
            "route_bonus": {
                "native-trigger-route": 18,
                "portal-shortcuts-route": -18,
                "remapper-route": 4,
                "launcher-entrypoint": 6,
            },
            "requirement_status": {
                "portal-global-shortcuts": "blocked",
                "portal-backend-config": "blocked",
                "portal-remote-desktop": "blocked",
                "uinput-permissions": "planned",
                "remapper-lifecycle": "planned",
                "text-surface-service": "planned",
                "watcher-user-service": "planned",
                "ydotool-daemon": "planned",
            },
            "capability_matrix": {
                "global_hotkeys": {"status": "ok", "recommended": "wm-native-bindings", "mechanisms": ["wm-native-bindings"], "notes": []},
                "screen_capture": {"status": "ok", "recommended": "x11-tools", "mechanisms": ["x11-tools"], "notes": []},
                "text_injection": {"status": "ok", "recommended": "x11-tools", "mechanisms": ["x11-tools"], "notes": []},
                "pointer_injection": {"status": "ok", "recommended": "x11-tools", "mechanisms": ["x11-tools"], "notes": []},
                "input_capture": {"status": "limited", "recommended": None, "mechanisms": [], "notes": ["target comparison assumes X11-native binds over portal capture"]},
            },
            "assumptions": [
                "Desktop-native WM bindings are the primary trigger surface.",
                "Portal shortcut sessions are not treated as the reference hotkey route.",
                "Remapper/helper tiers remain optional backups, not the default first choice.",
            ],
        },
        {
            "id": "gnome-wayland",
            "title": "GNOME Wayland portal-first",
            "backend": "wayland",
            "desktop_family": "gnome",
            "summary": "Assume a portal-shaped Wayland desktop where session-bound shortcuts and consented desktop services are first-class, even though launcher fallbacks remain mandatory.",
            "route_bonus": {
                "portal-shortcuts-route": 20,
                "native-trigger-route": -4,
                "launcher-entrypoint": 6,
                "helper-input-route": -2,
            },
            "requirement_status": {
                "portal-global-shortcuts": "ready",
                "portal-backend-config": "ready",
                "portal-remote-desktop": "planned",
                "uinput-permissions": "planned",
                "remapper-lifecycle": "planned",
                "text-surface-service": "planned",
                "watcher-user-service": "planned",
                "ydotool-daemon": "planned",
            },
            "capability_matrix": {
                "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": []},
                "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": []},
                "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["interactive permission path expected"]},
                "pointer_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(pointer)"], "notes": ["consent-driven route"]},
                "input_capture": {"status": "limited", "recommended": "portal:InputCapture", "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based activation"]},
            },
            "assumptions": [
                "Portal shortcut sessions are viable enough to model as the design-preferred trigger route.",
                "Launcher fallback remains mandatory because portal binding is a session/configure flow.",
                "Remapper/helper routes stay available but are not the first shipping choice in this profile.",
            ],
        },
        {
            "id": "kde-wayland",
            "title": "KDE Wayland portal-friendly",
            "backend": "wayland",
            "desktop_family": "kde",
            "summary": "Assume a Wayland desktop with strong desktop-service and portal integration, while still keeping WM-native and launcher routes visible.",
            "route_bonus": {
                "portal-shortcuts-route": 16,
                "native-trigger-route": 4,
                "launcher-entrypoint": 6,
            },
            "requirement_status": {
                "portal-global-shortcuts": "ready",
                "portal-backend-config": "ready",
                "portal-remote-desktop": "planned",
                "uinput-permissions": "planned",
                "remapper-lifecycle": "planned",
                "text-surface-service": "planned",
                "watcher-user-service": "planned",
                "ydotool-daemon": "planned",
            },
            "capability_matrix": {
                "global_hotkeys": {"status": "ok", "recommended": "portal:GlobalShortcuts", "mechanisms": ["portal:GlobalShortcuts"], "notes": []},
                "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot"], "notes": []},
                "text_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(keyboard)"], "notes": ["session consent may still be required"]},
                "pointer_injection": {"status": "limited", "recommended": None, "mechanisms": ["portal:RemoteDesktop(pointer)"], "notes": ["session consent may still be required"]},
                "input_capture": {"status": "limited", "recommended": "portal:InputCapture", "mechanisms": ["portal:InputCapture"], "notes": ["trigger-based activation"]},
            },
            "assumptions": [
                "Portal services are likely part of the reference Wayland route set.",
                "Desktop-native bind surfaces may still coexist with portal sessions.",
                "Helper/remapper routes remain backups when consented portal flows are not enough.",
            ],
        },
        {
            "id": "wlroots-wayland",
            "title": "wlroots-style Wayland remapper-first",
            "backend": "wayland",
            "desktop_family": "wlroots",
            "summary": "Assume a compositor family where low-latency remapper/helper routes are often the practical trigger edge and portal shortcuts are not the design center.",
            "route_bonus": {
                "remapper-route": 18,
                "helper-input-route": 10,
                "portal-shortcuts-route": -12,
                "native-trigger-route": 4,
                "launcher-entrypoint": 6,
            },
            "requirement_status": {
                "portal-global-shortcuts": "blocked",
                "portal-backend-config": "unknown",
                "portal-remote-desktop": "planned",
                "uinput-permissions": "ready",
                "remapper-lifecycle": "ready",
                "text-surface-service": "planned",
                "watcher-user-service": "planned",
                "ydotool-daemon": "ready",
            },
            "capability_matrix": {
                "global_hotkeys": {"status": "limited", "recommended": None, "mechanisms": ["remapper"], "notes": ["compare against remapper or compositor-native binds"]},
                "screen_capture": {"status": "ok", "recommended": "portal:Screenshot", "mechanisms": ["portal:Screenshot", "wlroots-native"], "notes": []},
                "text_injection": {"status": "limited", "recommended": "ydotool", "mechanisms": ["ydotool"], "notes": ["uinput/helper route assumed"]},
                "pointer_injection": {"status": "ok", "recommended": "ydotool", "mechanisms": ["ydotool"], "notes": ["uinput/helper route assumed"]},
                "input_capture": {"status": "limited", "recommended": None, "mechanisms": ["portal:InputCapture"], "notes": ["compositor/portal-specific"]},
            },
            "assumptions": [
                "Remapper and helper-daemon layers are treated as realistic primary edges for hotkeys and injected input.",
                "Portal shortcut sessions stay visible but are not assumed to be the best universal trigger route.",
                "Launcher fallback remains the cross-profile escape hatch.",
            ],
        },
    ]


def _target_status(route: Mapping[str, Any], profile: Mapping[str, Any]) -> tuple[str, str | None, dict[str, list[str]]]:
    req_ids = [str(x) for x in list(route.get("depends_on_requirements") or []) if str(x)]
    policies = dict(profile.get("requirement_status") or {})
    detail = {
        "ready_requirements": [],
        "planned_requirements": [],
        "blocked_requirements": [],
        "unknown_requirements": [],
    }
    if not req_ids:
        kind = str(route.get("activation_kind") or "")
        if kind == "launcher":
            return "ready", "This fallback route exists on every modeled target profile.", detail
        return "planned", "This route depends mainly on placing config or registering services on the target desktop.", detail

    for req_id in req_ids:
        status = str(policies.get(req_id) or "").strip().lower()
        if not status:
            if req_id.startswith("portal-"):
                status = "planned" if str(profile.get("backend") or "") == "wayland" else "blocked"
            elif req_id in {"uinput-permissions", "remapper-lifecycle", "text-surface-service", "watcher-user-service", "ydotool-daemon"}:
                status = "planned"
            else:
                status = "unknown"
        bucket = f"{status}_requirements"
        if bucket in detail:
            detail[bucket].append(req_id)
        else:
            detail["unknown_requirements"].append(req_id)

    if detail["blocked_requirements"]:
        return "blocked", "One or more route requirements are intentionally out-of-profile for this target desktop.", detail
    if detail["unknown_requirements"]:
        return "unknown", "This target profile does not model every requirement for the route yet.", detail
    if detail["planned_requirements"]:
        return "planned", "This route looks viable for the target profile but still assumes install/config work.", detail
    return "ready", "This route fits the target profile without extra modeled blockers.", detail


def _profile_adjusted_score(route: Mapping[str, Any], profile: Mapping[str, Any]) -> tuple[int, list[str]]:
    backend = str(profile.get("backend") or "")
    score, reasons = _selection_score(route, backend)
    bonus_map = dict(profile.get("route_bonus") or {})
    route_id = str(route.get("id") or "")
    bonus = int(bonus_map.get(route_id) or 0)
    if bonus:
        score += bonus
        reasons.append(f"target-profile bonus={bonus}")
    return score, reasons


def _route_inventory(strategy: Mapping[str, Any], profile: Mapping[str, Any]) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for raw in list(strategy.get("activation_routes") or []):
        if not isinstance(raw, Mapping):
            continue
        route = dict(raw)
        status, note, detail = _target_status(route, profile)
        route["route_status"] = status
        score, reasons = _profile_adjusted_score(route, profile)
        route["route_note"] = note
        route["route_detail"] = detail
        route["selection_group"] = _selection_group(route)
        route["selection_score"] = score
        route["selection_reasons"] = reasons
        routes.append(route)
    return routes


def _build_target_profile_selection(
    project_dir: Path,
    *,
    project,
    profile: Mapping[str, Any],
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    target_project = copy.deepcopy(project)
    if getattr(target_project, "settings", None) is not None:
        target_project.settings.desktop_backend = str(profile.get("backend") or getattr(target_project.settings, "desktop_backend", "auto") or "auto")
    strategy = summarize_project_strategy(
        target_project,
        capability_usage=capability_usage,
        capability_matrix=dict(profile.get("capability_matrix") or {}),
        capability_issues=[],
    )
    routes = _route_inventory(strategy, profile)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for route in routes:
        grouped.setdefault(str(route.get("selection_group") or "auxiliary"), []).append(route)

    selected_groups: list[dict[str, Any]] = []
    reference_routes: list[dict[str, Any]] = []
    primary_statuses: list[str] = []

    for group, items in sorted(grouped.items(), key=lambda pair: (_group_priority(pair[0]), pair[0])):
        candidates = sorted(items, key=_candidate_sort_key)
        if not candidates:
            continue
        primary = candidates[0]
        primary_status = str(primary.get("route_status") or "unknown")
        primary_statuses.append(primary_status)
        fallbacks = [
            {
                "route_id": str(item.get("id") or ""),
                "title": str(item.get("title") or item.get("id") or ""),
                "route_status": str(item.get("route_status") or "unknown"),
                "selection_score": int(item.get("selection_score") or 0),
            }
            for item in candidates[1:]
        ]
        meta = dict(_GROUP_META.get(group) or {})
        note = _selection_note(group, primary, fallbacks)
        selected_groups.append(
            {
                "selection_group": group,
                "group_title": meta.get("title") or group,
                "purpose": meta.get("purpose") or "",
                "primary_route_id": str(primary.get("id") or ""),
                "primary_route_title": str(primary.get("title") or primary.get("id") or ""),
                "primary_route_status": primary_status,
                "primary_selection_score": int(primary.get("selection_score") or 0),
                "selection_note": note,
                "fallback_route_ids": [str(item.get("route_id") or "") for item in fallbacks if str(item.get("route_id") or "")],
                "candidates": [
                    {
                        "route_id": str(item.get("id") or ""),
                        "title": str(item.get("title") or item.get("id") or ""),
                        "route_status": str(item.get("route_status") or "unknown"),
                        "selection_score": int(item.get("selection_score") or 0),
                        "activation_kind": str(item.get("activation_kind") or ""),
                        "fit": str(item.get("fit") or ""),
                    }
                    for item in candidates
                ],
            }
        )
        reference_routes.append(
            {
                "selection_group": group,
                "route_id": str(primary.get("id") or ""),
                "title": str(primary.get("title") or primary.get("id") or ""),
                "route_status": primary_status,
                "selection_score": int(primary.get("selection_score") or 0),
            }
        )

    summary = {
        "overall_status": _group_overall_status(primary_statuses),
        "selection_group_count": len(selected_groups),
        "ready_primary_groups": [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "ready"],
        "planned_primary_groups": [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "planned"],
        "blocked_primary_groups": [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "blocked"],
        "selected_route_ids": [str(item.get("route_id") or "") for item in reference_routes if str(item.get("route_id") or "")],
    }

    return {
        "profile": {
            "id": str(profile.get("id") or ""),
            "title": str(profile.get("title") or profile.get("id") or ""),
            "backend": str(profile.get("backend") or ""),
            "desktop_family": str(profile.get("desktop_family") or ""),
            "summary": str(profile.get("summary") or ""),
            "assumptions": [str(x) for x in list(profile.get("assumptions") or []) if str(x)],
        },
        "project": dict(strategy.get("project") or {}),
        "overview": dict(strategy.get("overview") or {}),
        "selection_summary": summary,
        "selected_groups": selected_groups,
        "reference_routes": reference_routes,
        "activation_routes": routes,
        "stack_profiles": list(strategy.get("stack_profiles") or strategy.get("deployment_profiles") or []),
        "runtime_seams": list(strategy.get("runtime_seams") or []),
        "host_requirements": list(strategy.get("host_requirements") or []),
        "capability_matrix": dict(profile.get("capability_matrix") or {}),
    }


def build_target_route_plan(
    project_dir: Path,
    *,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    profiles = _default_target_profiles()
    if target_profiles:
        wanted = {str(item).strip() for item in target_profiles if str(item).strip()}
        profiles = [dict(item) for item in profiles if str(item.get("id") or "") in wanted]
        if not profiles:
            raise ValueError("No matching target profiles selected.")

    profile_plans = [
        _build_target_profile_selection(
            project_dir,
            project=project,
            profile=profile,
            capability_usage=capability_usage,
        )
        for profile in profiles
    ]

    group_matrix: list[dict[str, Any]] = []
    group_ids = _dedupe_keep_order(
        [
            str(group.get("selection_group") or "")
            for plan in profile_plans
            for group in list(plan.get("selected_groups") or [])
            if isinstance(group, Mapping) and str(group.get("selection_group") or "")
        ]
    )
    divergent_groups: list[str] = []
    stable_groups: list[str] = []
    for group_id in group_ids:
        per_profile: list[dict[str, Any]] = []
        chosen_route_ids: list[str] = []
        for plan in profile_plans:
            profile = dict(plan.get("profile") or {})
            match = next((dict(item) for item in list(plan.get("selected_groups") or []) if isinstance(item, Mapping) and str(item.get("selection_group") or "") == group_id), {})
            route_id = str(match.get("primary_route_id") or "")
            if route_id:
                chosen_route_ids.append(route_id)
            per_profile.append(
                {
                    "profile_id": str(profile.get("id") or ""),
                    "profile_title": str(profile.get("title") or profile.get("id") or ""),
                    "route_id": route_id,
                    "route_status": str(match.get("primary_route_status") or "unknown"),
                    "selection_note": str(match.get("selection_note") or ""),
                }
            )
        unique_routes = _dedupe_keep_order(chosen_route_ids)
        if len(unique_routes) <= 1:
            stable_groups.append(group_id)
        else:
            divergent_groups.append(group_id)
        group_matrix.append(
            {
                "selection_group": group_id,
                "group_title": str((_GROUP_META.get(group_id) or {}).get("title") or group_id),
                "unique_route_ids": unique_routes,
                "divergent": len(unique_routes) > 1,
                "per_profile": per_profile,
            }
        )

    review_commands = _dedupe_keep_order(
        [
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-activation-pack {project_dir.as_posix()} --force --quiet --no-activation-check",
            f"vhk gen-route-selection-pack {project_dir.as_posix()} --force --quiet --no-selection-check",
            f"vhk gen-target-route-pack {project_dir.as_posix()} --force --quiet",
        ]
    )

    return {
        "source_contract": "target_route_pack",
        "project": {
            "name": str(getattr(project, "name", None) or project_dir.name),
            "desktop_backend": str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "unknown"),
            "root_dir": project_dir.as_posix(),
        },
        "target_summary": {
            "profile_count": len(profile_plans),
            "divergent_groups": divergent_groups,
            "stable_groups": stable_groups,
        },
        "target_profiles": profile_plans,
        "group_matrix": group_matrix,
        "review_commands": review_commands,
    }


def render_target_route_matrix(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("target_summary") or {})
    profiles = _trim_items(plan.get("target_profiles"), limit=8)
    group_matrix = _trim_items(plan.get("group_matrix"), limit=12)

    lines: list[str] = []
    lines.append(f"# VHK target route matrix for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-target-route-pack`. This pack compares route-selection decisions across hypothetical Linux target desktops so release planning does not depend only on the current host.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Declared project backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Target profiles compared: {int(summary.get('profile_count') or 0)}")
    lines.append(f"- Divergent selection groups: {len(list(summary.get('divergent_groups') or []))}")
    lines.append(f"- Stable selection groups: {len(list(summary.get('stable_groups') or []))}")
    lines.append("")

    if profiles:
        lines.append("## Target profiles")
        lines.append("")
        for item in profiles:
            profile = dict(item.get("profile") or {})
            sel = dict(item.get("selection_summary") or {})
            lines.append(f"### {profile.get('title') or profile.get('id')}")
            lines.append("")
            lines.append(f"- Profile id: `{profile.get('id') or ''}`")
            lines.append(f"- Backend: `{profile.get('backend') or ''}`")
            lines.append(f"- Overall status: `{sel.get('overall_status') or 'unknown'}`")
            lines.append(f"- Summary: {profile.get('summary') or 'n/a'}")
            refs = [dict(x) for x in list(item.get("reference_routes") or []) if isinstance(x, Mapping)]
            if refs:
                lines.append("- Reference routes:")
                for ref in refs:
                    lines.append(f"  - `{ref.get('selection_group') or ''}` → `{ref.get('route_id') or ''}` (`{ref.get('route_status') or 'unknown'}`)")
            assumptions = [str(x) for x in list(profile.get("assumptions") or []) if str(x)]
            if assumptions:
                lines.append("- Assumptions:")
                for assumption in assumptions:
                    lines.append(f"  - {assumption}")
            lines.append("")

    if group_matrix:
        lines.append("## Cross-profile route comparison")
        lines.append("")
        for row in group_matrix:
            lines.append(f"### {row.get('group_title') or row.get('selection_group')}")
            lines.append("")
            lines.append(f"- Selection group: `{row.get('selection_group') or ''}`")
            lines.append(f"- Divergent: `{'yes' if row.get('divergent') else 'no'}`")
            unique_route_ids = [str(x) for x in list(row.get('unique_route_ids') or []) if str(x)]
            if unique_route_ids:
                lines.append(f"- Candidate reference routes across targets: {', '.join(f'`{rid}`' for rid in unique_route_ids)}")
            lines.append("")
            for item in list(row.get("per_profile") or []):
                lines.append(
                    f"- `{item.get('profile_id') or ''}` → `{item.get('route_id') or ''}` (`{item.get('route_status') or 'unknown'}`)"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_target_route_fixups(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    profiles = [dict(item) for item in list(plan.get("target_profiles") or []) if isinstance(item, dict)]
    group_matrix = [dict(item) for item in list(plan.get("group_matrix") or []) if isinstance(item, dict)]

    lines: list[str] = []
    lines.append(f"# VHK target route fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-target-route-pack`. Use this when the project needs an explicit release story for more than one Linux target profile.")
    lines.append("")

    divergent = [item for item in group_matrix if bool(item.get("divergent"))]
    if divergent:
        lines.append("## Divergent groups that need explicit release decisions")
        lines.append("")
        for item in divergent:
            lines.append(f"### {item.get('group_title') or item.get('selection_group')}")
            lines.append("")
            for row in list(item.get("per_profile") or []):
                lines.append(f"- `{row.get('profile_id') or ''}` chooses `{row.get('route_id') or ''}` (`{row.get('route_status') or 'unknown'}`)")
            lines.append("")
    else:
        lines.append("## Divergent groups that need explicit release decisions")
        lines.append("")
        lines.append("None. All modeled target profiles currently agree on the same reference routes.")
        lines.append("")

    blocked_profiles = [
        (dict(item.get("profile") or {}), dict(item.get("selection_summary") or {}))
        for item in profiles
        if "blocked" in list((item.get("selection_summary") or {}).get("blocked_primary_groups") or [])
    ]
    lines.append("## Target profiles with blocked primary routes")
    lines.append("")
    if blocked_profiles:
        for profile, summary in blocked_profiles:
            lines.append(
                f"- `{profile.get('id') or ''}` has blocked groups: {', '.join(f'`{x}`' for x in list(summary.get('blocked_primary_groups') or []))}"
            )
        lines.append("")
    else:
        lines.append("None. No modeled target profile currently blocks its chosen primary routes.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_target_route_refresh_script(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST="${1:-./build/target-route-review}"')
    lines.append('mkdir -p "$DEST"')
    lines.append('echo "Collecting VHK target-route evidence into $DEST"')
    lines.append("")
    lines.append('printf "+ %s\\n" "vhk plan-project . --json > $DEST/plan-project.json"')
    lines.append('sh -lc "vhk plan-project . --json > \"$DEST\"/plan-project.json" || true')
    lines.append('printf "+ %s\\n" "vhk gen-activation-pack . --force --quiet --no-activation-check"')
    lines.append('sh -lc "vhk gen-activation-pack . --force --quiet --no-activation-check" || true')
    lines.append('printf "+ %s\\n" "vhk gen-route-selection-pack . --force --quiet --no-selection-check"')
    lines.append('sh -lc "vhk gen-route-selection-pack . --force --quiet --no-selection-check" || true')
    lines.append('printf "+ %s\\n" "vhk gen-target-route-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-target-route-pack . --force --quiet" || true')
    lines.append('echo "Target route comparison refresh complete."')
    return "\n".join(lines).rstrip() + "\n"


def write_target_route_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    matrix_doc: bool = True,
    fixups_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_target_route_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )

    written: dict[str, Path] = {}
    if matrix_doc:
        path = out_dir / "VHK_TARGET_ROUTE_MATRIX.md"
        _write_if_allowed(path, render_target_route_matrix(plan), force=force)
        written["matrix_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_TARGET_ROUTE_FIXUPS.md"
        _write_if_allowed(path, render_target_route_fixups(plan), force=force)
        written["fixups_doc"] = path
    if plan_json:
        path = out_dir / "VHK_TARGET_ROUTE_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_compare_target_routes.sh"
        _write_if_allowed(path, render_target_route_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path
    return written

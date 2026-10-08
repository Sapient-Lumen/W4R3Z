from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.activation_pack import build_activation_pack_plan


_STATUS_WEIGHT = {
    "ready": 90,
    "planned": 72,
    "degraded": 48,
    "unknown": 34,
    "blocked": 0,
}

_FIT_WEIGHT = {
    "strong": 14,
    "good": 10,
    "conditional": 4,
}

_STATUS_ORDER = {"blocked": 0, "degraded": 1, "unknown": 2, "planned": 3, "ready": 4}

_GROUP_META = {
    "universal-entry": {
        "title": "Universal entry route",
        "purpose": "An always-available wake-up path an operator can trust even when hotter trigger surfaces are desktop-specific or degraded.",
        "essential": True,
    },
    "trigger-entry": {
        "title": "Trigger ownership route",
        "purpose": "The reference route for hotkeys and desktop-triggered launches.",
        "essential": False,
    },
    "text-entry": {
        "title": "Text surface route",
        "purpose": "The reference route for service-managed text expansion and snippet entry.",
        "essential": False,
    },
    "event-plane": {
        "title": "Event plane route",
        "purpose": "The reference route for watcher/bus-driven automation that should survive shell exits.",
        "essential": False,
    },
    "input-edge": {
        "title": "Input edge route",
        "purpose": "The reference route for injected input, helper daemons, and input-edge adapters.",
        "essential": False,
    },
    "auxiliary": {
        "title": "Auxiliary route",
        "purpose": "A non-core activation route that still belongs in deployment review.",
        "essential": False,
    },
}


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


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


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 10) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _selection_group(route: Mapping[str, Any]) -> str:
    route_id = str(route.get("id") or "")
    if route_id == "launcher-entrypoint":
        return "universal-entry"
    if route_id in {"native-trigger-route", "portal-shortcuts-route", "remapper-route"}:
        return "trigger-entry"
    if route_id == "text-surface-route":
        return "text-entry"
    if route_id == "watcher-service-route":
        return "event-plane"
    if route_id == "helper-input-route":
        return "input-edge"
    return "auxiliary"


def _route_preference(route: Mapping[str, Any], backend: str) -> tuple[int, list[str]]:
    route_id = str(route.get("id") or "")
    score = 0
    reasons: list[str] = []

    if route_id == "launcher-entrypoint":
        score += 28
        reasons.append("universal fallback route")
    elif route_id == "native-trigger-route":
        score += 24
        reasons.append("desktop-native binding ownership")
    elif route_id == "text-surface-route":
        score += 22
        reasons.append("service-shaped text surface")
    elif route_id == "watcher-service-route":
        score += 18
        reasons.append("restartable watcher/event plane")
    elif route_id == "helper-input-route":
        score += 18
        reasons.append("narrow helper/input seam")
    elif route_id == "portal-shortcuts-route":
        score += 16
        reasons.append("session-bound portal shortcuts")
    elif route_id == "remapper-route":
        score += 12
        reasons.append("low-latency remapper tier")
    else:
        score += 8
        reasons.append("auxiliary activation route")

    if backend == "wayland" and route_id == "portal-shortcuts-route":
        score += 6
        reasons.append("Wayland-friendly shortcut session option")
    if backend in {"x11", "wayland"} and route_id == "native-trigger-route":
        score += 6
        reasons.append("desktop backend explicitly declared")
    if backend == "x11" and route_id == "portal-shortcuts-route":
        score -= 8
        reasons.append("portal shortcut route less central on X11")
    if backend == "wayland" and route_id == "helper-input-route":
        score += 4
        reasons.append("Wayland input edges usually need explicit helper ownership")
    if backend == "wayland" and route_id == "remapper-route":
        score += 2
        reasons.append("Wayland low-latency remapper route can be a practical backup")

    return score, reasons


def _selection_score(route: Mapping[str, Any], backend: str) -> tuple[int, list[str]]:
    status = str(route.get("route_status") or "unknown")
    fit = str(route.get("fit") or "good")
    score = _STATUS_WEIGHT.get(status, 30) + _FIT_WEIGHT.get(fit, 8)
    reasons = [f"route status={status}", f"fit={fit}"]
    pref_score, pref_reasons = _route_preference(route, backend)
    score += pref_score
    reasons.extend(pref_reasons)
    if not list(route.get("depends_on_requirements") or []):
        score += 4
        reasons.append("few host-side dependencies")
    return score, reasons


def _candidate_sort_key(item: Mapping[str, Any]) -> tuple[int, int, int, str]:
    blocked = 1 if str(item.get("route_status") or "") == "blocked" else 0
    status = _STATUS_ORDER.get(str(item.get("route_status") or "unknown"), 2)
    score = int(item.get("selection_score") or 0)
    return (blocked, -score, -status, str(item.get("title") or ""))


def _selection_note(group: str, primary: Mapping[str, Any], fallbacks: list[dict[str, Any]]) -> str:
    primary_status = str(primary.get("route_status") or "unknown")
    primary_title = str(primary.get("title") or primary.get("id") or "route")
    if group == "universal-entry":
        return f"Use {primary_title} as the non-negotiable operator fallback route."

    ready_fallbacks = [item for item in fallbacks if str(item.get("route_status") or "") == "ready"]
    if primary_status == "ready":
        if ready_fallbacks:
            return f"{primary_title} is the reference route; keep the ready fallback lanes documented rather than hiding them."
        return f"{primary_title} is the cleanest current reference route for this lane."
    if primary_status == "planned":
        if ready_fallbacks:
            best = ready_fallbacks[0]
            return (
                f"{primary_title} remains the design-preferred route, but {best.get('title') or best.get('id')} is more immediately live on this host. "
                "Ship both roles explicitly."
            )
        return f"{primary_title} is the design-preferred route, but it still needs operator placement/config activation."
    if primary_status in {"degraded", "unknown"}:
        if ready_fallbacks:
            best = ready_fallbacks[0]
            return (
                f"{primary_title} is currently weaker than {best.get('title') or best.get('id')}; consider promoting the healthier fallback until the preferred route is repaired."
            )
        return f"{primary_title} still needs more proof before it can be treated as the shipping reference route."
    return f"{primary_title} is currently blocked; a fallback route must carry this lane until the contract is fixed."


def _group_priority(group: str) -> int:
    order = {
        "universal-entry": 0,
        "trigger-entry": 1,
        "text-entry": 2,
        "event-plane": 3,
        "input-edge": 4,
        "auxiliary": 5,
    }
    return order.get(group, 9)


def _group_overall_status(primary_statuses: list[str]) -> str:
    if any(status == "blocked" for status in primary_statuses):
        return "blocked"
    if any(status == "degraded" for status in primary_statuses):
        return "degraded"
    if any(status == "unknown" for status in primary_statuses):
        return "unknown"
    if any(status == "planned" for status in primary_statuses):
        return "planned"
    if primary_statuses and all(status == "ready" for status in primary_statuses):
        return "ready"
    return "unknown"


def build_route_selection_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    activation_plan = build_activation_pack_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )

    project = dict(activation_plan.get("project") or {})
    backend = str(project.get("desktop_backend") or "").strip().lower()
    routes = [dict(item) for item in list(activation_plan.get("activation_routes") or []) if isinstance(item, dict)]

    grouped: dict[str, list[dict[str, Any]]] = {}
    for route in routes:
        group = _selection_group(route)
        score, reasons = _selection_score(route, backend)
        enriched = dict(route)
        enriched["selection_group"] = group
        enriched["selection_score"] = score
        enriched["selection_reasons"] = reasons
        grouped.setdefault(group, []).append(enriched)

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
        blocked = [item for item in fallbacks if str(item.get("route_status") or "") == "blocked"]
        meta = dict(_GROUP_META.get(group) or _GROUP_META["auxiliary"])
        note = _selection_note(group, primary, fallbacks)
        group_row = {
            "selection_group": group,
            "group_title": meta.get("title") or group,
            "purpose": meta.get("purpose") or "",
            "essential": bool(meta.get("essential", False)),
            "primary_route_id": str(primary.get("id") or ""),
            "primary_route_title": str(primary.get("title") or primary.get("id") or ""),
            "primary_route_status": primary_status,
            "primary_selection_score": int(primary.get("selection_score") or 0),
            "selection_note": note,
            "fallback_route_ids": [str(item.get("route_id") or "") for item in fallbacks if str(item.get("route_id") or "")],
            "blocked_route_ids": [str(item.get("route_id") or "") for item in blocked if str(item.get("route_id") or "")],
            "candidate_count": len(candidates),
            "candidates": [
                {
                    "route_id": str(item.get("id") or ""),
                    "title": str(item.get("title") or item.get("id") or ""),
                    "route_status": str(item.get("route_status") or "unknown"),
                    "selection_score": int(item.get("selection_score") or 0),
                    "activation_kind": str(item.get("activation_kind") or ""),
                    "fit": str(item.get("fit") or ""),
                    "selection_reasons": list(item.get("selection_reasons") or []),
                }
                for item in candidates
            ],
        }
        selected_groups.append(group_row)
        reference_routes.append(
            {
                "selection_group": group,
                "route_id": str(primary.get("id") or ""),
                "title": str(primary.get("title") or primary.get("id") or ""),
                "route_status": primary_status,
                "selection_score": int(primary.get("selection_score") or 0),
                "selection_note": note,
            }
        )

    overall = _group_overall_status(primary_statuses)
    blocked_primary = [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "blocked"]
    degraded_primary = [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "degraded"]
    unknown_primary = [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "unknown"]
    planned_primary = [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "planned"]
    ready_primary = [str(item.get("selection_group") or "") for item in selected_groups if str(item.get("primary_route_status") or "") == "ready"]

    promotion_candidates = [
        {
            "selection_group": str(item.get("selection_group") or ""),
            "primary_route_id": str(item.get("primary_route_id") or ""),
            "primary_route_status": str(item.get("primary_route_status") or "unknown"),
            "fallback_route_id": str(candidate.get("route_id") or ""),
            "fallback_route_status": str(candidate.get("route_status") or "unknown"),
            "fallback_title": str(candidate.get("title") or candidate.get("route_id") or ""),
        }
        for item in selected_groups
        for candidate in list(item.get("candidates") or [])[1:]
        if str(item.get("primary_route_status") or "") in {"planned", "degraded", "unknown", "blocked"}
        and str(candidate.get("route_status") or "") == "ready"
    ]

    review_commands = _dedupe_keep_order(
        [
            "vhk doctor --json",
            f"vhk validate {project_dir.as_posix()} --json",
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-host-contract-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-readiness-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-activation-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-route-selection-pack {project_dir.as_posix()} --force --quiet",
            *[
                str(cmd)
                for item in routes
                for cmd in list(item.get("verification_commands") or [])
                if str(cmd)
            ],
        ]
    )

    return {
        "source_contract": "route_selection_pack",
        "project": project,
        "overview": dict(activation_plan.get("overview") or {}),
        "selection_summary": {
            "overall_status": overall,
            "selection_group_count": len(selected_groups),
            "selected_route_ids": [str(item.get("route_id") or "") for item in reference_routes if str(item.get("route_id") or "")],
            "blocked_primary_groups": blocked_primary,
            "degraded_primary_groups": degraded_primary,
            "unknown_primary_groups": unknown_primary,
            "planned_primary_groups": planned_primary,
            "ready_primary_groups": ready_primary,
            "promotion_candidate_count": len(promotion_candidates),
        },
        "selected_groups": selected_groups,
        "reference_routes": reference_routes,
        "promotion_candidates": promotion_candidates,
        "activation_summary": dict(activation_plan.get("activation_summary") or {}),
        "host_contract_summary": dict(activation_plan.get("host_contract_summary") or {}),
        "readiness_summary": dict(activation_plan.get("readiness_summary") or {}),
        "activation_plan": activation_plan,
        "review_commands": review_commands,
        "session_capabilities": dict(capability_matrix or {}),
        "session_issues": [dict(item) for item in list(capability_issues or []) if isinstance(item, dict)],
        "host_snapshot": dict(host_snapshot or {}),
    }


def render_route_selection_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("selection_summary") or {})
    selected_groups = _trim_items(plan.get("selected_groups"), limit=10)
    reference_routes = _trim_items(plan.get("reference_routes"), limit=10)

    lines: list[str] = []
    lines.append(f"# VHK route selection for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-route-selection-pack`. This pack chooses a reference route for each relevant Linux activation lane, keeps fallback routes visible, and turns route selection into an explicit deployment decision instead of support folklore.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall selection status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Reference route groups: {int(summary.get('selection_group_count') or 0)}")
    lines.append(f"- Ready primary groups: {len(list(summary.get('ready_primary_groups') or []))}")
    lines.append(f"- Planned primary groups: {len(list(summary.get('planned_primary_groups') or []))}")
    lines.append(f"- Promotion candidates: {int(summary.get('promotion_candidate_count') or 0)}")
    lines.append("")

    if reference_routes:
        lines.append("## Reference route set")
        lines.append("")
        for item in reference_routes:
            lines.append(f"- `{item.get('selection_group') or ''}` → `{item.get('route_id') or ''}` (`{item.get('route_status') or 'unknown'}`)")
        lines.append("")

    if selected_groups:
        lines.append("## Selection groups")
        lines.append("")
        for item in selected_groups:
            lines.append(f"### {item.get('group_title') or item.get('selection_group')}")
            lines.append("")
            lines.append(f"- Selection group: `{item.get('selection_group') or ''}`")
            lines.append(f"- Purpose: {item.get('purpose') or 'n/a'}")
            lines.append(f"- Primary route: `{item.get('primary_route_id') or ''}`")
            lines.append(f"- Primary status: `{item.get('primary_route_status') or 'unknown'}`")
            lines.append(f"- Primary score: {int(item.get('primary_selection_score') or 0)}")
            lines.append(f"- Review note: {item.get('selection_note') or 'n/a'}")
            fallback_ids = [str(x) for x in list(item.get('fallback_route_ids') or []) if str(x)]
            if fallback_ids:
                lines.append(f"- Fallback routes: {', '.join(f'`{route_id}`' for route_id in fallback_ids)}")
            lines.append("")
            candidates = _trim_items(item.get("candidates"), limit=6)
            if candidates:
                lines.append("Candidate ranking:")
                lines.append("")
                for candidate in candidates:
                    lines.append(
                        f"- `{candidate.get('route_id') or ''}` → status `{candidate.get('route_status') or 'unknown'}`, score {int(candidate.get('selection_score') or 0)}, kind `{candidate.get('activation_kind') or ''}`"
                    )
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_route_fixups(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    selected_groups = [dict(item) for item in list(plan.get("selected_groups") or []) if isinstance(item, dict)]
    promotion_candidates = [dict(item) for item in list(plan.get("promotion_candidates") or []) if isinstance(item, dict)]

    lines: list[str] = []
    lines.append(f"# VHK route selection fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-route-selection-pack`. Use this when activation routes exist but you still need to decide which one is the shipping reference route and which ones should stay fallback-only.")
    lines.append("")

    needs_work = [
        item for item in selected_groups
        if str(item.get("primary_route_status") or "") in {"blocked", "degraded", "unknown", "planned"}
    ]
    if needs_work:
        lines.append("## Primary routes that still need work")
        lines.append("")
        for item in needs_work:
            lines.append(f"### {item.get('group_title') or item.get('selection_group')}")
            lines.append("")
            lines.append(f"- Primary route: `{item.get('primary_route_id') or ''}`")
            lines.append(f"- Status: `{item.get('primary_route_status') or 'unknown'}`")
            lines.append(f"- Note: {item.get('selection_note') or 'n/a'}")
            lines.append("")
    else:
        lines.append("## Primary routes that still need work")
        lines.append("")
        lines.append("None. The currently selected primary routes all look ready.")
        lines.append("")

    if promotion_candidates:
        lines.append("## Ready fallback routes worth promoting")
        lines.append("")
        for item in promotion_candidates:
            lines.append(
                f"- `{item.get('selection_group') or ''}`: `{item.get('fallback_route_id') or ''}` is ready while primary `{item.get('primary_route_id') or ''}` is `{item.get('primary_route_status') or 'unknown'}`"
            )
        lines.append("")
    else:
        lines.append("## Ready fallback routes worth promoting")
        lines.append("")
        lines.append("None. No healthier ready fallback currently beats the selected primary routes.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_route_refresh_script(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST="${1:-./build/route-selection-review}"')
    lines.append('mkdir -p "$DEST"')
    lines.append('echo "Collecting VHK route-selection evidence into $DEST"')
    lines.append("")
    lines.append('printf "+ %s\\n" "vhk doctor --json > $DEST/doctor.json"')
    lines.append('sh -lc "vhk doctor --json > \"$DEST\"/doctor.json" || true')
    lines.append('printf "+ %s\\n" "vhk validate . --json > $DEST/validate.json"')
    lines.append('sh -lc "vhk validate . --json > \"$DEST\"/validate.json" || true')
    lines.append('printf "+ %s\\n" "vhk plan-project . --json > $DEST/plan-project.json"')
    lines.append('sh -lc "vhk plan-project . --json > \"$DEST\"/plan-project.json" || true')
    lines.append('printf "+ %s\\n" "vhk gen-host-contract-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-host-contract-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-readiness-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-readiness-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-activation-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-activation-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-route-selection-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-route-selection-pack . --force --quiet" || true')
    lines.append('echo "Route selection refresh complete."')
    return "\n".join(lines).rstrip() + "\n"


def write_route_selection_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    selection_doc: bool = True,
    fixups_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_route_selection_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )

    written: dict[str, Path] = {}
    if selection_doc:
        path = out_dir / "VHK_ROUTE_SELECTION.md"
        _write_if_allowed(path, render_route_selection_doc(plan), force=force)
        written["selection_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_ROUTE_FIXUPS.md"
        _write_if_allowed(path, render_route_fixups(plan), force=force)
        written["fixups_doc"] = path
    if plan_json:
        path = out_dir / "VHK_ROUTE_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_review_route_selection.sh"
        _write_if_allowed(path, render_route_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path
    return written

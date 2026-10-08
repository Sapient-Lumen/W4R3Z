from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.loader import load_project
from vhk.project.readiness_pack import build_readiness_plan
from vhk.project.strategy import summarize_project_strategy


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


def _route_status(
    route: Mapping[str, Any],
    readiness_map: Mapping[str, Mapping[str, Any]] | None,
    alternative_group_map: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[str, str | None, dict[str, list[str]]]:
    readiness_map = readiness_map or {}
    alternative_group_map = alternative_group_map or {}
    req_ids = [str(x) for x in list(route.get("depends_on_requirements") or []) if str(x)]
    alt_group_ids = [str(x) for x in list(route.get("depends_on_alternative_groups") or []) if str(x)]
    detail = {
        "blocked_requirements": [],
        "degraded_requirements": [],
        "unknown_requirements": [],
        "ready_requirements": [],
        "blocked_alternative_groups": [],
        "degraded_alternative_groups": [],
        "unknown_alternative_groups": [],
        "ready_alternative_groups": [],
    }
    if not req_ids and not alt_group_ids:
        kind = str(route.get("activation_kind") or "")
        if kind == "launcher":
            return "ready", "This route is the baseline fallback and does not depend on extra host contracts.", detail
        return "planned", "This route mainly depends on explicit config placement or operator review rather than probed host contracts.", detail

    for req_id in req_ids:
        item = readiness_map.get(req_id)
        status = str((item or {}).get("readiness_status") or (item or {}).get("observed_status") or "unknown")
        if status == "blocked":
            detail["blocked_requirements"].append(req_id)
        elif status == "degraded":
            detail["degraded_requirements"].append(req_id)
        elif status == "ready":
            detail["ready_requirements"].append(req_id)
        else:
            detail["unknown_requirements"].append(req_id)

    preferred_filters: list[str] = []
    for group_id in alt_group_ids:
        item = dict(alternative_group_map.get(group_id) or {})
        status = str(item.get("effective_status") or "unknown")
        if status == "blocked":
            detail["blocked_alternative_groups"].append(group_id)
        elif status == "degraded":
            detail["degraded_alternative_groups"].append(group_id)
        elif status == "ready":
            detail["ready_alternative_groups"].append(group_id)
        else:
            detail["unknown_alternative_groups"].append(group_id)
        filter_id = str(item.get("bootstrap_filter_id") or "").strip()
        if filter_id:
            preferred_filters.append(filter_id)
    if preferred_filters:
        detail["preferred_bootstrap_filters"] = preferred_filters

    filter_suffix = ""
    if preferred_filters:
        filter_suffix = " Preferred bootstrap filter(s): " + ", ".join(f"`{item}`" for item in preferred_filters) + "."
    if detail["blocked_requirements"] or detail["blocked_alternative_groups"]:
        return "blocked", "One or more required host/readiness contracts are blocked." + filter_suffix, detail
    if detail["degraded_requirements"] or detail["degraded_alternative_groups"]:
        return "degraded", "One or more required host/readiness contracts still need fixups or lifecycle work." + filter_suffix, detail
    if detail["unknown_requirements"] or detail["unknown_alternative_groups"]:
        return "unknown", "The route depends on requirements that were not fully verified on this host." + filter_suffix, detail
    note = "All currently modeled route requirements look ready on this host." + filter_suffix
    return "ready", note, detail


def build_activation_pack_plan(
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
    readiness_plan = build_readiness_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )

    readiness_map = {
        str(item.get("id") or ""): dict(item)
        for item in list(readiness_plan.get("readiness_requirements") or [])
        if isinstance(item, dict) and str(item.get("id") or "")
    }
    alternative_group_map = {
        str(item.get("id") or ""): dict(item)
        for item in list(readiness_plan.get("alternative_requirement_groups") or [])
        if isinstance(item, dict) and str(item.get("id") or "")
    }

    routes: list[dict[str, Any]] = []
    for item in list(strategy.get("activation_routes") or []):
        if not isinstance(item, Mapping):
            continue
        route = dict(item)
        route["alternative_requirement_groups"] = [
            dict(alternative_group_map[group_id])
            for group_id in [str(x) for x in list(route.get("depends_on_alternative_groups") or []) if str(x)]
            if group_id in alternative_group_map
        ]
        status, note, detail = _route_status(route, readiness_map, alternative_group_map)
        route["route_status"] = status
        if note:
            route["route_note"] = note
        route["route_detail"] = detail
        preferred_bootstrap_filters = [str(x) for x in list(detail.get("preferred_bootstrap_filters") or []) if str(x)]
        if preferred_bootstrap_filters:
            route["preferred_bootstrap_filters"] = preferred_bootstrap_filters
            route["preferred_bootstrap_filter"] = preferred_bootstrap_filters[0]
        routes.append(route)

    order = {"blocked": 0, "degraded": 1, "unknown": 2, "planned": 3, "ready": 4}
    routes.sort(key=lambda item: (order.get(str(item.get("route_status") or "unknown"), 9), str(item.get("activation_kind") or ""), str(item.get("title") or "")))

    blocked = [str(item.get("id") or "") for item in routes if str(item.get("route_status") or "") == "blocked"]
    degraded = [str(item.get("id") or "") for item in routes if str(item.get("route_status") or "") == "degraded"]
    unknown = [str(item.get("id") or "") for item in routes if str(item.get("route_status") or "") == "unknown"]
    planned = [str(item.get("id") or "") for item in routes if str(item.get("route_status") or "") == "planned"]
    ready = [str(item.get("id") or "") for item in routes if str(item.get("route_status") or "") == "ready"]

    if blocked:
        overall = "blocked"
    elif degraded:
        overall = "degraded"
    elif unknown:
        overall = "unknown"
    elif planned:
        overall = "planned"
    elif ready:
        overall = "ready"
    else:
        overall = "unknown"

    route_kinds: list[dict[str, Any]] = []
    seen_kinds: set[str] = set()
    for item in routes:
        kind = str(item.get("activation_kind") or "")
        if not kind or kind in seen_kinds:
            continue
        seen_kinds.add(kind)
        subset = [dict(route) for route in routes if str(route.get("activation_kind") or "") == kind]
        statuses = {str(route.get("route_status") or "unknown") for route in subset}
        if "blocked" in statuses:
            status = "blocked"
        elif "degraded" in statuses:
            status = "degraded"
        elif "unknown" in statuses:
            status = "unknown"
        elif statuses == {"ready"}:
            status = "ready"
        else:
            status = "planned"
        route_kinds.append(
            {
                "activation_kind": kind,
                "status": status,
                "routes": subset,
            }
        )

    startup_order = [
        {
            "step": idx,
            "route_id": str(item.get("id") or ""),
            "title": str(item.get("title") or ""),
            "activation_kind": str(item.get("activation_kind") or ""),
            "route_status": str(item.get("route_status") or "unknown"),
            "entrypoint": str(item.get("entrypoint") or ""),
        }
        for idx, item in enumerate(routes, start=1)
    ]

    review_commands = _dedupe_keep_order(
        [
            "vhk doctor --json",
            f"vhk validate {project_dir.as_posix()} --json",
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-host-contract-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-readiness-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-activation-pack {project_dir.as_posix()} --force --quiet",
            *[
                str(cmd)
                for item in routes
                for cmd in list(item.get("verification_commands") or [])
                if str(cmd)
            ],
        ]
    )

    return {
        "source_contract": "activation_pack",
        "project": dict(strategy.get("project") or {}),
        "overview": dict(strategy.get("overview") or {}),
        "activation_summary": {
            "overall_status": overall,
            "blocked_routes": blocked,
            "degraded_routes": degraded,
            "unknown_routes": unknown,
            "planned_routes": planned,
            "ready_routes": ready,
            "route_count": len(routes),
        },
        "activation_routes": routes,
        "activation_kinds": route_kinds,
        "startup_order": startup_order,
        "host_contract_summary": dict((readiness_plan.get("host_contract_summary") or {})),
        "readiness_summary": dict((readiness_plan.get("readiness_summary") or {})),
        "readiness_plan": readiness_plan,
        "review_commands": review_commands,
        "session_capabilities": dict(capability_matrix or {}),
        "session_issues": [dict(item) for item in list(capability_issues or []) if isinstance(item, dict)],
        "stack_profiles": list(strategy.get("stack_profiles") or strategy.get("deployment_profiles") or []),
        "runtime_seams": list(strategy.get("runtime_seams") or []),
        "surface_choices": list(strategy.get("surface_choices") or []),
        "host_requirements": list(strategy.get("host_requirements") or []),
        "host_snapshot": dict(host_snapshot or {}),
    }


def render_activation_routes_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("activation_summary") or {})
    routes = _trim_items(plan.get("activation_routes"), limit=12)
    startup_order = _trim_items(plan.get("startup_order"), limit=12)
    kinds = _trim_items(plan.get("activation_kinds"), limit=8)

    lines: list[str] = []
    lines.append(f"# VHK activation routes for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-activation-pack`. This joins planner strategy, host contracts, and readiness proofs into reviewable Linux activation lanes: launcher entrypoints, desktop binds, services, remappers, portal sessions, and helper daemons.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall activation status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Blocked routes: {len(list(summary.get('blocked_routes') or []))}")
    lines.append(f"- Degraded routes: {len(list(summary.get('degraded_routes') or []))}")
    lines.append(f"- Planned routes: {len(list(summary.get('planned_routes') or []))}")
    lines.append(f"- Ready routes: {len(list(summary.get('ready_routes') or []))}")
    lines.append("")

    if routes:
        lines.append("## Route matrix")
        lines.append("")
        for item in routes:
            lines.append(f"### {item.get('title') or item.get('id')}")
            lines.append("")
            lines.append(f"- Route id: `{item.get('id') or ''}`")
            lines.append(f"- Route status: `{item.get('route_status') or 'unknown'}`")
            lines.append(f"- Activation kind: `{item.get('activation_kind') or 'unknown'}`")
            lines.append(f"- Startup owner: {item.get('startup_owner') or 'n/a'}")
            lines.append(f"- Steady state: {item.get('steady_state') or 'n/a'}")
            lines.append(f"- Entrypoint: {item.get('entrypoint') or 'n/a'}")
            note = str(item.get('route_note') or '').strip()
            if note:
                lines.append(f"- Current note: {note}")
            why = str(item.get('why') or '').strip()
            if why:
                lines.append(f"- Why this lane exists: {why}")
            reqs = [str(x) for x in list(item.get('depends_on_requirements') or []) if str(x)]
            if reqs:
                lines.append(f"- Depends on requirements: {', '.join(f'`{req}`' for req in reqs)}")
            alt_groups = [dict(group) for group in list(item.get('alternative_requirement_groups') or []) if isinstance(group, dict)]
            if alt_groups:
                alt_group_ids = [str(group.get('id') or '') for group in alt_groups if str(group.get('id') or '')]
                if alt_group_ids:
                    lines.append(f"- Alternative requirement groups: {', '.join(f'`{group_id}`' for group_id in alt_group_ids)}")
                preferred_filters = [str(x) for x in list(item.get('preferred_bootstrap_filters') or []) if str(x)]
                if preferred_filters:
                    lines.append(f"- Preferred bootstrap filters: {', '.join(f'`{flt}`' for flt in preferred_filters)}")
            fallbacks = [str(x) for x in list(item.get('fallback_routes') or []) if str(x)]
            if fallbacks:
                lines.append(f"- Fallback routes: {', '.join(f'`{req}`' for req in fallbacks)}")
            lines.append("")

    lines.append("## Startup order")
    lines.append("")
    if startup_order:
        for item in startup_order:
            lines.append(f"- {item.get('step')}. `{item.get('route_id') or ''}` — `{item.get('route_status') or 'unknown'}` via {item.get('entrypoint') or 'n/a'}")
    else:
        lines.append("No activation routes were generated.")
    lines.append("")

    if kinds:
        lines.append("## Activation kinds")
        lines.append("")
        for item in kinds:
            lines.append(f"- `{item.get('activation_kind') or ''}` — `{item.get('status') or 'unknown'}` ({len(list(item.get('routes') or []))} route(s))")
        lines.append("")

    lines.append("## Review loop")
    lines.append("")
    for command in list(plan.get("review_commands") or [])[:8]:
        lines.append(f"- `{command}`")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_activation_fixups(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("activation_summary") or {})
    blocked = [dict(item) for item in list(plan.get("activation_routes") or []) if isinstance(item, dict) and str(item.get("route_status") or "") == "blocked"]
    degraded = [dict(item) for item in list(plan.get("activation_routes") or []) if isinstance(item, dict) and str(item.get("route_status") or "") == "degraded"]
    planned = [dict(item) for item in list(plan.get("activation_routes") or []) if isinstance(item, dict) and str(item.get("route_status") or "") == "planned"]

    lines: list[str] = []
    lines.append(f"# VHK activation fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-activation-pack`. Use this when the project shape looks good but the real Linux wake-up path still needs service wiring, portal/session binding, helper daemons, or explicit launcher fallback decisions.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall activation status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Blocked: {len(blocked)}")
    lines.append(f"- Degraded: {len(degraded)}")
    lines.append(f"- Planned: {len(planned)}")
    lines.append("")

    def emit(items: list[dict[str, Any]], title: str) -> None:
        lines.append(title)
        lines.append("")
        if not items:
            lines.append("None in this category.")
            lines.append("")
            return
        for item in items:
            lines.append(f"### {item.get('title') or item.get('id')}")
            lines.append("")
            lines.append(f"- Route id: `{item.get('id') or ''}`")
            lines.append(f"- Activation kind: `{item.get('activation_kind') or 'unknown'}`")
            note = str(item.get('route_note') or '').strip()
            if note:
                lines.append(f"- Why it is here: {note}")
            for req in list((item.get("route_detail") or {}).get("blocked_requirements") or [])[:4]:
                lines.append(f"- [ ] Unblock requirement: `{req}`")
            for req in list((item.get("route_detail") or {}).get("degraded_requirements") or [])[:4]:
                lines.append(f"- [ ] Fix degraded requirement: `{req}`")
            for cmd in list(item.get("verification_commands") or [])[:3]:
                lines.append(f"- Verify with: `{cmd}`")
            fallbacks = [str(x) for x in list(item.get('fallback_routes') or []) if str(x)]
            if fallbacks:
                lines.append(f"- Fallback: {', '.join(f'`{x}`' for x in fallbacks)}")
            lines.append("")

    emit(blocked, "## Blocked queue")
    emit(degraded, "## Degraded queue")
    emit(planned, "## Planned/manual review queue")
    return "\n".join(lines).rstrip() + "\n"


def render_activation_refresh_script(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST="${1:-.}"')
    lines.append('mkdir -p "$DEST/reports" "$DEST/docs" "$DEST/scripts"')
    lines.append("")
    lines.append('echo "Collecting VHK activation evidence into $DEST"')
    lines.append("")
    lines.append("run_json() {")
    lines.append('  out="$1"')
    lines.append("  shift")
    lines.append('  if sh -lc "$*" >"$DEST/reports/$out" 2>"$DEST/reports/${out%.json}.stderr"; then')
    lines.append("    :")
    lines.append("  else")
    lines.append('    echo "command failed: $*" >> "$DEST/reports/FAILURES.txt"')
    lines.append("  fi")
    lines.append("}")
    lines.append("")
    lines.append('run_json doctor.json "vhk doctor --json"')
    lines.append('run_json validate.json "vhk validate . --json"')
    lines.append('run_json plan-project.json "vhk plan-project . --json"')
    lines.append('printf "+ %s\n" "vhk gen-host-contract-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-host-contract-pack . --force --quiet" || true')
    lines.append('printf "+ %s\n" "vhk gen-readiness-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-readiness-pack . --force --quiet" || true')
    lines.append('printf "+ %s\n" "vhk gen-activation-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-activation-pack . --force --quiet" || true')
    lines.append('echo "Review: docs/VHK_ACTIVATION_ROUTES.md, docs/VHK_ACTIVATION_FIXUPS.md, docs/VHK_ACTIVATION_PLAN.json"')
    lines.append('echo "Activation refresh complete."')
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_activation_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    routes_doc: bool = True,
    fixups_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or project_dir / "docs").expanduser().resolve()
    script_dir = (script_dir or project_dir / "scripts").expanduser().resolve()

    plan = build_activation_pack_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )

    written: dict[str, Path] = {}
    if routes_doc:
        path = out_dir / "VHK_ACTIVATION_ROUTES.md"
        _write_if_allowed(path, render_activation_routes_doc(plan), force=force)
        written["routes_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_ACTIVATION_FIXUPS.md"
        _write_if_allowed(path, render_activation_fixups(plan), force=force)
        written["fixups_doc"] = path
    if plan_json:
        path = out_dir / "VHK_ACTIVATION_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_review_activation_routes.sh"
        _write_if_allowed(path, render_activation_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path

    return written

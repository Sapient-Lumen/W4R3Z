from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from vhk.project.host_contract_pack import attach_alternative_package_context, build_host_contract_plan, build_portal_route_contract, summarize_requirement_alternative_groups
from vhk.project.loader import load_project
from vhk.project.strategy import summarize_project_strategy
from vhk.system.doctor import probe_current_user_groups, probe_input_event_access, probe_systemd_unit


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


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 8) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _service_unit_key(scope: str, unit: str) -> str:
    return f"{str(scope or 'system').strip().lower()}:{str(unit or '').strip()}"


def _service_state_to_track(status: str | None) -> str:
    lowered = str(status or "unknown").strip().lower()
    if lowered == "ok":
        return "ready"
    if lowered in {"inactive", "activating", "deactivating", "loaded"}:
        return "degraded"
    if lowered in {"failed", "unit_missing"}:
        return "blocked"
    return "unknown"


def _helper_present(snapshot: Mapping[str, Any] | None, *names: str) -> bool | None:
    if not isinstance(snapshot, Mapping):
        return None
    helpers = snapshot.get("helpers")
    if not isinstance(helpers, Mapping):
        return None
    results = [bool(helpers.get(name)) for name in names if name]
    if not results:
        return None
    return any(results)


def derive_service_unit_hints(requirements: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    """Return likely systemd units for host requirements.

    The goal is not to be exhaustive. It is to provide a reviewable baseline for
    common Linux-native deployment lanes already modeled by the planner.
    """

    hints: list[dict[str, str]] = []

    def add(unit: str, scope: str, *, title: str, requirement_id: str) -> None:
        entry = {
            "unit": unit,
            "scope": scope,
            "title": title,
            "requirement_id": requirement_id,
        }
        if entry not in hints:
            hints.append(entry)

    for item in list(requirements or []):
        if not isinstance(item, Mapping):
            continue
        req_id = str(item.get("id") or "").strip()
        services = {str(x).strip().lower() for x in list(item.get("services") or []) if str(x).strip()}

        if req_id == "text-surface-service" or "espanso" in services:
            add("espanso.service", "user", title="Espanso user service", requirement_id=req_id or "text-surface-service")
        if req_id == "watcher-user-service":
            add("vhk-busd.service", "user", title="VHK bus/watcher service", requirement_id=req_id)
        if req_id == "ydotool-daemon" or "ydotoold" in services:
            add("ydotoold.service", "user", title="ydotoold user service", requirement_id=req_id or "ydotool-daemon")
            add("ydotoold.service", "system", title="ydotoold system service", requirement_id=req_id or "ydotool-daemon")
        if req_id == "dotool-daemon" or "dotoold" in services:
            add("dotoold.service", "user", title="dotoold user service", requirement_id=req_id or "dotool-daemon")
            add("dotoold.service", "system", title="dotoold system service", requirement_id=req_id or "dotool-daemon")
        if req_id == "keyd-remapper-service" or "keyd" in services:
            add("keyd.service", "system", title="keyd system daemon", requirement_id=req_id or "keyd-remapper-service")
        if req_id == "kanata-remapper-service" or "kanata" in services:
            add("kanata.service", "user", title="Kanata user service", requirement_id=req_id or "kanata-remapper-service")
            add("kanata.service", "system", title="Kanata system service", requirement_id=req_id or "kanata-remapper-service")
        if req_id == "xremap-remapper-service" or "xremap" in services:
            add("xremap.service", "user", title="xremap user service", requirement_id=req_id or "xremap-remapper-service")
            add("xremap.service", "system", title="xremap system service", requirement_id=req_id or "xremap-remapper-service")
        if req_id == "kmonad-remapper-service" or "kmonad" in services:
            add("kmonad.service", "user", title="KMonad user service", requirement_id=req_id or "kmonad-remapper-service")
            add("kmonad.service", "system", title="KMonad system service", requirement_id=req_id or "kmonad-remapper-service")

    return hints


def collect_live_readiness_snapshot(
    requirements: list[dict[str, Any]] | None,
    *,
    base_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Collect live service/group probes for readiness review."""

    snapshot = dict(base_snapshot or {})
    if not isinstance(snapshot.get("user_groups"), Mapping):
        snapshot["user_groups"] = probe_current_user_groups()
    if not isinstance(snapshot.get("input_event_access"), Mapping):
        snapshot["input_event_access"] = probe_input_event_access()

    service_units: dict[str, Any] = {}
    existing_units = snapshot.get("service_units")
    if isinstance(existing_units, Mapping):
        service_units.update({str(k): v for k, v in existing_units.items()})

    for hint in derive_service_unit_hints(list(requirements or [])):
        key = _service_unit_key(str(hint.get("scope") or "system"), str(hint.get("unit") or ""))
        if key in service_units:
            continue
        service_units[key] = probe_systemd_unit(str(hint.get("unit") or ""), scope=str(hint.get("scope") or "system"))

    snapshot["service_units"] = service_units
    return snapshot


def _find_service_probe(snapshot: Mapping[str, Any] | None, unit: str, scope: str) -> dict[str, Any] | None:
    if not isinstance(snapshot, Mapping):
        return None
    service_units = snapshot.get("service_units")
    if not isinstance(service_units, Mapping):
        return None
    item = service_units.get(_service_unit_key(scope, unit))
    return dict(item) if isinstance(item, Mapping) else None


def _service_readiness(
    snapshot: Mapping[str, Any] | None,
    unit_hints: list[dict[str, str]],
) -> tuple[str, str | None, list[dict[str, Any]]]:
    probes: list[dict[str, Any]] = []
    tracks: list[str] = []
    for hint in unit_hints:
        unit = str(hint.get("unit") or "")
        scope = str(hint.get("scope") or "system")
        probe = _find_service_probe(snapshot, unit, scope)
        if probe:
            probes.append(probe)
            tracks.append(_service_state_to_track(str(probe.get("status") or "unknown")))
        else:
            probes.append({"unit": unit, "scope": scope, "status": "unknown"})
            tracks.append("unknown")

    if "ready" in tracks:
        return "ready", "A matching service unit is active.", probes
    if "blocked" in tracks:
        return "blocked", "A matching service unit is missing or failed.", probes
    if "degraded" in tracks:
        return "degraded", "A matching service unit exists but is not active.", probes
    return "unknown", "Service manager state was not confirmed.", probes


def _permission_readiness(item: Mapping[str, Any], snapshot: Mapping[str, Any] | None) -> tuple[str, str | None, dict[str, Any]]:
    uinput = dict((snapshot or {}).get("uinput") or {}) if isinstance(snapshot, Mapping) else {}
    groups = dict((snapshot or {}).get("user_groups") or {}) if isinstance(snapshot, Mapping) else {}
    input_events = dict((snapshot or {}).get("input_event_access") or {}) if isinstance(snapshot, Mapping) else {}

    detail = {
        "uinput": uinput,
        "user_groups": groups,
        "input_event_access": input_events,
    }

    can_write = uinput.get("can_write")
    input_status = str(input_events.get("status") or "unknown")
    group_names = {str(x) for x in list(groups.get("group_names") or []) if str(x)}
    required_groups = {str(x) for x in list(item.get("groups") or []) if str(x)}
    has_any_required_group = bool(group_names.intersection(required_groups))

    if can_write is True and input_status == "ok":
        return "ready", "uinput is writable and at least one raw input event device was readable.", detail
    if can_write is False:
        return "blocked", "`/dev/uinput` is present but not writable for the current user or service.", detail
    if str(uinput.get("status") or "") == "missing":
        return "blocked", "`/dev/uinput` was not found on this host.", detail
    if can_write is True and input_status in {"permission_denied", "missing"}:
        return "degraded", "uinput is writable, but raw input event access still needs review.", detail
    if has_any_required_group:
        return "degraded", "Relevant input/uinput groups are present, but live device access was not fully confirmed.", detail
    return "unknown", "Input/uinput group membership and live access were not confirmed.", detail


def _requirement_readiness(
    item: Mapping[str, Any],
    *,
    host_snapshot: Mapping[str, Any] | None,
) -> tuple[str, str | None, dict[str, Any]]:
    req_id = str(item.get("id") or "")
    req_type = str(item.get("requirement_type") or "")
    observed_status = str(item.get("observed_status") or "unknown")

    if req_id == "uinput-permissions":
        return _permission_readiness(item, host_snapshot)

    if req_id == "portal-backend-config":
        cfg = dict((host_snapshot or {}).get("xdg_portal_backend_config") or {}) if isinstance(host_snapshot, Mapping) else {}
        status = str(cfg.get("status") or "unknown")
        if status == "ok":
            return "ready", "Portal routing config with a `[preferred]` section was found.", {"portal_backend_config": cfg}
        if status in {"config_missing", "missing_preferred_section"}:
            return "degraded", "Portal routing config is incomplete or hidden behind distro defaults.", {"portal_backend_config": cfg}
        if status == "parse_failed":
            return "blocked", "Portal routing config was found but could not be parsed.", {"portal_backend_config": cfg}
        return "unknown", "Portal routing config was not confirmed.", {"portal_backend_config": cfg}

    if req_id == "ydotool-daemon":
        socket_info = dict((host_snapshot or {}).get("ydotool_socket") or {}) if isinstance(host_snapshot, Mapping) else {}
        if str(socket_info.get("status") or "") == "ok":
            return "ready", "ydotoold socket was reachable.", {"ydotool_socket": socket_info}
        helper_present = _helper_present(host_snapshot, "ydotool")
        readiness, note, probes = _service_readiness(host_snapshot, derive_service_unit_hints([dict(item)]))
        if helper_present is False:
            return "blocked", "ydotool binary was not found on PATH.", {"ydotool_socket": socket_info, "service_units": probes}
        if readiness == "ready":
            return "degraded", "ydotoold service looks active, but its socket was not reachable from this session.", {"ydotool_socket": socket_info, "service_units": probes}
        if readiness in {"blocked", "degraded"}:
            return "blocked", note or "ydotoold service was not ready.", {"ydotool_socket": socket_info, "service_units": probes}
        return "unknown", "ydotool lifecycle was not confirmed.", {"ydotool_socket": socket_info, "service_units": probes}

    if req_id == "dotool-daemon":
        helper_present = _helper_present(host_snapshot, "dotool", "dotoolc", "dotoold")
        readiness, note, probes = _service_readiness(host_snapshot, derive_service_unit_hints([dict(item)]))
        if readiness == "ready":
            return "ready", note or "dotoold service was active.", {"service_units": probes}
        if helper_present is False:
            return "blocked", "dotool / dotoolc helper binaries were not found on PATH.", {"service_units": probes}
        if readiness in {"blocked", "degraded"}:
            return "degraded", note or "dotoold service was not ready.", {"service_units": probes}
        if helper_present is True:
            return "unknown", "dotool helpers are installed, but dotoold lifecycle was not confirmed.", {"service_units": probes}
        return "unknown", "dotool lifecycle was not confirmed.", {"service_units": probes}

    if req_id == "text-surface-service":
        helper_present = _helper_present(host_snapshot, "espanso")
        readiness, note, probes = _service_readiness(host_snapshot, derive_service_unit_hints([dict(item)]))
        if helper_present is False:
            return "blocked", "Espanso binary was not found on PATH.", {"service_units": probes}
        if readiness == "ready":
            return "ready", note, {"service_units": probes}
        if readiness in {"blocked", "degraded"}:
            return "degraded", note, {"service_units": probes}
        return "unknown", "Text-surface service state was not confirmed.", {"service_units": probes}

    if req_id == "watcher-user-service":
        readiness, note, probes = _service_readiness(host_snapshot, derive_service_unit_hints([dict(item)]))
        if readiness == "ready":
            return "ready", note, {"service_units": probes}
        if readiness in {"blocked", "degraded"}:
            return "degraded", note, {"service_units": probes}
        return "unknown", "Watcher service state was not confirmed.", {"service_units": probes}

    if req_id in {"keyd-remapper-service", "kanata-remapper-service", "xremap-remapper-service", "kmonad-remapper-service"}:
        helper_map = {
            "keyd-remapper-service": ("keyd", "keyd", "keyd remapper service was not ready."),
            "kanata-remapper-service": ("kanata", "Kanata", "Kanata remapper service was not ready."),
            "xremap-remapper-service": ("xremap", "xremap", "xremap remapper service was not ready."),
            "kmonad-remapper-service": ("kmonad", "KMonad", "KMonad remapper service was not ready."),
        }
        helper_name, label, blocked_note = helper_map[req_id]
        helper_present = _helper_present(host_snapshot, helper_name)
        readiness, note, probes = _service_readiness(host_snapshot, derive_service_unit_hints([dict(item)]))
        if readiness == "ready":
            return "ready", note or f"{label} service was active.", {"service_units": probes}
        if helper_present is False:
            return "blocked", f"{label} binary was not found on PATH.", {"service_units": probes}
        if readiness in {"blocked", "degraded"}:
            return "degraded", note or blocked_note, {"service_units": probes}
        if helper_present is True:
            return "unknown", f"{label} is installed, but service lifecycle was not confirmed.", {"service_units": probes}
        return "unknown", f"{label} lifecycle was not confirmed.", {"service_units": probes}

    if req_type == "portal":
        track = {"ready": "ready", "degraded": "degraded", "blocked": "blocked"}.get(observed_status, "unknown")
        capability_note = str(item.get("observed_note") or "").strip() or None
        return track, capability_note, {"portal_interfaces": list(item.get("portal_interfaces") or [])}

    if req_type == "service":
        readiness, note, probes = _service_readiness(host_snapshot, derive_service_unit_hints([dict(item)]))
        return readiness, note, {"service_units": probes}

    return {"ready": "ready", "degraded": "degraded", "blocked": "blocked"}.get(observed_status, "unknown"), None, {}


def build_readiness_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        evidence_lane_profile=evidence_lane_profile,
    )
    host_plan = build_host_contract_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane_profile,
    )
    requirements = [dict(item) for item in list(host_plan.get("host_requirements") or []) if isinstance(item, dict)]
    host_snapshot = dict(host_snapshot or {})

    readiness_requirements: list[dict[str, Any]] = []
    for item in requirements:
        readiness, note, detail = _requirement_readiness(item, host_snapshot=host_snapshot)
        enriched = dict(item)
        enriched["readiness_status"] = readiness
        if note:
            enriched["readiness_note"] = note
        if detail:
            enriched["readiness_detail"] = detail
        readiness_requirements.append(enriched)

    readiness_requirements, alternative_groups = summarize_requirement_alternative_groups(
        readiness_requirements,
        status_key="readiness_status",
        effective_key="effective_readiness_status",
    )
    package_group_by_capability = {
        str(item.get("capability") or ""): dict(item)
        for item in list((host_plan.get("package_plan") or {}).get("package_groups") or [])
        if isinstance(item, Mapping) and str(item.get("capability") or "")
    }
    alternative_groups = attach_alternative_package_context(alternative_groups, package_group_by_capability)

    readiness_requirements.sort(
        key=lambda item: (
            {"blocked": 0, "degraded": 1, "unknown": 2, "ready": 3}.get(str(item.get("readiness_status") or "unknown"), 2),
            {"required": 0, "recommended": 1, "conditional": 2}.get(str(item.get("priority") or "conditional"), 2),
            str(item.get("title") or ""),
        )
    )

    blocked = [str(item.get("id") or "") for item in readiness_requirements if str(item.get("readiness_status") or "") == "blocked"]
    degraded = [str(item.get("id") or "") for item in readiness_requirements if str(item.get("readiness_status") or "") == "degraded"]
    unknown = [str(item.get("id") or "") for item in readiness_requirements if str(item.get("readiness_status") or "") == "unknown"]
    ready = [str(item.get("id") or "") for item in readiness_requirements if str(item.get("readiness_status") or "") == "ready"]
    effective_units = [
        {"id": str(item.get("id") or ""), "capability": item.get("capability"), "status": str(item.get("readiness_status") or "unknown")}
        for item in readiness_requirements
        if not str(item.get("alternative_group") or "").strip()
    ]
    effective_units.extend(
        {
            "id": str(item.get("id") or ""),
            "capability": item.get("capability"),
            "status": str(item.get("effective_status") or "unknown"),
            "title": item.get("title"),
            "active_member_ids": list(item.get("active_member_ids") or []),
        }
        for item in alternative_groups
    )
    effective_blocked = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "blocked"]
    effective_degraded = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "degraded"]
    effective_unknown = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "unknown"]
    effective_ready = [str(item.get("id") or "") for item in effective_units if str(item.get("status") or "") == "ready"]
    overall_status = "blocked" if effective_blocked else ("degraded" if effective_degraded else ("ready" if effective_units and not effective_unknown else "unknown"))

    lanes: list[dict[str, Any]] = []
    for capability_lane in list(host_plan.get("capability_lanes") or []):
        if not isinstance(capability_lane, Mapping):
            continue
        capability = str(capability_lane.get("capability") or "")
        items = [dict(item) for item in readiness_requirements if str(item.get("capability") or "") == capability]
        capability_alternative_groups = [dict(item) for item in alternative_groups if str(item.get("capability") or "") == capability]
        unit_statuses = [
            str(item.get("readiness_status") or "unknown")
            for item in items
            if not str(item.get("alternative_group") or "").strip()
        ]
        unit_statuses.extend(str(item.get("effective_status") or "unknown") for item in capability_alternative_groups)
        if "blocked" in unit_statuses:
            lane_status = "blocked"
        elif "degraded" in unit_statuses:
            lane_status = "degraded"
        elif unit_statuses and set(unit_statuses) == {"ready"}:
            lane_status = "ready"
        else:
            lane_status = "unknown"
        lanes.append(
            {
                "capability": capability,
                "status": lane_status,
                "requirements": items,
                "alternative_groups": capability_alternative_groups,
                "package_group": dict(capability_lane.get("package_group") or {}),
                "host_contract_status": capability_lane.get("status"),
            }
        )

    service_hints = derive_service_unit_hints(requirements)
    service_units: list[dict[str, Any]] = []
    for hint in service_hints:
        probe = _find_service_probe(host_snapshot, str(hint.get("unit") or ""), str(hint.get("scope") or "system")) or {
            "unit": hint.get("unit"),
            "scope": hint.get("scope"),
            "status": "unknown",
        }
        row = dict(hint)
        row["probe"] = probe
        row["readiness_status"] = _service_state_to_track(str(probe.get("status") or "unknown"))
        service_units.append(row)

    portal_route_contract = build_portal_route_contract(
        requirements,
        capability_matrix=capability_matrix,
        host_snapshot=host_snapshot,
    )

    review_commands = _dedupe_keep_order(
        [
            "vhk doctor --json",
            f"vhk validate {project_dir.as_posix()} --json",
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-host-contract-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-readiness-pack {project_dir.as_posix()} --force --quiet",
            *[
                str(cmd)
                for item in readiness_requirements
                for cmd in list(item.get("verify_commands") or [])
                if str(cmd)
            ],
        ]
    )

    return {
        "source_contract": "readiness_pack",
        "project": dict(strategy.get("project") or {}),
        "overview": dict(strategy.get("overview") or {}),
        "readiness_summary": {
            "overall_status": overall_status,
            "blocked_requirements": blocked,
            "degraded_requirements": degraded,
            "unknown_requirements": unknown,
            "ready_requirements": ready,
            "effective_blockers": effective_blocked,
            "effective_degraded": effective_degraded,
            "effective_unknown": effective_unknown,
            "effective_ready": effective_ready,
            "requirement_count": len(readiness_requirements),
            "alternative_group_count": len(alternative_groups),
        },
        "readiness_requirements": readiness_requirements,
        "alternative_requirement_groups": alternative_groups,
        "capability_lanes": lanes,
        "service_units": service_units,
        "user_groups": dict(host_snapshot.get("user_groups") or {}),
        "input_event_access": dict(host_snapshot.get("input_event_access") or {}),
        "host_contract_summary": dict(host_plan.get("host_summary") or {}),
        "host_contract": host_plan,
        "review_commands": review_commands,
        "session_capabilities": dict(capability_matrix or {}),
        "session_issues": [dict(item) for item in list(capability_issues or []) if isinstance(item, dict)],
        "portal_route_contract": portal_route_contract,
        "stack_profiles": list(strategy.get("stack_profiles") or strategy.get("deployment_profiles") or []),
        "toolchain_choices": list(strategy.get("toolchain_choices") or []),
        "host_snapshot": host_snapshot,
    }


def render_readiness_report(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    readiness_summary = dict(plan.get("readiness_summary") or {})
    readiness_requirements = _trim_items(plan.get("readiness_requirements"), limit=10)
    alternative_groups = _trim_items(plan.get("alternative_requirement_groups"), limit=8)
    capability_lanes = _trim_items(plan.get("capability_lanes"), limit=8)
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    service_units = _trim_items(plan.get("service_units"), limit=10)
    user_groups = dict(plan.get("user_groups") or {})
    input_event_access = dict(plan.get("input_event_access") or {})

    lines: list[str] = []
    lines.append(f"# VHK readiness report for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-readiness-pack`. This is the live-proof layer that sits on top of `gen-host-contract-pack`: service state, groups, raw-input access, and session-visible deployment readiness.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall readiness: `{readiness_summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Effective blockers: {len(list(readiness_summary.get('effective_blockers') or []))}")
    lines.append(f"- Effective degraded units: {len(list(readiness_summary.get('effective_degraded') or []))}")
    lines.append(f"- Effective unknown units: {len(list(readiness_summary.get('effective_unknown') or []))}")
    lines.append(f"- Alternative requirement groups: {readiness_summary.get('alternative_group_count') or 0}")
    lines.append("")

    if readiness_requirements:
        lines.append("## Requirement readiness")
        lines.append("")
        for item in readiness_requirements:
            lines.append(f"### {item.get('title') or item.get('id')}")
            lines.append("")
            lines.append(f"- Requirement id: `{item.get('id') or ''}`")
            lines.append(f"- Readiness: `{item.get('readiness_status') or 'unknown'}`")
            lines.append(f"- Host-contract status: `{item.get('observed_status') or 'unknown'}`")
            lines.append(f"- Priority: `{item.get('priority') or 'conditional'}`")
            capability = str(item.get('capability') or '').strip()
            if capability:
                lines.append(f"- Capability: `{capability}`")
            group_id = str(item.get('alternative_group') or '').strip()
            if group_id:
                lines.append(f"- Alternative group: `{group_id}` (`{item.get('alternative_group_status') or 'unknown'}`)")
                active = [str(x) for x in list(item.get('alternative_group_active_member_ids') or []) if str(x)]
                if active:
                    lines.append(f"- Active lane member(s): `{', '.join(active)}`")
                preferred = str(item.get('alternative_group_preferred_member_id') or '').strip()
                if preferred:
                    lines.append(f"- Preferred lane member: `{preferred}`")
                if item.get('suppressed_by_alternative'):
                    lines.append("- Effective blocker status: `covered`")
                group_note = str(item.get('alternative_group_note') or '').strip()
                if group_note:
                    lines.append(f"- Alternative note: {group_note}")
            note = str(item.get('readiness_note') or '').strip()
            if note:
                lines.append(f"- Current note: {note}")
            fixes = [str(x) for x in list(item.get('fixup_hints') or []) if str(x)]
            if fixes:
                lines.append("- Fixup hints:")
                for fix in fixes[:3]:
                    lines.append(f"  - {fix}")
            lines.append("")

    if alternative_groups:
        lines.append("## Alternative requirement groups")
        lines.append("")
        for group in alternative_groups:
            lines.append(f"### {group.get('title') or group.get('id')}")
            lines.append("")
            lines.append(f"- Policy: `{group.get('policy') or 'one_of'}`")
            lines.append(f"- Effective status: `{group.get('effective_status') or 'unknown'}`")
            preferred = str(group.get('preferred_member_id') or '').strip()
            if preferred:
                lines.append(f"- Preferred member: `{preferred}`")
            bootstrap_filter = str(group.get('bootstrap_filter_id') or '').strip()
            if bootstrap_filter:
                lines.append(f"- Preferred bootstrap filter: `{bootstrap_filter}`")
            note = str(group.get('note') or '').strip()
            if note:
                lines.append(f"- Note: {note}")
            for member in [dict(item) for item in list(group.get('members') or []) if isinstance(item, dict)]:
                line = f"- `{member.get('id') or ''}` → `{member.get('readiness_status') or 'unknown'}`"
                member_filter = str(member.get('bootstrap_filter_id') or '').strip()
                if member_filter:
                    line += f" (`{member_filter}`)"
                lines.append(line)
            lines.append("")

    if portal_route_contract:
        lines.append("## Portal route proofs")
        lines.append("")
        lines.append("This pack keeps portal readiness honest by comparing configured routing, installed backend manifests, and live frontend availability in the same review surface.")
        lines.append("")
        lines.append(f"- Route status: `{portal_route_contract.get('status') or 'unknown'}`")
        lines.append(f"- Config status: `{portal_route_contract.get('config_status') or 'unknown'}`")
        lines.append(f"- Manifest status: `{portal_route_contract.get('manifest_status') or 'unknown'}`")
        lines.append(f"- Installed backends: `{', '.join([str(x) for x in list(portal_route_contract.get('installed_backends') or []) if str(x)]) or '(none reported)'}`")
        issues = [dict(item) for item in list(portal_route_contract.get('issues') or []) if isinstance(item, dict)]
        if issues:
            lines.append("- Route issues:")
            for item in issues[:5]:
                lines.append(f"  - {item.get('summary') or item.get('kind') or 'portal issue'}")
        lines.append("")
        for item in [dict(x) for x in list(portal_route_contract.get('interfaces') or []) if isinstance(x, dict)][:8]:
            lines.append(f"- `{item.get('short_name') or item.get('interface') or ''}` — live `{item.get('live_status') or 'unknown'}`; configured `{', '.join([str(x) for x in list(item.get('configured_backends') or []) if str(x)]) or '(default)'}`; usable `{', '.join([str(x) for x in list(item.get('usable_backends') or []) if str(x)]) or '(none)'}`")
        lines.append("")

    lines.append("## Service lifecycle proofs")
    lines.append("")
    if service_units:
        for item in service_units:
            probe = dict(item.get("probe") or {})
            lines.append(f"- `{item.get('scope') or 'system'}:{item.get('unit') or ''}` — `{probe.get('status') or 'unknown'}` ({item.get('title') or item.get('requirement_id') or 'service'})")
    else:
        lines.append("No planner-backed service units were identified for this project.")
    lines.append("")

    lines.append("## Permission and device proofs")
    lines.append("")
    group_names = [str(x) for x in list(user_groups.get("group_names") or []) if str(x)]
    lines.append(f"- Current user groups: {', '.join(group_names) if group_names else '(none reported)' }")
    lines.append(f"- Raw input event access: `{input_event_access.get('status') or 'unknown'}`")
    if input_event_access.get("device_count") is not None:
        lines.append(f"- Event devices discovered: {input_event_access.get('device_count')} (readable: {input_event_access.get('readable_count') or 0})")
    lines.append("")

    if capability_lanes:
        lines.append("## Capability lanes")
        lines.append("")
        for lane in capability_lanes:
            lines.append(f"### {lane.get('capability') or 'capability'}")
            lines.append("")
            lines.append(f"- Readiness: `{lane.get('status') or 'unknown'}`")
            lines.append(f"- Host-contract lane: `{lane.get('host_contract_status') or 'unknown'}`")
            package_group = dict(lane.get("package_group") or {})
            if package_group:
                lines.append(f"- Package group: `{package_group.get('id') or package_group.get('group_id') or 'n/a'}`")
            alternative_lane_groups = [dict(item) for item in list(lane.get('alternative_groups') or []) if isinstance(item, dict)]
            if alternative_lane_groups:
                lines.append("- Alternative lane groups:")
                for alt_group in alternative_lane_groups:
                    active = [str(x) for x in list(alt_group.get('active_member_ids') or []) if str(x)]
                    line = f"  - `{alt_group.get('id') or ''}` → `{alt_group.get('effective_status') or 'unknown'}`"
                    if active:
                        line += f" via `{', '.join(active)}`"
                    preferred = str(alt_group.get('preferred_member_id') or '').strip()
                    if preferred and preferred not in active:
                        line += f" (preferred: `{preferred}`)"
                    bootstrap_filter = str(alt_group.get('bootstrap_filter_id') or '').strip()
                    if bootstrap_filter:
                        line += f" [bootstrap: `{bootstrap_filter}`]"
                    lines.append(line)
            lines.append("")

    lines.append("## Refresh loop")
    lines.append("")
    for command in list(plan.get("review_commands") or [])[:8]:
        lines.append(f"- `{command}`")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_readiness_fixups(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    readiness_summary = dict(plan.get("readiness_summary") or {})
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    blocked = [
        dict(item)
        for item in list(plan.get("readiness_requirements") or [])
        if isinstance(item, dict)
        and str(item.get("readiness_status") or "") == "blocked"
        and not bool(item.get("suppressed_by_alternative"))
    ]
    degraded = [
        dict(item)
        for item in list(plan.get("readiness_requirements") or [])
        if isinstance(item, dict)
        and str(item.get("readiness_status") or "") == "degraded"
        and not bool(item.get("suppressed_by_alternative"))
    ]
    alternative_groups = _trim_items(plan.get("alternative_requirement_groups"), limit=8)
    service_units = _trim_items(plan.get("service_units"), limit=10)

    lines: list[str] = []
    lines.append(f"# VHK readiness fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-readiness-pack`. Use this when the project is designed and packaged sensibly, but the current host still needs service activation, permission work, or portal/session review.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall readiness: `{readiness_summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Effective blockers: {len(list(readiness_summary.get('effective_blockers') or []))}")
    lines.append(f"- Effective degraded units: {len(list(readiness_summary.get('effective_degraded') or []))}")
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
            lines.append(f"- Requirement id: `{item.get('id') or ''}`")
            lines.append(f"- Capability: `{item.get('capability') or 'n/a'}`")
            note = str(item.get('readiness_note') or item.get('observed_note') or '').strip()
            if note:
                lines.append(f"- Why it is in this queue: {note}")
            for hint in list(item.get("fixup_hints") or [])[:4]:
                lines.append(f"- [ ] {hint}")
            for cmd in list(item.get("verify_commands") or [])[:3]:
                lines.append(f"- Verify with: `{cmd}`")
            lines.append("")

    if portal_route_contract:
        lines.append("## Portal routing queue")
        lines.append("")
        lines.append(f"- Route status: `{portal_route_contract.get('status') or 'unknown'}`")
        for item in [dict(x) for x in list(portal_route_contract.get('issues') or []) if isinstance(x, dict)][:6]:
            lines.append(f"- `{item.get('severity') or 'info'}` {item.get('summary') or item.get('kind') or 'portal issue'}")
        lines.append("")

    emit(blocked, "## Blocked queue")
    emit(degraded, "## Degraded queue")

    if alternative_groups:
        lines.append("## Alternative lane review")
        lines.append("")
        for group in alternative_groups:
            lines.append(f"### {group.get('title') or group.get('id')}")
            lines.append("")
            lines.append(f"- Effective status: `{group.get('effective_status') or 'unknown'}`")
            note = str(group.get('note') or '').strip()
            if note:
                lines.append(f"- Note: {note}")
            for member in [dict(item) for item in list(group.get('members') or []) if isinstance(item, dict)]:
                lines.append(f"- `{member.get('id') or ''}` → `{member.get('readiness_status') or 'unknown'}`")
            lines.append("")

    lines.append("## Service unit review")
    lines.append("")
    if service_units:
        for item in service_units:
            probe = dict(item.get("probe") or {})
            lines.append(f"- `{item.get('scope') or 'system'}:{item.get('unit') or ''}` → `{probe.get('status') or 'unknown'}`")
    else:
        lines.append("No planner-backed service units were identified.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_readiness_refresh_script(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST="${1:-.}"')
    lines.append('mkdir -p "$DEST/reports" "$DEST/docs" "$DEST/scripts"')
    lines.append("")
    lines.append('echo "Collecting VHK readiness evidence into $DEST"')
    lines.append("")
    lines.append("run_json() {")
    lines.append("  out=\"$1\"")
    lines.append("  shift")
    lines.append("  if sh -lc \"$*\" >\"$DEST/reports/$out\" 2>\"$DEST/reports/${out%.json}.stderr\"; then")
    lines.append("    :")
    lines.append("  else")
    lines.append("    echo \"command failed: $*\" >> \"$DEST/reports/FAILURES.txt\"")
    lines.append("  fi")
    lines.append("}")
    lines.append("")
    lines.append('run_json doctor.json "vhk doctor --json"')
    lines.append('run_json validate.json "vhk validate . --json"')
    lines.append('run_json plan-project.json "vhk plan-project . --json"')
    lines.append('printf "+ %s\\n" "vhk gen-host-contract-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-host-contract-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-readiness-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-readiness-pack . --force --quiet" || true')
    lines.append('echo "Review: docs/VHK_READINESS_REPORT.md, docs/VHK_READINESS_FIXUPS.md, docs/VHK_READINESS_PLAN.json"')
    lines.append('echo "Readiness refresh complete."')
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_readiness_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    report_doc: bool = True,
    fixups_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or project_dir / "docs").expanduser().resolve()
    script_dir = (script_dir or project_dir / "scripts").expanduser().resolve()

    plan = build_readiness_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane_profile,
    )

    written: dict[str, Path] = {}
    if report_doc:
        path = out_dir / "VHK_READINESS_REPORT.md"
        _write_if_allowed(path, render_readiness_report(plan), force=force)
        written["report_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_READINESS_FIXUPS.md"
        _write_if_allowed(path, render_readiness_fixups(plan), force=force)
        written["fixups_doc"] = path
    if plan_json:
        path = out_dir / "VHK_READINESS_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_refresh_readiness_report.sh"
        _write_if_allowed(path, render_readiness_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path

    return written

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from vhk.project.release_lane_pack import build_release_lane_plan


_WLROOTS_DESKTOPS = {"sway", "hyprland", "river", "wayfire", "phosh", "labwc", "niri"}


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


def _normalized_status(value: str | None) -> str:
    lowered = str(value or "unknown").strip().lower()
    if lowered in {"ready", "ok", "pass", "active", "loaded"}:
        return "ready"
    if lowered in {"degraded", "limited", "warn", "warning", "partial", "ok_with_warnings"}:
        return "degraded"
    if lowered in {"blocked", "fail", "failed", "missing", "permission_denied", "service_missing", "interface_missing", "backend_missing", "inactive", "masked", "not_found", "config_missing", "parse_failed"}:
        return "blocked"
    if lowered in {"planned", "install_needed"}:
        return "planned"
    return "unknown"


def match_desktop_family(desktop_family: str, current_desktop: str | None) -> tuple[str, str]:
    family = str(desktop_family or "").strip().lower()
    current = str(current_desktop or "").strip().lower()
    if not family:
        return "unknown", "Target lane does not name a desktop family."
    if not current:
        return "unknown", "Current desktop is not visible in the host snapshot."
    tokens = [part for part in current.replace(';', ':').split(':') if part]
    token_set = set(tokens)
    if family == "gnome":
        if "gnome" in token_set:
            return "match", "Current desktop tokens include GNOME."
        return "mismatch", f"Current desktop `{current}` does not look GNOME-like."
    if family == "kde":
        if "kde" in token_set or "plasma" in token_set:
            return "match", "Current desktop tokens include KDE/Plasma."
        return "mismatch", f"Current desktop `{current}` does not look KDE/Plasma-like."
    if family == "wlroots":
        matches = sorted(token_set & _WLROOTS_DESKTOPS)
        if matches:
            return "match", f"Current desktop tokens include wlroots-style compositor markers: {', '.join(matches)}."
        return "mismatch", f"Current desktop `{current}` does not look like a reviewed wlroots-style desktop."
    if family == "x11":
        return "neutral", "Generic X11 target lanes do not rely on one desktop-family token."
    if family in token_set:
        return "match", f"Current desktop tokens include `{family}`."
    return "mismatch", f"Current desktop `{current}` does not match target family `{family}`."


def _compare_expectation(expected: str, observed: str) -> tuple[str, str]:
    if expected == "ready":
        if observed == "ready":
            return "aligned", "Host meets a ready expectation."
        if observed in {"degraded", "planned"}:
            return "degraded", "Host only partially meets a ready expectation."
        if observed == "blocked":
            return "drifted", "Host blocks a lane requirement that the target story expects ready."
        return "unknown", "Host evidence is too incomplete to confirm a ready expectation."
    if expected == "planned":
        if observed == "ready":
            return "ahead", "Host already satisfies a requirement the target lane still treats as install/config work."
        if observed == "degraded":
            return "degraded", "Host shows partial progress on a planned requirement."
        if observed == "blocked":
            return "planned_gap", "Target lane still assumes follow-up install/config work here."
        return "unknown", "Host evidence is too incomplete to confirm the planned requirement."
    if expected == "blocked":
        if observed == "blocked":
            return "aligned", "Host remains outside this optional/out-of-profile requirement, matching the lane story."
        if observed in {"ready", "degraded", "planned"}:
            return "outside_profile", "Host has capability that this target lane does not treat as part of the flagship story."
        return "unknown", "Host evidence is too incomplete to compare this out-of-profile requirement."
    return "unknown", "Target expectation is not specific enough for a stronger comparison."


def _infer_deploy_style(lane: Mapping[str, Any]) -> str:
    explicit = str(lane.get("deploy_style") or "").strip()
    if explicit:
        return explicit
    trigger_route = str(lane.get("trigger_route_id") or "").strip()
    if not trigger_route:
        for item in list(lane.get("route_groups") or []):
            if isinstance(item, Mapping) and str(item.get("selection_group") or "") == "trigger-entry":
                trigger_route = str(item.get("primary_route_id") or "").strip()
                break
    if trigger_route == "portal-shortcuts-route":
        return "desktop-autostart"
    if trigger_route == "native-trigger-route":
        return "wm-bundle"
    if trigger_route in {"remapper-route", "helper-input-route"}:
        return "remapper-service"
    return "launcher-fallback"


def build_target_fit_contract_from_lane(
    lane: Mapping[str, Any] | None,
    *,
    host_truth: Mapping[str, Any] | None = None,
    host_requirements: list[dict[str, Any]] | None = None,
    portal_route_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    lane = lane or {}
    host_truth = host_truth or {}
    portal_route_contract = portal_route_contract or {}
    expectations = [dict(item) for item in list(lane.get("requirement_expectations") or []) if isinstance(item, Mapping)]
    observed_by_id = {
        str(item.get("id") or ""): dict(item)
        for item in list(host_requirements or [])
        if isinstance(item, Mapping) and str(item.get("id") or "")
    }
    comparisons: list[dict[str, Any]] = []
    aligned_ids: list[str] = []
    drift_ids: list[str] = []
    degraded_ids: list[str] = []
    ahead_ids: list[str] = []
    outside_profile_ids: list[str] = []
    unknown_ids: list[str] = []
    for item in expectations:
        requirement_id = str(item.get("id") or "").strip()
        if not requirement_id:
            continue
        observed = observed_by_id.get(requirement_id, {})
        expected_status = _normalized_status(item.get("expected_status") or item.get("status"))
        observed_status = _normalized_status(observed.get("observed_status") or observed.get("status"))
        fit_status, note = _compare_expectation(expected_status, observed_status)
        row = {
            "id": requirement_id,
            "title": str(item.get("title") or observed.get("title") or requirement_id),
            "priority": str(item.get("priority") or observed.get("priority") or "conditional"),
            "requirement_type": str(item.get("requirement_type") or observed.get("requirement_type") or ""),
            "expected_status": expected_status,
            "observed_status": observed_status,
            "fit_status": fit_status,
            "observed_note": str(observed.get("observed_note") or observed.get("why") or observed.get("title") or ""),
            "note": note,
        }
        comparisons.append(row)
        if fit_status == "aligned":
            aligned_ids.append(requirement_id)
        elif fit_status == "drifted":
            drift_ids.append(requirement_id)
        elif fit_status in {"degraded", "planned_gap"}:
            degraded_ids.append(requirement_id)
        elif fit_status == "ahead":
            ahead_ids.append(requirement_id)
        elif fit_status == "outside_profile":
            outside_profile_ids.append(requirement_id)
        else:
            unknown_ids.append(requirement_id)

    current_desktop = str(portal_route_contract.get("xdg_current_desktop") or "").strip() or None
    desktop_status, desktop_note = match_desktop_family(str(lane.get("desktop_family") or ""), current_desktop)
    trigger_route_id = str(lane.get("trigger_route_id") or "").strip()
    if not trigger_route_id:
        for item in list(lane.get("route_groups") or []):
            if isinstance(item, Mapping) and str(item.get("selection_group") or "") == "trigger-entry":
                trigger_route_id = str(item.get("primary_route_id") or "").strip()
                break
    notes: list[str] = []
    if trigger_route_id == "portal-shortcuts-route":
        interfaces = [dict(item) for item in list(portal_route_contract.get("interfaces") or []) if isinstance(item, Mapping)]
        gs = next((item for item in interfaces if str(item.get("short_name") or "") == "GlobalShortcuts"), {})
        if gs:
            notes.append(f"GlobalShortcuts live status is `{gs.get('live_status') or 'unknown'}` on this host.")
        notes.append("This target lane assumes a portal-session trigger path, so configured/live portal drift matters more than on remapper- or WM-first lanes.")
    elif trigger_route_id in {"remapper-route", "helper-input-route"}:
        notes.append("This target lane assumes a helper/remapper trigger edge, so uinput policy and helper-service ownership matter more than portal shortcut health.")
    elif trigger_route_id == "native-trigger-route":
        notes.append("This target lane assumes a desktop-native binding edge, so desktop-family fit and launcher fallback honesty matter more than portal shortcut health.")

    if desktop_status == "mismatch":
        notes.append(desktop_note)
    elif desktop_status == "match":
        notes.append(desktop_note)

    overall = "aligned"
    if drift_ids or desktop_status == "mismatch":
        overall = "drifted"
    elif degraded_ids or unknown_ids or desktop_status == "unknown":
        overall = "degraded"
    if not expectations and not current_desktop and not host_truth:
        overall = "unknown"

    return {
        "status": overall,
        "profile_id": str(lane.get("profile_id") or ""),
        "profile_title": str(lane.get("title") or lane.get("profile_id") or "target"),
        "release_level": str(lane.get("release_level") or ""),
        "backend": str(lane.get("backend") or ""),
        "desktop_family": str(lane.get("desktop_family") or ""),
        "deploy_style": _infer_deploy_style(lane),
        "trigger_route_id": trigger_route_id,
        "desktop_match": {
            "status": desktop_status,
            "current_desktop": current_desktop,
            "note": desktop_note,
        },
        "host_truth_status": str(host_truth.get("status") or host_truth.get("overall_status") or "unknown"),
        "expectation_count": len(comparisons),
        "aligned_requirement_ids": aligned_ids,
        "drift_requirement_ids": drift_ids,
        "degraded_requirement_ids": degraded_ids,
        "ahead_requirement_ids": ahead_ids,
        "outside_profile_requirement_ids": outside_profile_ids,
        "unknown_requirement_ids": unknown_ids,
        "comparisons": comparisons,
        "notes": _dedupe_keep_order(notes),
    }


def select_target_lane(
    project_dir: Path,
    *,
    bundle_target_profile: str | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    plan = build_release_lane_plan(
        project_dir,
        target_profiles=[bundle_target_profile] if bundle_target_profile else None,
        capability_usage=capability_usage,
    )
    lanes = [dict(item) for item in list(plan.get("release_lanes") or []) if isinstance(item, Mapping)]
    if not lanes:
        return {}
    if bundle_target_profile:
        wanted = str(bundle_target_profile or "").strip()
        match = next((dict(item) for item in lanes if str(item.get("profile_id") or "") == wanted), {})
        return match or dict(lanes[0])
    return dict(lanes[0])

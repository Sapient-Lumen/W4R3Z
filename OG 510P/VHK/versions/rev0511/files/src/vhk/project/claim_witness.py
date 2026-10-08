from __future__ import annotations

from typing import Any, Mapping

_WLROOTS_DESKTOPS = {"sway", "hyprland", "river", "wayfire", "phosh", "labwc", "niri"}

_CLAIM_HOST_PROFILES: dict[str, dict[str, str]] = {
    "gnome-wayland": {"desktop_family": "gnome", "route_bias": "portal-first", "backend": "wayland"},
    "kde-wayland": {"desktop_family": "kde", "route_bias": "portal-first", "backend": "wayland"},
    "hyprland-conservative": {"desktop_family": "hyprland", "route_bias": "remapper-first", "backend": "wayland"},
    "wlroots-sway-conservative": {"desktop_family": "wlroots", "route_bias": "remapper-first", "backend": "wayland"},
    "x11-i3": {"desktop_family": "i3", "route_bias": "native-first", "backend": "x11"},
    "portable-text": {"desktop_family": "", "route_bias": "portable", "backend": "cross-session"},
}


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def match_claim_desktop_family(desktop_family: str, current_desktop: str | None) -> tuple[str, str]:
    family = str(desktop_family or "").strip().lower()
    current = str(current_desktop or "").strip().lower()
    if not family:
        return "unknown", "Target claim does not name one desktop family."
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
    if family in token_set:
        return "match", f"Current desktop tokens include `{family}`."
    return "mismatch", f"Current desktop `{current}` does not match target family `{family}`."


def recommended_claim_level(item: Mapping[str, Any]) -> str:
    score = int(item.get("score") or 0)
    blocker_count = len([str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)])
    fit = str(item.get("fit") or "unknown").strip().lower()
    if fit in {"poor", "missing"} or score < 68:
        return "unsupported"
    if score >= 84 and blocker_count == 0:
        return "reference"
    if score >= 80 and blocker_count <= 1:
        return "supported"
    if score >= 74 and blocker_count <= 2:
        return "caveated"
    return "experimental"


def claim_host_fit_for_target(
    target: str,
    *,
    title: str,
    host_summary: Mapping[str, Any] | None = None,
    portal_route_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    host_summary = host_summary or {}
    portal_route_contract = portal_route_contract or {}
    if not host_summary and not portal_route_contract:
        return {}
    profile = dict(_CLAIM_HOST_PROFILES.get(target) or {})
    host_status = str(host_summary.get("overall_status") or host_summary.get("status") or "unknown")
    portal_status = str(portal_route_contract.get("status") or "unknown")
    current_desktop = str(portal_route_contract.get("xdg_current_desktop") or "").strip() or None
    notes: list[str] = []
    if target == "portable-text":
        notes.append("Portable text baseline is intentionally not bound to one desktop family.")
        if host_status == "blocked":
            notes.append("Current host still has blocked requirements, so treat it as partial proof only.")
            status = "degraded"
        elif host_status in {"ready", "degraded"}:
            status = "neutral"
        else:
            status = "unknown"
        return {
            "status": status,
            "title": title,
            "target": target,
            "desktop_family": "portable",
            "route_bias": "portable",
            "current_desktop": current_desktop,
            "desktop_match_status": "neutral",
            "host_truth_status": host_status,
            "portal_route_status": portal_status,
            "notes": notes,
        }
    if not profile:
        return {
            "status": "unknown",
            "title": title,
            "target": target,
            "desktop_family": "",
            "route_bias": "",
            "current_desktop": current_desktop,
            "desktop_match_status": "unknown",
            "host_truth_status": host_status,
            "portal_route_status": portal_status,
            "notes": ["No current-host review profile is modeled for this claim target yet."],
        }
    desktop_status, desktop_note = match_claim_desktop_family(str(profile.get("desktop_family") or ""), current_desktop)
    if desktop_note:
        notes.append(desktop_note)
    route_bias = str(profile.get("route_bias") or "")
    if route_bias == "portal-first":
        notes.append("This claim leans on portal-first trigger/injection posture, so portal routing health matters to the evidence story.")
    elif route_bias == "remapper-first":
        notes.append("This claim leans on compositor/remapper posture more than portal shortcut availability.")
    elif route_bias == "native-first":
        notes.append("This claim leans on desktop-native trigger ownership more than portal routing.")
    status = "aligned"
    if desktop_status == "mismatch":
        status = "drifted"
    elif desktop_status == "unknown":
        status = "unknown"
    elif route_bias == "portal-first" and portal_status in {"blocked", "degraded"}:
        status = "degraded"
    elif host_status == "blocked":
        status = "degraded"
    elif host_status == "unknown":
        status = "unknown"
    if status == "degraded" and host_status == "blocked":
        notes.append("Current host still has blocked requirements for this project shape.")
    if status == "degraded" and route_bias == "portal-first" and portal_status in {"blocked", "degraded"}:
        notes.append("Current portal route truth is not strong enough to treat this machine as clean reference proof.")
    return {
        "status": status,
        "title": title,
        "target": target,
        "desktop_family": str(profile.get("desktop_family") or ""),
        "route_bias": route_bias,
        "current_desktop": current_desktop,
        "desktop_match_status": desktop_status,
        "host_truth_status": host_status,
        "portal_route_status": portal_status,
        "notes": dedupe_keep_order(notes),
    }


def claim_host_review_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str((item.get("current_host_fit") or {}).get("status") or "") for item in rows if isinstance(item, dict)]
    return {
        "claims_with_current_host_review": sum(1 for item in rows if dict(item.get("current_host_fit") or {})),
        "aligned_count": sum(1 for status in statuses if status == "aligned"),
        "degraded_count": sum(1 for status in statuses if status == "degraded"),
        "drifted_count": sum(1 for status in statuses if status == "drifted"),
        "neutral_count": sum(1 for status in statuses if status == "neutral"),
        "unknown_count": sum(1 for status in statuses if status == "unknown"),
    }


def claim_host_witness_contract(
    rows: list[dict[str, Any]],
    *,
    portal_route_contract: Mapping[str, Any] | None = None,
    host_truth: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    summary = claim_host_review_summary(rows)
    reviewed = int(summary.get("claims_with_current_host_review") or 0)
    if reviewed <= 0:
        return {}
    status = "aligned"
    if int(summary.get("drifted_count") or 0) > 0:
        status = "drifted"
    elif int(summary.get("degraded_count") or 0) > 0:
        status = "degraded"
    elif int(summary.get("unknown_count") or 0) > 0 and int(summary.get("aligned_count") or 0) == 0:
        status = "unknown"
    elif int(summary.get("neutral_count") or 0) > 0 and int(summary.get("aligned_count") or 0) == 0:
        status = "neutral"
    notes: list[str] = []
    if status == "drifted":
        notes.append("At least one strong target claim is being reviewed from a host that drifts from that lane.")
    elif status == "degraded":
        notes.append("Current host only partially matches at least one recommended target lane.")
    elif status == "aligned":
        notes.append("Current host lines up with the reviewed target-claim profiles the planner can model.")
    elif status == "neutral":
        notes.append("Current host is useful for portable-baseline evidence, but not for every desktop-specific claim.")
    else:
        notes.append("Current host evidence is too incomplete to confirm the reviewed target-claim lanes.")
    current_desktop = str((portal_route_contract or {}).get("xdg_current_desktop") or "").strip() or None
    if current_desktop:
        notes.append(f"Current desktop tokens: `{current_desktop}`.")
    host_status = str((host_truth or {}).get("overall_status") or (host_truth or {}).get("status") or "unknown")
    if host_status != "unknown":
        notes.append(f"Host truth currently reads `{host_status}`.")
    return {
        "status": status,
        "reviewed_claim_count": reviewed,
        "current_desktop": current_desktop,
        "host_truth_status": host_status,
        **summary,
        "notes": dedupe_keep_order(notes),
    }
